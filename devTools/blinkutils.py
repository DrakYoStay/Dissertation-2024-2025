import mediapipe as mp
import cv2
import numpy as np

def eye_aspect_ratio(landmarks, eye_indices):
    p1 = np.array(landmarks[eye_indices[0]])
    p2 = np.array(landmarks[eye_indices[1]])
    p3 = np.array(landmarks[eye_indices[2]])
    p4 = np.array(landmarks[eye_indices[3]])
    p5 = np.array(landmarks[eye_indices[4]])
    p6 = np.array(landmarks[eye_indices[5]])
    A = np.linalg.norm(p2 - p6)
    B = np.linalg.norm(p3 - p5)
    C = np.linalg.norm(p1 - p4)
    return (A + B) / (2.0 * C)

def detect_liveness_from_image(image_np):
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        if not results.multi_face_landmarks:
            return False

        face_landmarks = results.multi_face_landmarks[0]
        h, w, _ = image_np.shape
        landmarks = [(int(pt.x * w), int(pt.y * h)) for pt in face_landmarks.landmark]

        left_eye_indices = [33, 160, 158, 133, 153, 144]
        right_eye_indices = [362, 385, 387, 263, 373, 380]

        left_ear = eye_aspect_ratio(landmarks, left_eye_indices)
        right_ear = eye_aspect_ratio(landmarks, right_eye_indices)
        avg_ear = (left_ear + right_ear) / 2.0

        # Accept blink OR natural motion: relaxed EAR threshold
        if avg_ear < 0.22:
            return True  # blink detected

        # Head movement: check eyebrow–chin vertical distance
        top = landmarks[10]    # forehead
        bottom = landmarks[152]  # chin
        height = np.linalg.norm(np.array(top) - np.array(bottom))

        # If the face is tall enough in the frame, we accept it as motion
        if height > h * 0.25:
            return True

        return False
