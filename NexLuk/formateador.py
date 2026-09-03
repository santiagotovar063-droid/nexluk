"""
=========================================================
formateador.py

Sistema avanzado de post-procesamiento y limpieza de texto.

Se encarga de:
- Normalizar espacios y saltos de linea excesivos.
- Eliminar marcas residuales de salida de IA (ej. bloques de codigo sueltos).
- Asegurar un formato Markdown limpio y estetico para la interfaz.
=========================================================
"""

import re

class Formateador:
    def __init__(self):
        pass

    # =========================================================
    # LIMPIEZA GENERAL DE TEXTO
    # =========================================================

    def limpiar_texto(self, texto):
        """
        Limpia, normaliza y sanea una cadena de texto para su correcta visualizacion.
        """
        if not texto or not isinstance(texto, str):
            return ""

        # 1. Normalizar espacios multiples horizontales (conservando saltos de linea)
        texto_limpio = re.sub(r'[ \t]+', ' ', texto)

        # 2. Limitar saltos de linea consecutivos excesivos (maximo dos)
        texto_limpio = re.sub(r'\n{3,}', '\n\n', texto_limpio)

        # 3. Eliminar etiquetas residuales comunes generadas por modelos de lenguaje
        texto_limpio = texto_limpio.replace("```json", "").replace("```html", "").replace("```markdown", "")

        # 4. Retirar espacios en blanco al inicio y final de la cadena
        return texto_limpio.strip()

    # =========================================================
    # ESTRUCTURACION DE BLOQUES (UI / REPORTE)
    # =========================================================

    def estructurar_seccion(self, titulo, contenido):
        """
        Envuelve un texto en una seccion con formato Markdown estandar
        para mantener la consistencia visual en los reportes generados.
        """
        if not contenido:
            return ""
            
        contenido_limpio = self.limpiar_texto(contenido)
        return f"### {titulo}\n\n{contenido_limpio}\n\n---"