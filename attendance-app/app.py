
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog

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
            # After student_screen renders, show enrollment dialog if student is logged in
            if (
                st.session_state.get('is_logged_in')
                and st.session_state.get('user_role') == 'student'
                and st.session_state.get('pending_join_code')
            ):
                auto_enroll_dialog(st.session_state['pending_join_code'])

        case None:
            home_screen()

main()