"""
escudo.py

Modulo de analisis estatico local y extraccion de entidades.
Opera en segundo plano (sin llamadas a IA/tokens) para:
- Extraccion de URLs y deteccion de indicadores de phishing.
- Deteccion y clasificacion de direcciones IP.
- Extraccion limpia de correos electronicos.
- Evaluacion de nivel de alerta preliminar.
"""

import re
import ipaddress
from urllib.parse import urlparse


class Escudo:
    def __init__(self):
        self.patron_ipv4 = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        self.patron_ipv6 = r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'
        self.patron_correo = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        self.patron_url = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w./?%&=]*)?'

        self.keywords_sospechosas = {
            "login", "signin", "verify", "update", "secure",
            "account", "banking", "auth", "password", "confirm",
            "verificar", "actualizar", "cuenta", "clave", "banco",
            "urgente", "suspendida", "recuperar", "acceso"
        }

    def escanear_documento(self, texto):
        if not texto or not isinstance(texto, str):
            return {
                "correos": [],
                "ips": [],
                "enlaces": [],
                "alertas_phishing": [],
                "estado_seguridad": "verde",
                "nivel_alerta": 0
            }

        correos = self.extraer_correos(texto)
        ips = self.analizar_ips(texto)
        enlaces = self.analizar_enlaces(texto)

        alertas_phishing = [e for e in enlaces if e.get("sospechoso", False)]

        estado_seguridad = "verde"
        nivel_alerta = 0

        if alertas_phishing:
            estado_seguridad = "amarillo"
            nivel_alerta = 1

        # Si hay multiples enlaces sospechosos o un enlace apunta directo a una IP, sube a rojo
        if len(alertas_phishing) >= 2 or any("ip_en_url" in e.get("indicadores", []) for e in alertas_phishing):
            estado_seguridad = "rojo"
            nivel_alerta = 2

        ips_publicas = [ip for ip in ips if ip["tipo"] == "Publica"]
        if len(ips_publicas) > 5:
            if estado_seguridad == "verde":
                estado_seguridad = "amarillo"
            nivel_alerta = max(nivel_alerta, 1)

        return {
            "correos": correos,
            "ips": ips,
            "enlaces": enlaces,
            "alertas_phishing": alertas_phishing,
            "estado_seguridad": estado_seguridad,
            "nivel_alerta": nivel_alerta
        }

    def extraer_correos(self, texto):
        correos = re.findall(self.patron_correo, texto)
        return sorted(list(set(correos)))

    def analizar_ips(self, texto):
        encontradas_v4 = re.findall(self.patron_ipv4, texto)
        encontradas_v6 = re.findall(self.patron_ipv6, texto)

        todas_ips = list(set(encontradas_v4 + encontradas_v6))
        analisis = []

        for ip in todas_ips:
            try:
                obj_ip = ipaddress.ip_address(ip)

                if obj_ip.is_private:
                    tipo = "Privada (Red Local / VPN)"
                elif obj_ip.is_loopback:
                    tipo = "Loopback (Localhost)"
                elif obj_ip.is_reserved:
                    tipo = "Reservada"
                else:
                    tipo = "Publica"

                analisis.append({
                    "ip": ip,
                    "version": obj_ip.version,
                    "tipo": tipo,
                    "valida": True
                })
            except ValueError:
                analisis.append({
                    "ip": ip,
                    "version": None,
                    "tipo": "Invalida",
                    "valida": False
                })

        return analisis

    def analizar_enlaces(self, texto):
        urls = list(set(re.findall(self.patron_url, texto)))
        analisis = []

        for url in urls:
            try:
                parsed_url = urlparse(url)
                dominio = parsed_url.netloc.lower()
                ruta = parsed_url.path.lower()
                query = parsed_url.query.lower()

                es_sospechoso = False
                coincidencias = []

                for kw in self.keywords_sospechosas:
                    if kw in dominio or kw in ruta or kw in query:
                        es_sospechoso = True
                        coincidencias.append(kw)

                # Detectar si el enlace usa una direccion IP directa en lugar de dominio
                host_sin_puerto = dominio.split(":")[0]
                if re.fullmatch(self.patron_ipv4, host_sin_puerto):
                    es_sospechoso = True
                    coincidencias.append("ip_en_url")

                # Enlace sin HTTPS que contiene palabras sensibles
                if parsed_url.scheme == "http" and coincidencias:
                    coincidencias.append("sin_https")

                analisis.append({
                    "url": url,
                    "esquema": parsed_url.scheme,
                    "dominio": dominio,
                    "sospechoso": es_sospechoso,
                    "indicadores": sorted(list(set(coincidencias)))
                })
            except Exception:
                analisis.append({
                    "url": url,
                    "esquema": "desconocido",
                    "dominio": "error_parsing",
                    "sospechoso": True,
                    "indicadores": ["parse_error"]
                })

        return analisis