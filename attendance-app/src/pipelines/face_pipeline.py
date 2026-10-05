"""
Face recognition pipeline using DeepFace (pure-Python, no dlib/cmake needed).
Public API is identical to the old dlib-based pipeline so no other files change.
"""

import numpy as np
import streamlit as st

from src.database.db import get_all_students


# ── Model config ──────────────────────────────────────────────────────────────
_MODEL_NAME = "Facenet"          # 128-d embeddings, fast & accurate
_DETECTOR   = "opencv"           # pure-Python OpenCV detector, no cmake
_THRESHOLD  = 0.40               # cosine distance threshold (lower = stricter)


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
    Compatible with the old dlib-based signature.
    """
    DeepFace = _load_deepface()
    try:
        results = DeepFace.represent(
            image_np,
            model_name=_MODEL_NAME,
            detector_backend=_DETECTOR,
            enforce_detection=False,
        )
        embeddings = []
        for r in results:
            emb = np.array(r["embedding"])
            # Skip near-zero embeddings produced when no face is found
            if np.linalg.norm(emb) > 1e-3:
                embeddings.append(emb)
        return embeddings
    except Exception:
        return []


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
    if not model_data:
        return detected_student, [], len(encodings)

    clf       = model_data["clf"]
    X_train   = model_data["X"]
    y_train   = model_data["y"]
    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        # Verify with cosine distance against the stored embedding
        student_embedding = np.array(X_train[y_train.index(predicted_id)])
        norm_enc   = encoding / (np.linalg.norm(encoding) + 1e-9)
        norm_train = student_embedding / (np.linalg.norm(student_embedding) + 1e-9)
        cosine_dist = 1.0 - float(np.dot(norm_enc, norm_train))

        if cosine_dist <= _THRESHOLD:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)
