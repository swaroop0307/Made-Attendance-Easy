import streamlit as st


def header_home():
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:2.5rem; margin-top:1.5rem">
            <h1 style='text-align:center; color:#ffffff; font-size: 2.75rem; letter-spacing: -0.03em; margin: 0; font-weight: 800;'>
                SNAP<span style="background: linear-gradient(135deg, #a5b4fc, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CLASS</span>
            </h1>
            <p style='text-align:center; color:#cbd5e1; font-size: 1.05rem; margin-top: 0.5rem; max-width: 420px;'>
                AI-powered facial & voice biometric attendance system
            </p>
        </div>   
    """, unsafe_allow_html=True)


def header_dashboard():
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; padding: 0.5rem 0 1rem 0;">
            <div>
                <h2 style='text-align:left; color:#1e1b4b; font-size: 1.65rem; margin:0; font-weight:800; letter-spacing: -0.02em;'>
                    SNAP<span style="color:#6366f1;">CLASS</span>
                </h2>
                <span style="font-size: 0.78rem; font-weight:600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">
                    Attendance Portal
                </span>
            </div>
        </div>   
    """, unsafe_allow_html=True)
