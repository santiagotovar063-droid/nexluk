"""
=========================================================
redactor.py

Sistema avanzado de generacion y estructuracion de respuestas.

Permite:
- Mantener plantillas estandarizadas para correos, reportes y minutas.
- Formatear respuestas de texto plano o markdown estructurado.
- Generar plantillas corporativas con variables dinamicas de forma local.
=========================================================
"""

class Redactor:
    def __init__(self):
        # =====================================================
        # BANCO DE PLANTILLAS CORPORATIVAS Y TECNICAS
        # =====================================================
        self.plantillas = {
            
            # --- OPERATIVAS / COTIDIANAS ---
            "correo_formal": (
                "Asunto: {asunto}\n\n"
                "Estimado/a {destinatario},\n\n"
                "Por medio de la presente, me dirijo a usted con relacion a {motivo}.\n\n"
                "Quedo a su entera disposicion para cualquier duda, aclaracion o seguimiento necesario.\n\n"
                "Atentamente,\n"
                "{remitente}"
            ),
            
            "seguimiento_rapido": (
                "Hola {destinatario},\n\n"
                "Espero que te encuentres bien. Te escribo para dar seguimiento al tema de {tema}.\n"
                "Agradecere tus comentarios para poder avanzar con {proximo_paso}.\n\n"
                "Saludos cordiales,\n"
                "{remitente}"
            ),

            # --- TECNICAS / CIBERSEGURIDAD ---
            "reporte_red": (
                "REPORTE TECNICO DE DIAGNOSTICO\n"
                "=========================================================\n"
                "Fecha: {fecha}\n"
                "Objetivo / Host: {ip}\n"
                "---------------------------------------------------------\n\n"
                "[DIAGNOSTICO INICIAL]\n"
                "{diagnostico}\n\n"
                "[HALLAZGOS CLAVE]\n"
                "{hallazgos}\n\n"
                "[RECOMENDACION TECNICA]\n"
                "{recomendacion}\n"
            ),

            "incidente_seguridad": (
                "ALERTA PRELIMINAR DE INCIDENTE\n"
                "=========================================================\n"
                "Sistema / Activo: {activo}\n"
                "Nivel de Riesgo: {nivel_riesgo}\n"
                "Anomalia Detectada: {anomalia}\n\n"
                "Acciones Inmediatas Ejecutadas:\n"
                "{acciones}\n"
            ),

            # --- ADMINISTRATIVAS / CORPORATIVAS ---
            "nda_resumido": (
                "ACUERDO DE CONFIDENCIALIDAD (RESUMEN OPERATIVO)\n"
                "=========================================================\n"
                "Entre las partes {parte_a} y {parte_b}, se establece el compromiso "
                "de confidencialidad respecto a la informacion vinculada con '{proyecto}', "
                "vigente a partir de la fecha {fecha}.\n"
            )
        }

    # =========================================================
    # OBTENER CATALOGO
    # =========================================================

    def obtener_catalogo(self):
        """Devuelve las llaves de todas las plantillas disponibles."""
        return list(self.plantillas.keys())

    # =========================================================
    # GENERAR DOCUMENTO / PLANTILLA
    # =========================================================

    def generar(self, tipo_plantilla, **datos):
        """
        Toma una plantilla por su nombre e inyecta los datos proporcionados
        en formato de argumentos clave-valor.
        """
        if tipo_plantilla not in self.plantillas:
            return f"Error: La plantilla '{tipo_plantilla}' no se encuentra registrada en el sistema."
            
        try:
            plantilla_base = self.plantillas[tipo_plantilla]
            return plantilla_base.format(**datos)
            
        except KeyError as e:
            return f"Error de redaccion: Falta el parametro obligatorio {e} para completar la plantilla."
        except Exception as e:
            return f"Error inesperado al generar la redaccion: {str(e)}"