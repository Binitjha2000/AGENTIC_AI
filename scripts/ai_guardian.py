import cv2
import mediapipe as mp
import numpy as np
import os

# Initialize MediaPipe face detection and face mesh
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.2)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.2, min_tracking_confidence=0.2)

# Load multiple reference images and extract facial landmarks
reference_images = ["me7.jpg", "me2.jpg", "me3.jpg", "me4.jpg", "me5.jpg", "me6.jpg", "me.jpg"]  # List of your reference images
reference_landmarks = []

# Load and process reference images
for img_path in reference_images:
    reference_image = cv2.imread(img_path)
    if reference_image is None:
        print(f"Error: Unable to load image {img_path}!")
        continue
    reference_rgb = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)
    reference_results = face_mesh.process(reference_rgb)
    if reference_results.multi_face_landmarks:
        reference_landmarks.append(reference_results.multi_face_landmarks[0])
    else:
        print(f"Error: No faces detected in {img_path}")

# Function to compute Euclidean distance between landmarks (more precise by comparing eye and nose regions)
def calculate_landmark_distance(landmarks1, landmarks2):
    distance = 0
    selected_landmarks = [33, 263, 61, 291, 1]  # Selected landmarks: eyes, nose, chin (adjust for precision)
    for lm1, lm2 in zip(selected_landmarks, selected_landmarks):
        distance += np.linalg.norm(np.array([landmarks1[lm1].x, landmarks1[lm1].y]) - np.array([landmarks2[lm2].x, landmarks2[lm2].y]))
    return distance

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret:
        break
    
    # Convert image to RGB (MediaPipe uses RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    results = face_detector.process(frame_rgb)
    
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Detect facial landmarks in the current frame
            frame_results = face_mesh.process(frame_rgb)
            if frame_results.multi_face_landmarks:
                frame_landmarks = frame_results.multi_face_landmarks[0]
                
                # Compare the detected landmarks with each reference image's landmarks
                match_found = False
                for reference in reference_landmarks:
                    distance = calculate_landmark_distance(reference.landmark, frame_landmarks.landmark)
                    print(f"Distance: {distance}")  # Log for debugging
                    
                    # Define a threshold distance for match (adjustable value)
                    if distance < 1.0:  # Threshold for a match (fine-tune this)
                        match_found = True
                        break  # If any reference image matches, exit the loop
                
                if match_found:
                    color = (0, 255, 0)  # Match (Green)
                else:
                    color = (0, 0, 255)  # Mismatch (Red)
                    os.system("rundll32.exe user32.dll,LockWorkStation")  # Lock the system
                    print("No match found. System locked.")
                
                # Optionally, draw the landmarks on the frame
                mp_drawing.draw_landmarks(frame, frame_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

    cv2.imshow('Face Detection with MediaPipe', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
