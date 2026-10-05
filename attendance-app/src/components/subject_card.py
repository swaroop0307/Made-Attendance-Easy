import streamlit as st
import textwrap


def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f'<div style="background:#ffffff;border-radius:1.25rem;padding:1.5rem;border:1px solid #e2e8f0;box-shadow:0 10px 25px -5px rgba(0,0,0,0.04);margin-bottom:1.25rem;position:relative;overflow:hidden;transition:transform 0.2s ease,box-shadow 0.2s ease;">'
    html += '<div style="position:absolute;left:0;top:0;bottom:0;width:6px;background:linear-gradient(180deg,#6366f1,#ec4899);"></div>'
    html += f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:0.75rem;">'
    html += f'<h3 style="margin:0;color:#0f172a;font-size:1.35rem;font-weight:700;letter-spacing:-0.02em;">{name}</h3>'
    html += f'<span style="background:#eef2ff;color:#4f46e5;font-size:0.82rem;font-weight:700;padding:4px 10px;border-radius:9999px;border:1px solid #c7d2fe;">{code}</span>'
    html += '</div>'
    html += f'<p style="color:#64748b;font-size:0.92rem;margin:0 0 1rem 0;">Section: <b style="color:#334155;">{section}</b></p>'

    if stats:
        html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:0.75rem;">'
        for icon, label, value in stats:
            html += f'<div style="background:#f8fafc;border:1px solid #e2e8f0;padding:6px 12px;border-radius:9999px;font-size:0.85rem;color:#475569;display:inline-flex;align-items:center;gap:6px;"><span>{icon}</span> <strong style="color:#0f172a;">{value}</strong> <span>{label}</span></div>'
        html += '</div>'

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
