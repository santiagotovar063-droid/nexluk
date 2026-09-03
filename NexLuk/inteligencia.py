"""
=========================================================
inteligencia.py

Sistema avanzado de conexion e interaccion con Gemini.

Se encarga de:
- Empacar archivos e imagenes de forma multimodal.
- Integrar dinamicamente los contextos del GestorPrompts.
- Gestionar peticiones de analisis profundo y chat libre
  con manejo de errores y control de respuestas.
=========================================================
"""

from google import genai
from google.genai import types
from io import BytesIO

class MotorIA:
    def __init__(self, api_key, modelo="gemini-2.5-flash"):
        if not api_key:
            raise ValueError("Se requiere una API Key valida para inicializar el MotorIA.")
        
        self.client = genai.Client(api_key=api_key)
        self.modelo = modelo

    # =========================================================
    # EMPAQUETADO MULTIMODAL DE DATOS
    # =========================================================

    def _empacar_documento(self, documento):
        """
        Traduce el formato normalizado del Lector al formato 
        multimodal que la API de Gemini comprende (Bytes/Partes).
        """
        paquete = []
        
        if not documento:
            return paquete

        # Si el documento contiene texto plano extraido
        if documento.get("texto"):
            paquete.append(f"--- CONTENIDO DEL DOCUMENTO ---\n{documento['texto']}")

        # Si el documento contiene datos binarios en crudo (PDFs o imagenes)
        if documento.get("crudo"):
            extension = documento.get("extension", "").lower()
            
            if extension == "pdf":
                paquete.append(
                    types.Part.from_bytes(
                        data=documento["crudo"],
                        mime_type="application/pdf"
                    )
                )
            elif extension in ["png", "jpg", "jpeg"]:
                buffer = BytesIO()
                documento["crudo"].save(buffer, format="PNG")
                buffer.seek(0)
                paquete.append(
                    types.Part.from_bytes(
                        data=buffer.getvalue(),
                        mime_type="image/png"
                    )
                )

        return paquete

    # =========================================================
    # EJECUCION DE CONSULTAS Y ANALISIS
    # =========================================================

    def consultar(self, instruccion_final, documento=None):
        """
        Envia la instruccion procesada (que ya incluye el prompt especializado)
        junto con el documento opcional a Gemini.
        """
        try:
            contenido_prompt = [instruccion_final]

            # Si hay un documento adjunto, lo sumamos al contexto de la IA
            if documento:
                partes_documento = self._empacar_documento(documento)
                contenido_prompt.extend(partes_documento)

            respuesta = self.client.models.generate_content(
                model=self.modelo,
                contents=contenido_prompt
            )

            if not respuesta or not respuesta.text:
                return "Error: La IA no devolvio ninguna respuesta o el contenido fue bloqueado por filtros de seguridad."

            return respuesta.text

        except Exception as e:
            return f"Error critico al conectar con el motor de IA: {str(e)}"