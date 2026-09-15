import edge_tts
import asyncio

async def generar_voz_neuronal(texto, ruta_salida):
    """
    Convierte texto a voz neuronal usando Microsoft Edge TTS.
    Voces disponibles MX: es-MX-JorgeNeural (Hombre), es-MX-DaliaNeural (Mujer)
    """
    voz = "es-MX-JorgeNeural" 
    comunicar = edge_tts.Communicate(texto, voz)
    await comunicar.save(ruta_salida)

def obtener_texto_documento(documento):
    if not documento:
        return ""

    # Intenta buscar 'texto'
    texto = documento.get("texto")
    if texto and isinstance(texto, str):
        return texto

    # Intenta buscar 'contenido'
    contenido = documento.get("contenido")
    if contenido and isinstance(contenido, str):
        return contenido

    # Si el Lector lo mando como bytes 'crudo'
    crudo = documento.get("crudo")
    if crudo and isinstance(crudo, bytes):
        try:
            return crudo.decode('utf-8')
        except:
            return str(crudo)

    return ""


def construir_expediente(documentos):
    partes = []

    for indice, documento in enumerate(documentos, start=1):
        nombre = documento.get("nombre", f"Documento_{indice}")
        tipo = documento.get("tipo", "desconocido")
        contenido = obtener_texto_documento(documento)

        partes.append(
            f"""
==================================================
DOCUMENTO {indice}
==================================================

NOMBRE:
{nombre}

TIPO:
{tipo}

CONTENIDO:
{contenido}

==================================================
FIN DOCUMENTO {indice}
==================================================
"""
        )

    return "\n".join(partes)