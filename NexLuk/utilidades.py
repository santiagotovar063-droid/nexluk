import edge_tts
import asyncio

async def generar_voz_neuronal(texto, ruta_salida): #Todo este modulo es para generar voz neuronal, se le pasa el texto y la ruta de salida donde se guardara el archivo de audio
    """
    Convierte texto a voz neuronal usando Microsoft Edge TTS.
    Voces disponibles: Jorge(Hombre), Dalia (Mujer)
    """
    voz = "es-MX-JorgeNeural" 
    comunicar = edge_tts.Communicate(texto, voz)
    await comunicar.save(ruta_salida)

def obtener_texto_documento(documento): #En este bloque se define como obtener el texto de un documento, ya sea que venga en 'texto', 'contenido' o 'crudo'
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


def construir_expediente(documentos): #Se define como debe verse el expediente, con los documentos que se le pasen, y se les da un formato para que sea mas facil de leer
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