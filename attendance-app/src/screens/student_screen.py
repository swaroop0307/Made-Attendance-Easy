import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    # Import lazy here — avoids crash on Streamlit Cloud cold start
    from src.components.dialog_auto_enroll import auto_enroll_dialog

    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']} 👋")
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.session_state.pop('pending_join_code', None)
            st.rerun()

    st.space()

    # If a join-code is pending, show the enrollment dialog right away
    pending_code = st.session_state.get('pending_join_code')
    if pending_code:
        auto_enroll_dialog(pending_code)
        return  # Dialog is showing; don't render dashboard below it yet

    c1, c2 = st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.info("You haven't enrolled in any subjects yet. Click 'Enroll in Subject' to get started!")
    else:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def unenroll_button(bound_student_id=student_id, bound_sid=sid, bound_name=sub['name']):
                if st.button("Unenroll from this course", type='tertiary', width='stretch', key=f"unenroll_{bound_sid}"):
                    unenroll_student_to_subject(bound_student_id, bound_sid)
                    st.toast(f'Unenrolled from {bound_name} successfully!')
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        ('📅', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended']),
                    ],
                    footer_callback=unenroll_button
                )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    # ── LOGIN / REGISTER SCREEN ──────────────────────────────────────────────
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.session_state.pop('pending_join_code', None)
            st.rerun()

    pending_code = st.session_state.get('pending_join_code')
    if pending_code:
        st.info(f"📎 You were invited to join a class! **Scan your face** to log in or register first, then you'll be auto-enrolled.")

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()

    show_registration = False
    photo_source = st.camera_input("Position your face in the center and take a photo")

    if photo_source:
        # Lazy import — dlib/face_recognition only loaded when actually needed
        try:
            from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
        except Exception as e:
            st.error(f"Face recognition model failed to load: {e}")
            st.stop()

        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning your face..'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('No face detected! Please make sure your face is clearly visible.')
            elif num_faces > 1:
                st.warning('Multiple faces detected! Please ensure only your face is in the frame.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome back, {student['name']}! 👋")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new student — register below.')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header('Register New Profile')
            st.markdown("Enter your name and take a photo to create your student account.")

            new_name = st.text_input("Your full name", placeholder='E.g. Priya Sharma')

            st.subheader('Optional: Voice Enrollment')
            st.info("Record a short phrase so teachers can also take voice-based attendance.")

            audio_data = None
            try:
                audio_data = st.audio_input('Say something like: "I am present, my name is Priya."')
            except Exception:
                st.warning('Audio input not available on this device.')

            if st.button('Create Account & Join', type='primary'):
                if new_name:
                    with st.spinner('Creating your profile...'):
                        try:
                            from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
                        except Exception as e:
                            st.error(f"Face model failed to load: {e}")
                            st.stop()

                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)

                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None

                            if audio_data:
                                try:
                                    from src.pipelines.voice_pipeline import get_voice_embedding
                                    voice_emb = get_voice_embedding(audio_data.read())
                                except Exception:
                                    pass  # Voice is optional, don't block registration

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile created! Welcome, {new_name}! 🎉')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Couldn't detect your face clearly. Please retake your photo in good lighting.")
                else:
                    st.warning('Please enter your name to continue.')

    footer_dashboard()