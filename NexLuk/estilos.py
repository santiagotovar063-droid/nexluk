import streamlit as st


def aplicar_estilos():
    try:
        st.set_page_config(
            page_title="NexLuk | Core System",
            page_icon="N",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception:
        pass

    st.markdown(
        """
        <style>
        /* Fondo general y tipografia */
        .stApp {
            background-color: #0b1120;
            color: #e2e8f0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        /* Encabezados */
        h1, h2, h3 {
            color: #f8fafc !important;
            font-weight: 600;
            letter-spacing: 0.2px;
        }

        /* Banner principal */
        .nl-hero {
            background: #111827;
            border: 1px solid #1e293b;
            border-left: 4px solid #2563eb;
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .nl-hero-title {
            color: #f8fafc;
            font-size: 1.45rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.3px;
        }
        .nl-hero-sub {
            color: #94a3b8;
            font-size: 0.88rem;
            margin: 4px 0 0 0;
        }
        .nl-status-pill {
            background: rgba(16, 185, 129, 0.12);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }

        /* Titulos de seccion */
        .nl-panel-header {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.1px;
            margin: 18px 0 10px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid #1e293b;
        }

        /* Tarjetas de metricas nativas */
        div[data-testid="stMetric"] {
            background-color: #111827;
            border: 1px solid #1e293b;
            border-top: 3px solid #2563eb;
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
        }

        /* Tarjeta de modo expediente */
        .expediente-card {
            background: #111827;
            border: 1px solid #1e293b;
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 16px 18px;
            margin: 12px 0;
        }
        .expediente-card h3 {
            color: #60a5fa !important;
            font-size: 1.05rem;
            margin: 0 0 4px 0;
        }
        .expediente-card p {
            color: #cbd5e1;
            font-size: 0.88rem;
            margin: 0;
        }

        /* Contenedor de reporte detallado */
        .nl-report-box {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 20px 24px;
            margin-top: 12px;
            line-height: 1.65;
            color: #e2e8f0;
        }

        /* Expander corporativo */
        div[data-testid="stExpander"] {
            background-color: #111827;
            border: 1px solid #1e293b;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        /* Inputs y chat */
        .stTextInput input,
        .stChatInput textarea {
            border-radius: 8px !important;
            border: 1px solid #1e293b !important;
            background-color: #111827 !important;
            color: #f8fafc !important;
        }
        .stTextInput input:focus,
        .stChatInput textarea:focus {
            border-color: #2563eb !important;
        }

        /* Mensajes de chat */
        div[data-testid="stChatMessage"] {
            background-color: #111827;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }

        /* Alertas */
        .stAlert {
            border-radius: 8px;
            border: 1px solid #1e293b;
        }
        </style>
        """,
        unsafe_allow_html=True
    )