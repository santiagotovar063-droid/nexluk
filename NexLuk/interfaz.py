import os
import streamlit as st


def _formatear_tamano(num_bytes):
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def dibujar_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] {
                    background-color: #0b1120;
                    border-right: 1px solid #1e293b;
                }
                .nl-brand {
                    background: #111827;
                    border: 1px solid #1e293b;
                    border-left: 3px solid #2563eb;
                    border-radius: 8px;
                    padding: 12px 14px;
                    margin-bottom: 14px;
                }
                .nl-brand-title {
                    color: #f8fafc;
                    font-size: 1.15rem;
                    font-weight: 700;
                    letter-spacing: 0.4px;
                    margin: 0;
                    line-height: 1.2;
                }
                .nl-brand-sub {
                    color: #94a3b8;
                    font-size: 0.74rem;
                    margin: 4px 0 0 0;
                    letter-spacing: 0.3px;
                }
                .nl-section-label {
                    color: #94a3b8;
                    font-size: 0.70rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin: 14px 0 6px 0;
                    padding-bottom: 4px;
                    border-bottom: 1px solid #1e293b;
                }
                .nl-cap-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.76rem;
                    color: #cbd5e1;
                    margin: 8px 0 4px 0;
                }
                .nl-cap-badge {
                    background: #1e293b;
                    color: #60a5fa;
                    font-weight: 600;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 0.72rem;
                }
                .nl-cap-bar-bg {
                    width: 100%;
                    height: 5px;
                    background: #1e293b;
                    border-radius: 4px;
                    overflow: hidden;
                    margin-bottom: 10px;
                }
                .nl-cap-bar-fill {
                    height: 100%;
                    border-radius: 4px;
                    transition: width 0.25s ease;
                }
                .nl-doc-card {
                    background: #111827;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                    padding: 8px 10px;
                    margin-bottom: 6px;
                }
                .nl-doc-name {
                    color: #e2e8f0;
                    font-size: 0.80rem;
                    font-weight: 600;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-bottom: 4px;
                }
                .nl-doc-meta {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.70rem;
                    color: #94a3b8;
                }
                .nl-doc-ext {
                    background: #172554;
                    color: #60a5fa;
                    padding: 1px 6px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 0.66rem;
                }
                section[data-testid="stSidebar"] button[kind="primary"] {
                    background-color: #2563eb;
                    border: 1px solid #3b82f6;
                    color: #ffffff;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                    border-radius: 6px;
                    padding: 0.55rem 1rem;
                    margin-top: 8px;
                }
                section[data-testid="stSidebar"] button[kind="primary"]:hover {
                    background-color: #1d4ed8;
                    border-color: #60a5fa;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Encabezado corporativo
        st.markdown(
            """
            <div class="nl-brand">
                <div class="nl-brand-title">NexLuk Core</div>
                <div class="nl-brand-sub">Asistencia Hibrida y Auditoria Inteligente</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Credencial API
        st.markdown('<div class="nl-section-label">Acceso y Credenciales</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Credencial API Gemini",
            type="password",
            placeholder="Ingresa tu clave API...",
            label_visibility="collapsed",
        )

        # Configuracion de analisis (sin ciberseguridad)
        st.markdown('<div class="nl-section-label">Configuracion de Analisis</div>', unsafe_allow_html=True)
        modo_seleccionado = st.selectbox(
            "Directiva de Operacion",
            options=["cotidiano", "legal", "auditor"],
            format_func=lambda x: x.capitalize(),
        )

        # Modulo de ingesta
        st.markdown('<div class="nl-section-label">Modulo de Ingesta</div>', unsafe_allow_html=True)
        archivos_subidos = st.file_uploader(
            "Cargar documentos (maximo 6)",
            type=["txt", "pdf", "png", "jpg", "jpeg", "eml", "msg"],
            accept_multiple_files=True,
            key="cargador_documentos",
        )

        total_archivos = len(archivos_subidos) if archivos_subidos else 0
        if total_archivos > 6:
            st.error("Limite excedido: solo puedes cargar hasta 6 documentos.")
            archivos_subidos = archivos_subidos[:6]
            total_archivos = 6

        porcentaje = int((total_archivos / 6) * 100)
        color_barra = "#10b981" if total_archivos < 5 else ("#f59e0b" if total_archivos == 5 else "#2563eb")

        st.markdown(
            f"""
            <div class="nl-cap-row">
                <span>Capacidad de ingesta</span>
                <span class="nl-cap-badge">{total_archivos} / 6</span>
            </div>
            <div class="nl-cap-bar-bg">
                <div class="nl-cap-bar-fill" style="width: {porcentaje}%; background: {color_barra};"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if archivos_subidos:
            for indice, archivo in enumerate(archivos_subidos, start=1):
                ext = os.path.splitext(archivo.name)[1].replace(".", "").upper() or "DOC"
                tamano = _formatear_tamano(archivo.size)
                st.markdown(
                    f"""
                    <div class="nl-doc-card" title="{archivo.name}">
                        <div class="nl-doc-name">{indice}. {archivo.name}</div>
                        <div class="nl-doc-meta">
                            <span class="nl-doc-ext">{ext}</span>
                            <span>{tamano}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Tipo de auditoria
        st.markdown('<div class="nl-section-label">Tipo de Auditoria</div>', unsafe_allow_html=True)
        modo_auditoria = st.radio(
            "Modo de procesamiento",
            options=["Auditoria individual", "Auditoria de expediente"],
            index=0,
            label_visibility="collapsed",
        )
        st.session_state.modo_auditoria = modo_auditoria

        # Accion principal
        ejecutar = st.button(
            "Iniciar Secuencia de Analisis",
            type="primary",
            use_container_width=True,
        )

        return api_key, modo_seleccionado, archivos_subidos, modo_auditoria, ejecutar