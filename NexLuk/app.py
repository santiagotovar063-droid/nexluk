"""
=========================================================
app.py

Orquestador Principal de NexLuk (Streamlit UI).

Funciones principales:
- Enlaza Lector, Escudo, IA y Base de datos.
- Despacha los eventos visuales.
=========================================================
"""

import streamlit as st
import traceback
import io
import re
from gtts import gTTS

from lector import Lector
from escudo import Escudo
from redactor import Redactor
from formateador import Formateador
from prompts import GestorPrompts
from inteligencia import MotorIA
from memoria_sql import BovedaSQL

from estilos import aplicar_estilos
from utilidades import obtener_texto_documento, construir_expediente
from interfaz import dibujar_sidebar

# =========================================================
# CONFIGURACION Y ESTILOS
# =========================================================
aplicar_estilos()

# =========================================================
# SESSION STATE
# =========================================================
if "reporte_actual" not in st.session_state:
    st.session_state.reporte_actual = None
if "documento_cargado" not in st.session_state:
    st.session_state.documento_cargado = None
if "documentos_cargados" not in st.session_state:
    st.session_state.documentos_cargados = []
if "datos_escudo" not in st.session_state:
    st.session_state.datos_escudo = None
if "datos_escudo_expediente" not in st.session_state:
    st.session_state.datos_escudo_expediente = None
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []
if "modo_auditoria" not in st.session_state:
    st.session_state.modo_auditoria = "Auditoria individual"

# =========================================================
# BARRA LATERAL
# =========================================================
api_key, modo_seleccionado, archivos_subidos, modo_auditoria, ejecutar = dibujar_sidebar()

# =========================================================
# CUERPO PRINCIPAL
# =========================================================
st.title("Panel de Control")
st.markdown("Bienvenido al entorno de analisis. El sistema esta en linea.")

# =========================================================
# RESUMEN DE DOCUMENTOS
# =========================================================
if archivos_subidos:
    st.markdown("---")
    st.markdown("### Expediente cargado")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documentos", len(archivos_subidos), "de 6 maximo")
    with col2:
        st.metric("Modo", modo_auditoria)
    with col3:
        st.metric("Directiva", modo_seleccionado.capitalize())

# =========================================================
# EJECUCION PRINCIPAL
# =========================================================
if ejecutar:
    if not api_key:
        st.error("Solicitud detenida: Se requiere la Credencial API en el panel lateral.")
    elif not archivos_subidos:
        st.warning("Protocolo en espera: Debes cargar al menos un documento.")
    else:
        try:
            lector = Lector()
            documentos = []

            # -------------------------------------------------
            # LECTURA DE ARCHIVOS
            # -------------------------------------------------
            with st.spinner("Leyendo documentos..."):
                for archivo in archivos_subidos:
                    try:
                        documento = lector.leer_archivo(archivo)
                        documentos.append(documento)
                    except Exception as error_archivo:
                        st.error(f"No se pudo leer {archivo.name}: {str(error_archivo)}")

            if not documentos:
                st.error("No fue posible leer ninguno de los documentos.")
                st.stop()

            st.session_state.documentos_cargados = documentos

            # -------------------------------------------------
            # AUDITORIA INDIVIDUAL
            # -------------------------------------------------
            if modo_auditoria == "Auditoria individual":
                reportes = []
                escudo = Escudo()
                gestor_prompts = GestorPrompts()
                motor_ia = MotorIA(api_key=api_key)
                formateador = Formateador()
                progreso = st.progress(0)
                total = len(documentos)

                for indice, documento in enumerate(documentos, start=1):
                    nombre = documento.get("nombre", f"Documento_{indice}")
                    st.markdown(f"### Analizando documento {indice}/{total}")
                    st.info(f"Documento: {nombre}")

                    texto_documento = obtener_texto_documento(documento)
                    datos_escudo = escudo.escanear_documento(texto_documento)

                    prompt_instruccion = gestor_prompts.obtener_prompt(
                        rol=modo_seleccionado,
                        instruccion_usuario=f"Analiza el documento '{nombre}' bajo el enfoque de {modo_seleccionado}."
                    )

                    respuesta_ia = motor_ia.consultar(prompt_instruccion, documento=documento)
                    reporte_limpio = formateador.limpiar_texto(respuesta_ia)

                    reportes.append({
                        "nombre": nombre,
                        "reporte": reporte_limpio,
                        "datos_escudo": datos_escudo
                    })

                    try:
                        boveda = BovedaSQL()
                        id_audit = boveda.guardar_registro(
                            archivo=nombre,
                            modo=modo_seleccionado,
                            analisis_completo=reporte_limpio
                        )
                        boveda.guardar_entidades(id_audit, datos_escudo)
                    except Exception as error_boveda:
                        st.warning(f"No se pudo guardar {nombre} en la boveda: {str(error_boveda)}")

                    progreso.progress(indice / total)

                st.session_state.reporte_actual = reportes
                st.session_state.documento_cargado = documentos[0]
                st.session_state.datos_escudo = reportes[0]["datos_escudo"]
                st.success(f"Auditoria finalizada: {len(reportes)} documento(s) analizado(s).")

            # -------------------------------------------------
            # AUDITORIA DE EXPEDIENTE
            # -------------------------------------------------
            else:
                with st.spinner("Construyendo expediente documental..."):
                    contenido_expediente = construir_expediente(documentos)
                    documento_expediente = {
                        "nombre": f"Expediente_{len(documentos)}_documentos",
                        "extension": "txt",
                        "tipo": "texto",
                        "contenido": contenido_expediente,
                        "mime": "text/plain"
                    }

                st.markdown("""
                <div class="expediente-card">
                    <h3>Modo Auditoria de Expediente</h3>
                    <p>NexLuk analizara los documentos como un conjunto documental.</p>
                </div>
                """, unsafe_allow_html=True)

                escudo = Escudo()
                datos_escudo = escudo.escanear_documento(contenido_expediente)
                st.session_state.datos_escudo_expediente = datos_escudo

                gestor_prompts = GestorPrompts()
                prompt_instruccion = gestor_prompts.obtener_prompt(
                    rol=modo_seleccionado,
                    instruccion_usuario=f"Realiza una auditoria legal integral del expediente completo. Analiza todos los documentos en conjunto y detecta relaciones, contradicciones y riesgos. Aqui esta el contenido exacto del expediente para analizar:\n\n{contenido_expediente}"
                )

                motor_ia = MotorIA(api_key=api_key)
                respuesta_ia = motor_ia.consultar(prompt_instruccion, documento=documento_expediente)

                formateador = Formateador()
                reporte_limpio = formateador.limpiar_texto(respuesta_ia)

                st.session_state.reporte_actual = reporte_limpio
                st.session_state.documento_cargado = documento_expediente
                st.session_state.datos_escudo = datos_escudo

                try:
                    boveda = BovedaSQL()
                    nombres = ", ".join(d.get("nombre", "Sin nombre") for d in documentos)
                    id_audit = boveda.guardar_registro(
                        archivo=f"EXPEDIENTE: {nombres}",
                        modo=modo_seleccionado,
                        analisis_completo=reporte_limpio
                    )
                    boveda.guardar_entidades(id_audit, datos_escudo)
                except Exception as error_boveda:
                    st.warning(f"El analisis termino, pero no fue posible guardar: {str(error_boveda)}")

                st.success("Auditoria del expediente finalizada.")

        except Exception as e:
            st.error(f"Falla en el sistema: {str(e)}")
            st.text(traceback.format_exc())

# =========================================================
# MOSTRAR RESULTADOS
# =========================================================
if st.session_state.reporte_actual:
    st.markdown("---")

    if isinstance(st.session_state.reporte_actual, list):
        st.markdown("## Resultados de Auditoria")
        for indice, resultado in enumerate(st.session_state.reporte_actual, start=1):
            nombre = resultado.get("nombre", f"Documento {indice}")
            reporte = resultado.get("reporte", "")
            datos = resultado.get("datos_escudo", {})

            with st.expander(f"Documento {indice}: {nombre}", expanded=indice == 1):
                seguridad = datos.get("estado_seguridad", "verde")
                col1, col2, col3 = st.columns(3)

                with col1:
                    if seguridad == "verde":
                        st.metric("Estado", "Seguro", "Sin anomalias")
                    else:
                        st.metric("Estado", "Alerta", "Riesgo detectado")
                with col2:
                    st.metric("IPs", len(datos.get("ips", [])))
                with col3:
                    st.metric("URLs", len(datos.get("enlaces", [])))

                st.markdown("### Reporte Detallado")
                st.markdown(reporte)

    else:
        st.markdown("## Dictamen del Expediente")
        datos = st.session_state.datos_escudo or {}
        seguridad = datos.get("estado_seguridad", "verde")

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if seguridad == "verde":
                st.metric("Estado", "Seguro", "Sin anomalias")
            else:
                st.metric("Estado", "Alerta", "Riesgo detectado")
        with col_s2:
            st.metric("IPs Identificadas", len(datos.get("ips", [])))
        with col_s3:
            st.metric("URLs Analizadas", len(datos.get("enlaces", [])))

        st.markdown("### Reporte Detallado")
        st.markdown(st.session_state.reporte_actual)

    # =====================================================
    # CHAT
    # =====================================================
    st.markdown("---")
    st.markdown("### Interfaz de Comunicacion NexLuk")

    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    pregunta_usuario = st.chat_input("Ingresa tu peticion para NexLuk...")

    if pregunta_usuario:
        if not api_key:
            st.error("Conexion rechazada: Ingresa la API Key en el panel.")
        else:
            st.session_state.historial_chat.append({"rol": "user", "contenido": pregunta_usuario})
            with st.chat_message("user"):
                st.markdown(pregunta_usuario)

            with st.chat_message("assistant"):
                with st.spinner("Sintetizando respuesta..."):
                    try:
                        contexto = st.session_state.reporte_actual
                        if isinstance(contexto, list):
                            contexto_chat = ""
                            for resultado in contexto:
                                contexto_chat += f"\n\nDOCUMENTO: {resultado['nombre']}\n\n{resultado['reporte']}"
                        else:
                            contexto_chat = contexto

                        prompt_chat = f"""
Actua como NexLuk en modo {modo_seleccionado}.
Contexto de la auditoria:
{contexto_chat}

Pregunta o instruccion actual del usuario:
{pregunta_usuario}

Responde utilizando exclusivamente la informacion disponible en la auditoria. No inventes datos.
"""
                        motor_chat = MotorIA(api_key=api_key)
                        respuesta_chat = motor_chat.consultar(
                            prompt_chat,
                            documento=st.session_state.documento_cargado
                        )

                        formateador_chat = Formateador()
                        respuesta_limpia = formateador_chat.limpiar_texto(respuesta_chat)

                        st.markdown(respuesta_limpia)
                        st.session_state.historial_chat.append({
                            "rol": "assistant",
                            "contenido": respuesta_limpia
                        })

                        texto_voz = respuesta_limpia
                        texto_voz = re.sub(r'\((.*?)\)', r'entre parentesis \1', texto_voz)
                        texto_voz = texto_voz.replace("*", "").replace("#", "").replace('"', "")
                        texto_voz = re.sub(r'^\s*-\s+', '', texto_voz, flags=re.MULTILINE)

                        try:
                            tts = gTTS(text=texto_voz, lang="es", tld="com.mx")
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            st.audio(audio_buffer, format="audio/mp3")
                        except Exception:
                            pass

                    except Exception as e:
                        st.error(f"Error de comunicacion: {str(e)}")