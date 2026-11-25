import streamlit as st
import traceback
import io
import re
import edge_tts
import asyncio
import os

# Modulos de la arquitectura modular
from utilidades import obtener_texto_documento, construir_expediente, generar_voz_neuronal
from lector import Lector
from escudo import Escudo
from redactor import Redactor
from formateador import Formateador
from prompts import GestorPrompts
from inteligencia import MotorIA
from memoria_sql import BovedaSQL
from estilos import aplicar_estilos
from interfaz import dibujar_sidebar

# Aplicamos la configuracion de pagina y el CSS empresarial
aplicar_estilos()


def mostrar_alertas_phishing(datos):
    alertas = datos.get("alertas_phishing", [])
    if not alertas:
        return

    estado = datos.get("estado_seguridad", "amarillo")
    borde = "#ef4444" if estado == "rojo" else "#f59e0b"
    fondo = "rgba(239, 68, 68, 0.08)" if estado == "rojo" else "rgba(245, 158, 11, 0.08)"
    titulo_color = "#f87171" if estado == "rojo" else "#fbbf24"
    etiqueta_riesgo = "ALERTA CRITICA DE PHISHING" if estado == "rojo" else "ADVERTENCIA: ENLACES SOSPECHOSOS"

    items_html = ""
    for item in alertas:
        url = item.get("url", "URL desconocida")
        indicadores = ", ".join(item.get("indicadores", [])) or "patron_sospechoso"
        items_html += (
            f'<div style="margin-top:8px; padding:8px 10px; background:#0b1120; '
            f'border:1px solid #1e293b; border-radius:6px;">'
            f'<div style="color:#f8fafc; font-size:0.84rem; word-break:break-all;"><strong>URL:</strong> {url}</div>'
            f'<div style="color:#94a3b8; font-size:0.76rem; margin-top:4px;">'
            f'<strong>Indicadores:</strong> <span style="color:{titulo_color};">{indicadores}</span></div>'
            f'</div>'
        )

    st.markdown(
        f"""
        <div style="background:{fondo}; border:1px solid #1e293b; border-left:4px solid {borde};
                    border-radius:8px; padding:14px 16px; margin:12px 0;">
            <div style="color:{titulo_color}; font-size:0.82rem; font-weight:700; letter-spacing:0.6px;">
                {etiqueta_riesgo} ({len(alertas)} detectado(s))
            </div>
            <div style="color:#cbd5e1; font-size:0.82rem; margin-top:4px;">
                El analisis estatico detecto enlaces con patrones asociados a suplantacion o riesgo:
            </div>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# Inicializacion de Session State
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

# Renderizamos la barra lateral
api_key, modo_seleccionado, archivos_subidos, modo_auditoria, ejecutar = dibujar_sidebar()

# Encabezado corporativo principal
st.markdown(
    """
    <div class="nl-hero">
        <div>
            <div class="nl-hero-title">NexLuk Core | Panel de Control</div>
            <div class="nl-hero-sub">Plataforma de asistencia hibrida, analisis documental y auditoria inteligente.</div>
        </div>
        <div class="nl-status-pill">Sistema en linea</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Resumen superior cuando existen documentos cargados
if archivos_subidos:
    st.markdown('<div class="nl-panel-header">Resumen de Ingesta Activa</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documentos", f"{len(archivos_subidos)} / 6", "Capacidad de carga")
    with col2:
        st.metric("Tipo de Auditoria", modo_auditoria)
    with col3:
        st.metric("Directiva Activa", modo_seleccionado.capitalize())

# Logica principal de ejecucion
if ejecutar:
    if not api_key:
        st.error("Solicitud detenida: Se requiere la Credencial API en el panel lateral.")
    elif not archivos_subidos:
        st.warning("Protocolo en espera: Debes cargar al menos un documento.")
    else:
        try:
            lector = Lector()
            documentos = []

            with st.spinner("Leyendo y normalizando documentos..."):
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

            if modo_auditoria == "Auditoria individual":
                reportes = []
                escudo = Escudo()
                gestor_prompts = GestorPrompts()
                motor_ia = MotorIA(api_key=api_key)
                formateador = Formateador()
                progreso = st.progress(0)
                estado_texto = st.empty()
                total = len(documentos)

                for indice, documento in enumerate(documentos, start=1):
                    nombre = documento.get("nombre", f"Documento_{indice}")
                    estado_texto.info(f"Procesando documento {indice} de {total}: {nombre}")

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

                    # Persistencia en Boveda SQLite
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

                estado_texto.empty()
                st.session_state.reporte_actual = reportes
                st.session_state.documento_cargado = documentos[0]
                st.session_state.datos_escudo = reportes[0]["datos_escudo"]
                st.success(f"Auditoria finalizada: {len(reportes)} documento(s) analizado(s).")

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

                st.markdown(
                    """
                    <div class="expediente-card">
                        <h3>Modo Auditoria de Expediente</h3>
                        <p>NexLuk analizara todos los documentos como un conjunto documental integrado.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                escudo = Escudo()
                datos_escudo = escudo.escanear_documento(contenido_expediente)
                st.session_state.datos_escudo_expediente = datos_escudo

                gestor_prompts = GestorPrompts()
                prompt_instruccion = gestor_prompts.obtener_prompt(
                    rol=modo_seleccionado,
                    instruccion_usuario=(
                        "Realiza una auditoria integral del expediente completo. "
                        "Analiza todos los documentos en conjunto y detecta relaciones, "
                        "contradicciones y riesgos. Aqui esta el contenido exacto del expediente "
                        f"para analizar:\n\n{contenido_expediente}"
                    )
                )

                with st.spinner("Ejecutando analisis integral con IA..."):
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

# Panel de resultados
if st.session_state.reporte_actual:
    st.markdown('<div class="nl-panel-header">Panel de Resultados de Auditoria</div>', unsafe_allow_html=True)

    if isinstance(st.session_state.reporte_actual, list):
        for indice, resultado in enumerate(st.session_state.reporte_actual, start=1):
            nombre = resultado.get("nombre", f"Documento {indice}")
            reporte = resultado.get("reporte", "")
            datos = resultado.get("datos_escudo", {})

            with st.expander(f"Documento {indice}: {nombre}", expanded=(indice == 1)):
                seguridad = datos.get("estado_seguridad", "verde")
                col1, col2, col3 = st.columns(3)

                with col1:
                    if seguridad == "verde":
                        st.metric("Estado de Revision", "Normal", "Sin anomalias")
                    else:
                        st.metric("Estado de Revision", "Alerta", "Riesgo detectado")
                with col2:
                    st.metric("IPs Detectadas", len(datos.get("ips", [])))
                with col3:
                    st.metric("URLs Detectadas", len(datos.get("enlaces", [])))

                mostrar_alertas_phishing(datos)

                st.markdown('<div class="nl-panel-header">Reporte Detallado</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="nl-report-box">\n\n{reporte}\n\n</div>', unsafe_allow_html=True)

    else:
        datos = st.session_state.datos_escudo or {}
        seguridad = datos.get("estado_seguridad", "verde")

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if seguridad == "verde":
                st.metric("Estado del Expediente", "Normal", "Sin anomalias")
            else:
                st.metric("Estado del Expediente", "Alerta", "Riesgo detectado")
        with col_s2:
            st.metric("IPs Identificadas", len(datos.get("ips", [])))
        with col_s3:
            st.metric("URLs Analizadas", len(datos.get("enlaces", [])))

        mostrar_alertas_phishing(datos)

        st.markdown('<div class="nl-panel-header">Dictamen Detallado del Expediente</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="nl-report-box">\n\n{st.session_state.reporte_actual}\n\n</div>',
            unsafe_allow_html=True
        )

    # Interfaz de comunicacion NexLuk
    st.markdown('<div class="nl-panel-header">Interfaz de Comunicacion NexLuk</div>', unsafe_allow_html=True)

    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    pregunta_usuario = st.chat_input("Ingresa tu consulta sobre la auditoria...")

    if pregunta_usuario:
        if not api_key:
            st.error("Conexion rechazada: Ingresa la API Key en el panel lateral.")
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

                        # Limpieza de Markdown antes del Text-to-Speech
                        texto_voz = respuesta_limpia
                        texto_voz = re.sub(r'\((.*?)\)', r'entre parentesis \1', texto_voz)
                        texto_voz = texto_voz.replace("*", "").replace("#", "").replace('"', "")
                        texto_voz = re.sub(r'^\s*-\s+', '', texto_voz, flags=re.MULTILINE)

                        try:
                            archivo_audio = "respuesta_nexus.mp3"
                            asyncio.run(generar_voz_neuronal(texto_voz, archivo_audio))
                            st.audio(archivo_audio, format="audio/mp3", autoplay=True)
                        except Exception as error_voz:
                            st.warning(f"No se pudo generar el audio: {error_voz}")

                    except Exception as e:
                        st.error(f"Error de comunicacion: {str(e)}")