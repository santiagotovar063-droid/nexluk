import streamlit as st

def dibujar_sidebar():
    with st.sidebar:
        st.markdown("## NexLuk Core")
        st.caption("Terminal de Asistencia Hibrida")
        st.markdown("---")

        api_key = st.text_input("Credencial API Gemini", type="password")

        st.markdown("### Configuracion de Analisis")
        modo_seleccionado = st.selectbox(
            "Directiva de Operacion:",
            options=["cotidiano", "ciberseguridad", "legal", "auditor"],
            format_func=lambda x: x.capitalize()
        )

        st.markdown("---")
        st.markdown("### Modulo de Ingesta")
        st.caption("Puedes cargar hasta 6 documentos.")
        
        archivos_subidos = st.file_uploader(
            "Cargar documentos",
            type=["txt", "pdf", "png", "jpg", "jpeg", "eml", "msg"],
            accept_multiple_files=True,
            key="cargador_documentos"
        )

        if archivos_subidos:
            if len(archivos_subidos) > 6:
                st.error("Limite excedido: solo puedes cargar hasta 6 documentos.")
                archivos_subidos = archivos_subidos[:6]

            st.markdown("---")
            st.markdown(f"### Documentos cargados: {len(archivos_subidos)}/6")
            
            for indice, archivo in enumerate(archivos_subidos, start=1):
                st.markdown(
                    f"""
                    <div class="document-card">
                        <strong>{indice}. {archivo.name}</strong><br>
                        <small>{archivo.type}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("### Tipo de Auditoria")
        
        modo_auditoria = st.radio(
            "Selecciona como deseas analizar los documentos:",
            options=["Auditoria individual", "Auditoria de expediente"],
            index=0
        )
        st.session_state.modo_auditoria = modo_auditoria

        st.markdown("---")
        ejecutar = st.button("Iniciar Secuencia de Analisis", type="primary", use_container_width=True)

        return api_key, modo_seleccionado, archivos_subidos, modo_auditoria, ejecutar