import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at 20% 20%, #4338ca 0%, #1e1b4b 60%, #0f172a 100%) !important;
                color: #f8fafc !important;
            }

            /* Portal Selection Cards */
            .stApp div[data-testid="stColumn"] {
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                padding: 2.2rem 2rem !important;
                border-radius: 1.75rem !important;
                box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5) !important;
                transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                text-align: center !important;
            }

            .stApp div[data-testid="stColumn"]:hover {
                transform: translateY(-5px) !important;
                border-color: rgba(165, 180, 252, 0.5) !important;
                box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.35) !important;
            }

            .stApp div[data-testid="stColumn"] img {
                margin: 1rem auto !important;
                filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.35));
                transition: transform 0.3s ease;
            }

            .stApp div[data-testid="stColumn"]:hover img {
                transform: scale(1.05);
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f1f5f9 100%) !important;
                color: #0f172a !important;
            }

            /* Dashboard Cards / Containers */
            div[data-testid="stMetric"], div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.9) !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 1.25rem !important;
                padding: 1.25rem !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

            /* Hide streamlit standard chrome */
            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 3rem !important;
                max-width: 1020px !important;
            }

            html, body, p, label, input, textarea, select, option, .stMarkdown, .stText {
                font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
                letter-spacing: -0.01em;
            }

            [data-testid="stIconMaterial"], [data-testid="stIcon"], .material-symbols-rounded, .material-symbols-outlined, .material-symbols-sharp {
                font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
            }

            h1, h2, h3 {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                letter-spacing: -0.025em !important;
            }

            h1 {
                font-size: 2.75rem !important;
                line-height: 1.5 !important;
                margin-bottom: 1.5rem !important;
            }

            h2 {
                font-size: 1.75rem !important;
                line-height: 1.5 !important;
                margin-bottom: 1rem !important;
            }

            /* Modern pill & glow buttons (scoped specifically to st.button) */
            div.stButton > button {
                font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
                border-radius: 9999px !important;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                padding: 0.65rem 1.6rem !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            div.stButton > button[kind="secondary"] {
                border-radius: 9999px !important;
                background: linear-gradient(135deg, #ec4899 0%, #db2777 100%) !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                padding: 0.65rem 1.6rem !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(219, 39, 119, 0.3) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            div.stButton > button[kind="tertiary"] {
                border-radius: 9999px !important;
                background: #0f172a !important;
                color: #f8fafc !important;
                font-weight: 600 !important;
                padding: 0.65rem 1.6rem !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            div.stButton > button:hover {
                transform: translateY(-2px) scale(1.02) !important;
                filter: brightness(1.08) !important;
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.45) !important;
            }

            div.stButton > button:active {
                transform: translateY(0) scale(0.98) !important;
            }

            /* Inputs & Textareas */
            input, textarea, [data-baseweb="input"] {
                border-radius: 0.85rem !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
            }

            input:focus, textarea:focus {
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
            }

            /* Tab navigation */
            button[data-baseweb="tab"] {
                border-radius: 0.75rem 0.75rem 0 0 !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)