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

@app.route('/verify-faces', methods=['POST'])
def verify_face():
    try:
        data = request.get_json()

        # Ambil gambar dari request dan hapus metadata jika ada
        image_data1 = data['image1']
        if ',' in image_data1:
            # Pisahkan metadata dari data gambar
            image_data1 = image_data1.split(',')[1]
        
        # Decode gambar dari Base64
        decoded_image1 = base64.b64decode(image_data1)

        # Load gambar menggunakan face_recognition
        image1 = face_recognition.load_image_file(BytesIO(decoded_image1))
        face_encodings1 = face_recognition.face_encodings(image1)

        if not face_encodings1:
            return jsonify({'match': False, 'user_id': None})

        face_encoding1 = face_encodings1[0]

        # Koneksi ke database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Query untuk mendapatkan semua wajah dari database
        query = "SELECT img, User_id FROM Face_Data"
        cursor.execute(query)

        match_found = False
        user_id = None

        # Iterasi untuk mencari kecocokan wajah
        for (face_data, db_user_id) in cursor.fetchall():
            if ',' in face_data:
                # Pisahkan metadata dari data gambar
                face_data = face_data.split(',')[1]
            
            decoded_db_image = base64.b64decode(face_data)

            # Load gambar dari database
            db_face_image = face_recognition.load_image_file(BytesIO(decoded_db_image))
            db_face_encoding = face_recognition.face_encodings(db_face_image)

            if db_face_encoding:
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
