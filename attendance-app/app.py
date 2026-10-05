
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon='🎓'
    )

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    # Capture join-code from URL and persist in session_state so it survives reruns
    url_join_code = st.query_params.get('join-code')
    if url_join_code:
        st.session_state['pending_join_code'] = url_join_code
        # Force student login flow if not already there
        if st.session_state['login_type'] != 'student':
            st.session_state['login_type'] = 'student'
            st.rerun()

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()

main()