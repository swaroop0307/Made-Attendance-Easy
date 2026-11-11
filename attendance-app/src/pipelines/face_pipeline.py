"""
Face recognition pipeline using DeepFace (pure-Python, no dlib/cmake needed).
Public API is identical to the old dlib-based pipeline so no other files change.
"""

import os
import numpy as np
import streamlit as st

from src.database.db import get_all_students


# ── Model config ──────────────────────────────────────────────────────────────
_MODEL_NAME = "Facenet"          # 128-d embeddings, fast & accurate
_DETECTOR   = "opencv"           # pure-Python OpenCV detector, no cmake
_THRESHOLD  = 0.45               # cosine distance threshold (tuned for classroom lighting & angles)


@st.cache_resource(show_spinner=False)
def _load_deepface():
    """Warm up DeepFace (downloads weights once, then cached)."""
    from deepface import DeepFace
    # Run a tiny dummy call to trigger model download on cold-start
    import numpy as _np
    dummy = _np.zeros((100, 100, 3), dtype=_np.uint8)
    try:
        DeepFace.represent(dummy, model_name=_MODEL_NAME,
                           detector_backend=_DETECTOR, enforce_detection=False)
    except Exception:
        pass
    return DeepFace


def get_face_embeddings(image_np: np.ndarray) -> list:
    """
    Return a list of 128-d numpy arrays, one per detected face.
    Handles single portraits as well as multiple faces in classroom photos.
    """
    DeepFace = _load_deepface()
    embeddings = []

    # Ensure 3-channel RGB image
    if len(image_np.shape) == 2:
        image_np = np.stack((image_np,) * 3, axis=-1)
    elif image_np.shape[2] == 4:
        image_np = image_np[:, :, :3]

    h, w = image_np.shape[:2]

    # Primary pass: DeepFace represent with OpenCV detector
    try:
        results = DeepFace.represent(
            image_np,
            model_name=_MODEL_NAME,
            detector_backend=_DETECTOR,
            enforce_detection=False,
        )
        for r in results:
            area = r.get("facial_area", {})
            conf = r.get("face_confidence", 1.0)
            # If no face is found and enforce_detection=False, DeepFace falls back to whole image
            if conf == 0 and area.get("x") == 0 and area.get("y") == 0 and area.get("w") == w and area.get("h") == h:
                continue
            emb = np.array(r["embedding"])
            if np.linalg.norm(emb) > 1e-3:
                embeddings.append(emb)
    except Exception:
        pass

    # Fallback pass: DeepFace's OpenCV detector uses minNeighbors=10 which can drop
    # smaller/angled faces in classroom group photos. If 1 or fewer faces were found,
    # run OpenCV Haar cascade directly with tuned minNeighbors=4 to catch all students.
    if len(embeddings) <= 1:
        try:
            import cv2
            cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            if os.path.isfile(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                detected_boxes = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=4,
                    minSize=(30, 30),
                )
                if len(detected_boxes) > len(embeddings):
                    alt_embeddings = []
                    for (x, y, fw, fh) in detected_boxes:
                        pad_x = int(fw * 0.15)
                        pad_y = int(fh * 0.15)
                        x1 = max(0, x - pad_x)
                        y1 = max(0, y - pad_y)
                        x2 = min(w, x + fw + pad_x)
                        y2 = min(h, y + fh + pad_y)

                        face_crop = image_np[y1:y2, x1:x2]
                        if face_crop.shape[0] < 20 or face_crop.shape[1] < 20:
                            continue

                        crop_res = DeepFace.represent(
                            face_crop,
                            model_name=_MODEL_NAME,
                            detector_backend="skip",
                            enforce_detection=False,
                        )
                        if crop_res:
                            crop_emb = np.array(crop_res[0]["embedding"])
                            if np.linalg.norm(crop_emb) > 1e-3:
                                alt_embeddings.append(crop_emb)

                    if len(alt_embeddings) > len(embeddings):
                        embeddings = alt_embeddings
        except Exception:
            pass

    return embeddings


@st.cache_resource(show_spinner=False)
def get_trained_model():
    """
    Build an SVC classifier from all student face embeddings stored in DB.
    Returns None (no students), 0 (no embeddings), or dict with clf/X/y.
    """
    from sklearn.svm import SVC

    student_db = get_all_students()
    if not student_db:
        return None

    X, y = [], []
    for student in student_db:
        embedding = student.get("face_embedding")
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get("student_id"))

    if len(X) == 0:
        return 0

    clf = SVC(kernel="linear", probability=True, class_weight="balanced")
    try:
        clf.fit(X, y)
    except ValueError:
        pass

    return {"clf": clf, "X": X, "y": y}


def train_classifier():
    """Invalidate the cache and retrain after a new student registers."""
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np: np.ndarray):
    """
    Detect all faces in a classroom photo and match them against enrolled students.

    Returns:
        detected_student  – dict {student_id: True} for matched students
        all_students      – sorted list of all known student IDs
        num_faces         – number of faces detected in the image
    """
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = get_trained_model()
    if not model_data or not isinstance(model_data, dict) or not model_data.get("X"):
        return detected_student, [], len(encodings)

    X_train   = model_data["X"]
    y_train   = model_data["y"]
    all_students = sorted(list(set(y_train)))

    if not encodings:
        return detected_student, all_students, 0

    # Match each detected face against all enrolled students via minimum cosine distance
    for encoding in encodings:
        norm_enc = encoding / (np.linalg.norm(encoding) + 1e-9)
        best_student_id = None
        min_cosine_dist = float("inf")

        for train_emb, student_id in zip(X_train, y_train):
            norm_train = train_emb / (np.linalg.norm(train_emb) + 1e-9)
            cosine_dist = 1.0 - float(np.dot(norm_enc, norm_train))

            if cosine_dist < min_cosine_dist:
                min_cosine_dist = cosine_dist
                best_student_id = student_id

        # Verify best match is within the acceptable threshold
        if min_cosine_dist <= _THRESHOLD and best_student_id is not None:
            detected_student[int(best_student_id)] = True

    return detected_student, all_students, len(encodings)
