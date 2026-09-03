"""
=========================================================
lector.py

Sistema avanzado de ingestion y normalizacion de archivos.
=========================================================
"""

import email
from email import policy
from PIL import Image
import io

class Lector:
    def __init__(self):
        self.formatos_texto = {"txt", "md", "log", "csv"}
        self.formatos_imagen = {"png", "jpg", "jpeg"}
        self.formatos_documento = {"pdf"}
        self.formatos_correo = {"eml", "msg"}

    def leer_archivo(self, uploaded_file):
        if not uploaded_file:
            raise ValueError("No se proporciono ningun archivo para leer.")

        nombre_archivo = uploaded_file.name
        extension = nombre_archivo.split(".")[-1].lower()

        resultado = {
            "nombre": nombre_archivo,
            "extension": extension,
            "texto": "",
            "crudo": None,
            "metadatos": {}
        }

        try:
            if extension in self.formatos_texto:
                resultado["texto"] = self._procesar_texto(uploaded_file)
                
            elif extension in self.formatos_documento:
                resultado["crudo"] = uploaded_file.read()
                
            elif extension in self.formatos_imagen:
                resultado["crudo"] = self._procesar_imagen(uploaded_file)
                
            elif extension == "eml":
                resultado["texto"], resultado["metadatos"] = self._procesar_eml(uploaded_file)
                
            else:
                raise Exception(f"Formato de archivo no soportado: .{extension}")

        except Exception as e:
            raise RuntimeError(f"Error procesando el archivo '{nombre_archivo}': {str(e)}")

        return resultado

    def _procesar_texto(self, archivo):
        bytes_contenido = archivo.read()
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return bytes_contenido.decode(encoding)
            except UnicodeDecodeError:
                continue
        return bytes_contenido.decode("utf-8", errors="ignore")

    def _procesar_imagen(self, archivo):
        imagen = Image.open(archivo)
        if imagen.mode not in ("RGB", "L"):
            imagen = imagen.convert("RGB")
        return imagen

    def _procesar_eml(self, archivo):
        raw_bytes = archivo.read()
        mensaje = email.message_from_bytes(raw_bytes, policy=policy.default)
        
        metadatos = {
            "de": mensaje.get("From", ""),
            "para": mensaje.get("To", ""),
            "asunto": mensaje.get("Subject", ""),
            "fecha": mensaje.get("Date", "")
        }

        cuerpo_texto = ""
        if mensaje.is_multipart():
            for parte in mensaje.walk():
                if parte.get_content_type() == "text/plain":
                    cuerpo_texto = parte.get_content()
                    break
        else:
            cuerpo_texto = mensaje.get_content()

        return cuerpo_texto, metadatos