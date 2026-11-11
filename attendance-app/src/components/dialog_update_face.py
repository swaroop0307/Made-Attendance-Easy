import streamlit as st
import numpy as np
from PIL import Image
import time

from src.database.db import update_student_face_embedding


@st.dialog("Update Face Photo (FaceID)")
def update_face_dialog(student_id: int):
    st.write(
        "Capture or upload a new photo to update your FaceID biometric profile. "
        "Use this if you have changed your hairstyle, grown a beard, started wearing glasses, "
        "or are experiencing trouble with face login."
    )
    st.info("💡 **Tips for best results:** Look directly at the camera, ensure good frontal lighting, and make sure only your face is in the frame.")

    source_type = st.radio(
        "Select photo source:",
        options=["📷 Camera", "📁 Upload Photo"],
        horizontal=True,
        key="update_face_source_type",
        label_visibility="collapsed"
    )

    photo_source = None
    if source_type == "📷 Camera":
        photo_source = st.camera_input("Take a photo to update FaceID", key="update_face_cam")
    else:
        photo_source = st.file_uploader(
            "Upload a clear photo of your face (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            key="update_face_upload"
        )
        if photo_source:
            st.image(photo_source, caption="Uploaded Photo Preview", width=250)

    if photo_source:
        try:
            from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
        except Exception as e:
            st.error(f"Face recognition model failed to load: {e}")
            return

        img = np.array(Image.open(photo_source).convert("RGB"))
        with st.spinner("Analyzing facial features..."):
            encodings = get_face_embeddings(img)

        if not encodings:
            st.error("No face detected! Please ensure your face is clearly visible and well-lit, then try again.")
        elif len(encodings) > 1:
            st.error("Multiple faces detected! Please ensure only your face is visible in the frame.")
        else:
            st.success("Face clearly detected! Ready to update.")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Cancel", type="tertiary", width="stretch"):
                    st.rerun()
            with c2:
                if st.button("Save New FaceID", type="primary", width="stretch"):
                    with st.spinner("Saving new face embedding & retraining model..."):
                        face_emb = encodings[0].tolist()
                        update_student_face_embedding(student_id, face_emb)

                        if "student_data" in st.session_state and isinstance(st.session_state.student_data, dict):
                            st.session_state.student_data["face_embedding"] = face_emb

                        train_classifier()
                        st.toast("FaceID updated and retrained successfully! 🎉")
                        time.sleep(1.2)
                        st.rerun()

