"""
=========================================================
app.py

Orquestador Principal de NexLuk (Streamlit UI).
Integra todos los modulos: Lector, Escudo, Redactor,
Formateador, GestorPrompts, MotorIA, BovedaSQL y Voz (gTTS).
Sin tildes ni emojis para evitar conflictos de codificacion.
=========================================================
"""

import streamlit as st
import traceback
import io
import re
from gtts import gTTS

# Importacion de nuestros modulos locales
from lector import Lector
from escudo import Escudo
from redactor import Redactor
from formateador import Formateador
from prompts import GestorPrompts
from inteligencia import MotorIA
from memoria_sql import BovedaSQL

# =========================================================
# CONFIGURACION DE LA PAGINA Y DISENO VISUAL
# =========================================================
st.set_page_config(
    page_title="NexLuk | Asistente Hibrido Ciber-Legal",
    page_icon="N",
    layout="wide"
)

# Inyeccion de Estilos CSS Personalizados para la Interfaz
st.markdown("""
    <style>
    /* Estilo general del fondo principal */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Personalizacion de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Tarjetas de metricas y contenedores personalizados */
    div.stMetric {
        background-color: #21262d;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }

    /* Botones principales con estilo llamativo */
    .stButton>button {
        border-radius: 6px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estados de sesion si no existen
if "reporte_actual" not in st.session_state:
    st.session_state.reporte_actual = None
if "documento_cargado" not in st.session_state:
    st.session_state.documento_cargado = None
if "datos_escudo" not in st.session_state:
    st.session_state.datos_escudo = None
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []

# =========================================================
# BARRA LATERAL (CONFIGURACION Y ENTRADAS)
# =========================================================
with st.sidebar:
    st.markdown("## NexLuk Core")
    st.caption("Asistente Operativo Hibrido")
    st.markdown("---")

    # 1. Credencial de Gemini
    api_key = st.text_input("API Key de Gemini", type="password", help="Ingresa tu clave de la API de Google AI Studio.")
    
    # 2. Selector de Modo / Rol
    st.markdown("### Modo de Operacion")
    modo_seleccionado = st.selectbox(
        "Selecciona el enfoque:",
        options=["cotidiano", "ciberseguridad", "legal", "auditor"],
        format_func=lambda x: x.capitalize()
    )

    st.markdown("---")

    # 3. Subida de Archivos
    st.markdown("### Ingesta de Documentos")
    archivo_subido = st.file_uploader(
        "Sube un archivo (TXT, PDF, Imagen, EML)",
        type=["txt", "pdf", "png", "jpg", "jpeg", "eml"]
    )

    st.markdown("---")
    
    # Boton de ejecucion principal
    ejecutar = st.button("Ejecutar Analisis", type="primary", use_container_width=True)

# =========================================================
# CUERPO PRINCIPAL (PANEL DE ACCION Y RESULTADOS)
# =========================================================
st.title("Panel de Control NexLuk")

# Si el usuario subio un archivo y dio clic en ejecutar
if ejecutar:
    if not api_key:
        st.warning("Por favor, ingresa tu API Key de Gemini en la barra lateral.")
    elif not archivo_subido:
        st.warning("Sube al menos un archivo para iniciar el analisis.")
    else:
        try:
            with st.spinner("Procesando informacion con los motores locales..."):
                # 1. Lectura e ingestion
                lector = Lector()
                documento = lector.leer_archivo(archivo_subido)
                st.session_state.documento_cargado = documento

                # 2. Escaneo de seguridad local (Escudo - Cero Tokens)
                texto_a_escanear = documento.get("texto", "")
                if not texto_a_escanear and documento.get("crudo") and isinstance(documento.get("crudo"), bytes):
                    texto_a_escanear = str(documento.get("crudo"))
                
                escudo = Escudo()
                datos_escudo = escudo.escanear_documento(texto_a_escanear)
                st.session_state.datos_escudo = datos_escudo

                # 3. Analisis Inteligente con Gemini
                gestor_prompts = GestorPrompts()
                prompt_instruccion = gestor_prompts.obtener_prompt(
                    rol=modo_seleccionado,
                    instruccion_usuario=f"Analiza el documento adjunto '{archivo_subido.name}' bajo el enfoque de {modo_seleccionado}."
                )

                motor_ia = MotorIA(api_key=api_key)
                respuesta_ia = motor_ia.consultar(prompt_instruccion, documento=documento)

                # 4. Formateo de salida
                formateador = Formateador()
                reporte_limpio = formateador.limpiar_texto(respuesta_ia)
                st.session_state.reporte_actual = reporte_limpio

                # 5. Resguardo en Boveda SQL
                boveda = BovedaSQL()
                id_audit = boveda.guardar_registro(
                    archivo=archivo_subido.name,
                    modo=modo_seleccionado,
                    analisis_completo=reporte_limpio
                )
                boveda.guardar_entidades(id_audit, datos_escudo)

                st.success("Analisis completado y respaldado en la Boveda con exito.")

        except Exception as e:
            st.error(f"Ocurrio un error durante el proceso: {str(e)}")
            st.text(traceback.format_exc())

# =========================================================
# MOSTRAR RESULTADOS Y SEMAFORO DE SEGURIDAD
# =========================================================
if st.session_state.reporte_actual:
    st.markdown("---")
    
    # Mostrar alertas del Escudo (Semaforo)
    if st.session_state.datos_escudo:
        seguridad = st.session_state.datos_escudo.get("estado_seguridad", "verde")
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            if seguridad == "verde":
                st.success("Estado: Limpio")
            else:
                st.warning("Estado: Advertencias detectadas")
                
        with col_s2:
            num_ips = len(st.session_state.datos_escudo.get("ips", []))
            st.metric("IPs Encontradas", num_ips)
            
        with col_s3:
            num_urls = len(st.session_state.datos_escudo.get("enlaces", []))
            st.metric("Enlaces Analizados", num_urls)

    st.markdown("### Reporte de Analisis")
    st.markdown(st.session_state.reporte_actual)
    st.markdown("---")

    # =========================================================
    # BARRA DE CHAT INTERACTIVO (CON VOZ FILTRADA Y DOCUMENTO)
    # =========================================================
    st.markdown("### Conversar con NexLuk sobre este documento")

    # Mostrar historial de chat en pantalla
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    # Entrada de texto para chatear
    pregunta_usuario = st.chat_input("Escribe tu duda, correccion o solicitud...")

    if pregunta_usuario:
        if not api_key:
            st.error("Se requiere la API Key en la barra lateral para usar el chat.")
        else:
            # Registrar pregunta del usuario
            st.session_state.historial_chat.append({"rol": "user", "contenido": pregunta_usuario})
            with st.chat_message("user"):
                st.markdown(pregunta_usuario)

            # Generar respuesta de la IA basada en el contexto actual
            with st.chat_message("assistant"):
                with st.spinner("NexLuk esta respondiendo..."):
                    try:
                        prompt_chat = f"""
                        Actua como NexLuk en modo {modo_seleccionado}. 
                        Contexto del documento analizado previamente:
                        {st.session_state.reporte_actual}
                        
                        Pregunta o instruccion actual del usuario:
                        {pregunta_usuario}
                        """
                        motor_chat = MotorIA(api_key=api_key)
                        respuesta_chat = motor_chat.consultar(prompt_chat, documento=st.session_state.documento_cargado)
                        
                        formateador_chat = Formateador()
                        respuesta_limpia = formateador_chat.limpiar_texto(respuesta_chat)

                        st.markdown(respuesta_limpia)
                        st.session_state.historial_chat.append({"rol": "assistant", "contenido": respuesta_limpia})

                        # --- FILTRO FONETICO PARA LA VOZ ---
                        texto_voz = respuesta_limpia
                        
                        # Cambiar formato de parentesis a lenguaje natural
                        texto_voz = re.sub(r'\((.*?)\)', r'entre parentesis \1', texto_voz)
                        
                        # Eliminar asteriscos, numerales y comillas que ensucian la lectura
                        texto_voz = texto_voz.replace('*', '').replace('#', '').replace('"', '')
                        
                        # Suavizar guiones de listas
                        texto_voz = re.sub(r'^\s*-\s+', '', texto_voz, flags=re.MULTILINE)
                        
                        # Sintesis de voz automatica filtrada (gTTS)
                        try:
                            tts = gTTS(text=texto_voz, lang='es', tld='com.mx')
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            st.audio(audio_buffer, format="audio/mp3", autoplay=True)
                        except Exception:
                            pass

                    except Exception as e:
                        st.error(f"Error en el chat: {str(e)}")

else:
    st.info("Sube un documento en la barra lateral y presiona 'Ejecutar Analisis' para comenzar.")