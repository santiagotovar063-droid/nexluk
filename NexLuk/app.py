import streamlit as st
import traceback
import io
import re
import edge_tts
import asyncio
import os

# Importamos nuestros propios modulos de la arquitectura modular
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

# Configuracion inicial de la ventana del navegador
try:
    st.set_page_config(page_title="NexLuk Core", layout="wide", initial_sidebar_state="expanded")
except:
    pass

# Aplicamos el CSS personalizado
aplicar_estilos()

# El Session State es la memoria temporal de la app. 
# Si no guardamos las variables aqui, Streamlit las borraria cada que das clic en un boton.
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

# Llamamos a la funcion que dibuja el menu izquierdo y recibimos lo que el usuario eligio
api_key, modo_seleccionado, archivos_subidos, modo_auditoria, ejecutar = dibujar_sidebar()

# Encabezado principal de la aplicacion
st.title("Panel de Control")
st.markdown("Bienvenido al entorno de analisis. El sistema esta en linea.")

# Si el usuario ya subio archivos, mostramos un pequeño resumen superior
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

# Esta es la logica principal que se activa cuando presionan el boton azul
if ejecutar:
    # Validaciones de seguridad antes de arrancar
    if not api_key:
        st.error("Solicitud detenida: Se requiere la Credencial API en el panel lateral.")
    elif not archivos_subidos:
        st.warning("Protocolo en espera: Debes cargar al menos un documento.")
    else:
        try:
            # Instanciamos el lector y preparamos una lista vacia
            lector = Lector()
            documentos = []

            # Bucle para leer y procesar cada archivo subido
            with st.spinner("Leyendo documentos..."):
                for archivo in archivos_subidos:
                    try:
                        documento = lector.leer_archivo(archivo)
                        documentos.append(documento)
                    except Exception as error_archivo:
                        st.error(f"No se pudo leer {archivo.name}: {str(error_archivo)}")

            # Si ningun archivo sirvio, detenemos la ejecucion aqui
            if not documentos:
                st.error("No fue posible leer ninguno de los documentos.")
                st.stop()

            # Guardamos los documentos en memoria para usarlos despues
            st.session_state.documentos_cargados = documentos

            # Logica si el usuario eligio analizar los archivos uno por uno
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

                    # Extraemos el texto puro y lo pasamos por el Escudo (Analisis Estatico)
                    texto_documento = obtener_texto_documento(documento)
                    datos_escudo = escudo.escanear_documento(texto_documento)

                    # Preparamos las instrucciones para la IA dependiendo si es Legal o Ciberseguridad
                    prompt_instruccion = gestor_prompts.obtener_prompt(
                        rol=modo_seleccionado,
                        instruccion_usuario=f"Analiza el documento '{nombre}' bajo el enfoque de {modo_seleccionado}."
                    )

                    # Mandamos el prompt a Gemini y limpiamos su respuesta
                    respuesta_ia = motor_ia.consultar(prompt_instruccion, documento=documento)
                    reporte_limpio = formateador.limpiar_texto(respuesta_ia)

                    # Guardamos el resultado en nuestra lista temporal
                    reportes.append({
                        "nombre": nombre,
                        "reporte": reporte_limpio,
                        "datos_escudo": datos_escudo
                    })

                    # Bloque de persistencia forense (Base de datos SQLite)
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

                    # Actualizamos la barra de progreso
                    progreso.progress(indice / total)

                # Actualizamos la memoria del sistema con todos los reportes generados
                st.session_state.reporte_actual = reportes
                st.session_state.documento_cargado = documentos[0]
                st.session_state.datos_escudo = reportes[0]["datos_escudo"]
                st.success(f"Auditoria finalizada: {len(reportes)} documento(s) analizado(s).")

            # Logica si el usuario eligio analizar todo como un solo expediente cruzado
            else:
                with st.spinner("Construyendo expediente documental..."):
                    # La funcion inyecta separadores visuales para que la IA no mezcle los archivos
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

                # Pasamos el mega-texto por el Escudo
                escudo = Escudo()
                datos_escudo = escudo.escanear_documento(contenido_expediente)
                st.session_state.datos_escudo_expediente = datos_escudo

                # Le inyectamos el texto completo a la IA directamente en el prompt
                gestor_prompts = GestorPrompts()
                prompt_instruccion = gestor_prompts.obtener_prompt(
                    rol=modo_seleccionado,
                    instruccion_usuario=f"Realiza una auditoria integral del expediente completo. Analiza todos los documentos en conjunto y detecta relaciones, contradicciones y riesgos. Aqui esta el contenido exacto del expediente para analizar:\n\n{contenido_expediente}"
                )

                # Solicitamos el analisis semantico
                motor_ia = MotorIA(api_key=api_key)
                respuesta_ia = motor_ia.consultar(prompt_instruccion, documento=documento_expediente)

                formateador = Formateador()
                reporte_limpio = formateador.limpiar_texto(respuesta_ia)

                # Guardamos los resultados globales en memoria
                st.session_state.reporte_actual = reporte_limpio
                st.session_state.documento_cargado = documento_expediente
                st.session_state.datos_escudo = datos_escudo

                # Trazabilidad forense del expediente completo
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

        # Atrapamos fallas criticas para que la app no tire la pantalla completa de error
        except Exception as e:
            st.error(f"Falla en el sistema: {str(e)}")
            st.text(traceback.format_exc())

# Seccion para renderizar los resultados en pantalla si ya existen
if st.session_state.reporte_actual:
    st.markdown("---")

    # Si es una lista, significa que fue auditoria individual
    if isinstance(st.session_state.reporte_actual, list):
        st.markdown("## Resultados de Auditoria")
        for indice, resultado in enumerate(st.session_state.reporte_actual, start=1):
            nombre = resultado.get("nombre", f"Documento {indice}")
            reporte = resultado.get("reporte", "")
            datos = resultado.get("datos_escudo", {})

            # Usamos un expander para no saturar la vista con texto
            with st.expander(f"Documento {indice}: {nombre}", expanded=indice == 1):
                seguridad = datos.get("estado_seguridad", "verde")
                col1, col2, col3 = st.columns(3)

                # Tarjetas visuales que se alimentan del Escudo (Analisis Estatico)
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

    # Si no es lista, significa que fue auditoria cruzada (Expediente)
    else:
        st.markdown("## Dictamen del Expediente")
        datos = st.session_state.datos_escudo or {}
        seguridad = datos.get("estado_seguridad", "verde")

        # Dibujamos las tarjetas globales
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

    # Modulo de comunicacion interactiva (El Chat)
    st.markdown("---")
    st.markdown("### Interfaz de Comunicacion NexLuk")

    # Dibujamos los mensajes previos para mantener el contexto
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    pregunta_usuario = st.chat_input("Ingresa tu peticion para NexLuk...")

    if pregunta_usuario:
        if not api_key:
            st.error("Conexion rechazada: Ingresa la API Key en el panel.")
        else:
            # Mostramos la pregunta en pantalla
            st.session_state.historial_chat.append({"rol": "user", "contenido": pregunta_usuario})
            with st.chat_message("user"):
                st.markdown(pregunta_usuario)

            # Solicitamos la respuesta a la IA
            with st.chat_message("assistant"):
                with st.spinner("Sintetizando respuesta..."):
                    try:
                        # Reagrupamos el contexto de la auditoria para darselo a la IA
                        contexto = st.session_state.reporte_actual
                        if isinstance(contexto, list):
                            contexto_chat = ""
                            for resultado in contexto:
                                contexto_chat += f"\n\nDOCUMENTO: {resultado['nombre']}\n\n{resultado['reporte']}"
                        else:
                            contexto_chat = contexto

                        # Inyectamos el contexto como delimitador para evitar alucinaciones
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

                        # Expresiones regulares (Regex) para limpiar Markdown antes del Text-to-Speech
                        texto_voz = respuesta_limpia
                        texto_voz = re.sub(r'\((.*?)\)', r'entre parentesis \1', texto_voz)
                        texto_voz = texto_voz.replace("*", "").replace("#", "").replace('"', "")
                        texto_voz = re.sub(r'^\s*-\s+', '', texto_voz, flags=re.MULTILINE)

                        # Motor asincrono de voz neuronal
                        try:
                            archivo_audio = "respuesta_nexus.mp3"
                            asyncio.run(generar_voz_neuronal(texto_voz, archivo_audio))
                            st.audio(archivo_audio, format="audio/mp3", autoplay=True)
                        except Exception as error_voz:
                            st.warning(f"No se pudo generar el audio: {error_voz}")

                    except Exception as e:
                        st.error(f"Error de comunicacion: {str(e)}")