import cv2
import torch
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('best.pt')  # You can use 'yolov8s.pt', 'yolov8m.pt', etc., for larger models

# Function to draw bounding boxes and labels
def draw_boxes(frame, results):
    for result in results:
        boxes = result.boxes  # Get the bounding boxes
        for box in boxes:
            # Extract bounding box coordinates and class information
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Convert to int
            confidence = box.conf[0]  # Confidence score
            class_id = int(box.cls[0])  # Class ID
            class_name = model.names[class_id]  # Class name from the model's class names list

            # Draw the bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name} ({confidence:.2f})"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Access the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Starting webcam... Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Run YOLOv8 model inference
    results = model(frame)

    # Draw the bounding boxes on the frame
    draw_boxes(frame, results)

    # Display the output frame
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
