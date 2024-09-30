from flask import Flask, request, jsonify
import base64
from io import BytesIO
import face_recognition
import mysql.connector
from PIL import Image

app = Flask(__name__)

# Configure your MySQL connection
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'cashier-ai'
}

@app.route('/is-face-valid', methods=['POST'])
def face_validation():
    try:
        data = request.get_json()

        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]  # Remove metadata
        
        decoded_image = base64.b64decode(image_data)

        # Load image using face_recognition (will use GPU with dlib[cuda])
        image = face_recognition.load_image_file(BytesIO(decoded_image))
        face_encodings = face_recognition.face_encodings(image)

        # Return true if a face is detected, false if not
        if face_encodings:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify-faces', methods=['POST'])
def verify_face():
    try:
        data = request.get_json()

        # Decode base64 image
        image_data1 = data['image1']
        if ',' in image_data1:
            image_data1 = image_data1.split(',')[1]  # Remove metadata
        
        decoded_image1 = base64.b64decode(image_data1)

        # Load image using face_recognition (will use GPU with dlib[cuda])
        image1 = face_recognition.load_image_file(BytesIO(decoded_image1))
        face_encodings1 = face_recognition.face_encodings(image1)

        if not face_encodings1:
            return jsonify({'match': False, 'user_id': None})

        face_encoding1 = face_encodings1[0]

        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Query all face images from database
        query = "SELECT img, User_id FROM Face_Data"
        cursor.execute(query)

        match_found = False
        user_id = None

        # Loop through faces from the database
        for (face_data, db_user_id) in cursor.fetchall():
            if ',' in face_data:
                face_data = face_data.split(',')[1]  # Remove metadata
            
            decoded_db_image = base64.b64decode(face_data)

            # Load image from database using face_recognition
            db_face_image = face_recognition.load_image_file(BytesIO(decoded_db_image))
            db_face_encoding = face_recognition.face_encodings(db_face_image)

            if db_face_encoding:
                # Compare faces using GPU-accelerated dlib
                match = face_recognition.compare_faces([face_encoding1], db_face_encoding[0], tolerance=0.4)
                if match[0]:
                    match_found = True
                    user_id = db_user_id
                    break

        cursor.close()
        connection.close()

        response = {'match': match_found, 'user_id': user_id}
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
