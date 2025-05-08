import mediapipe as mp
import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO

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

def detect_liveness_from_frames(frames):
    mp_face_mesh = mp.solutions.face_mesh
    ear_threshold = 0.23
    blink_detected = False
    face_positions = []
    ear_series = []

    left_eye_indices = [33, 160, 158, 133, 153, 144]
    right_eye_indices = [362, 385, 387, 263, 373, 380]

    with mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, max_num_faces=1) as face_mesh:
        for frame in frames:
            img_data = frame.split(',')[1]
            img = Image.open(BytesIO(base64.b64decode(img_data)))
            img_np = np.array(img)

            results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
            if not results.multi_face_landmarks:
                continue

            face_landmarks = results.multi_face_landmarks[0]
            h, w, _ = img_np.shape
            landmarks = [(int(pt.x * w), int(pt.y * h)) for pt in face_landmarks.landmark]

            left_ear = eye_aspect_ratio(landmarks, left_eye_indices)
            right_ear = eye_aspect_ratio(landmarks, right_eye_indices)
            avg_ear = (left_ear + right_ear) / 2.0
            ear_series.append(avg_ear)

            print(f"EAR: {avg_ear:.3f}")

            # Track face center (e.g., nose tip)
            face_positions.append(landmarks[1])

    # Blink detection: look for open -> closed -> open pattern
    for i in range(2, len(ear_series) - 2):
        if (
            ear_series[i - 2] > ear_threshold and
            ear_series[i] < ear_threshold and
            ear_series[i + 2] > ear_threshold
        ):
            blink_detected = True
            break

    # Movement detection: nose displacement between first and last frames
    if len(face_positions) >= 2:
        displacement = np.linalg.norm(np.array(face_positions[0]) - np.array(face_positions[-1]))
        moved = displacement > 5  # pixel threshold
        print(f"EAR: {moved:.3f}")
    else:
        moved = False

    return blink_detected and moved
