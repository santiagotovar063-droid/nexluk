def obtener_texto_documento(documento):
    if not documento:
        return ""

    contenido = documento.get("contenido")
    if isinstance(contenido, str):
        return contenido

    texto = documento.get("texto")
    if isinstance(texto, str):
        return texto

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