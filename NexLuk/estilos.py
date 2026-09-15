import streamlit as st

def aplicar_estilos():
    st.set_page_config(
        page_title="NexLuk | Core System",
        page_icon="N",
        layout="wide"
    )

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #090c10 0%, #161b22 100%);
        color: #e6edf3;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(13, 17, 23, 0.90) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid #1f6feb;
        box-shadow: 2px 0 15px rgba(31, 111, 235, 0.1);
    }

    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    div.stMetric {
        background: rgba(33, 38, 45, 0.65);
        backdrop-filter: blur(5px);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-top: 3px solid #1f6feb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    .stButton > button {
        background: linear-gradient(90deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 15px rgba(31, 111, 235, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #388bfd 0%, #58a6ff 100%);
        box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4);
        transform: scale(1.02);
    }

    .stAlert {
        border-radius: 8px;
        border: none;
    }

    .stTextInput input,
    .stChatInput textarea {
        border-radius: 8px;
        border: 1px solid #30363d;
        background-color: #0d1117;
        color: #c9d1d9;
    }

    .document-card {
        background: rgba(33, 38, 45, 0.65);
        border: 1px solid #30363d;
        border-left: 4px solid #1f6feb;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
    }

    .expediente-card {
        background: linear-gradient(
            135deg,
            rgba(31,111,235,0.15),
            rgba(88,166,255,0.05)
        );
        border: 1px solid #1f6feb;
        border-radius: 12px;
        padding: 18px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)