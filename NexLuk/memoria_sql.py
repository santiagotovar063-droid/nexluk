"""
memoria_sql.py

Sistema de almacenamiento historico (Boveda SQLite) en carpeta dedicada.
Registra auditorias, entidades del Escudo y hallazgos importantes
detectados por la IA para consultas y cruces de datos.
"""

import os
import sqlite3
from datetime import datetime


class BovedaSQL:
    def __init__(self, carpeta_datos=None, db_name="memoria_nexluk.db"):
        # Si existe una ruta configurada en el servidor (ej. Render Disk o servidor local), la usa.
        # Si no, crea una carpeta real llamada "boveda_datos" dentro del proyecto.
        base_dir = carpeta_datos or os.getenv("NEXLUK_DATA_DIR", "boveda_datos")
        self.carpeta_datos = os.path.abspath(base_dir)
        os.makedirs(self.carpeta_datos, exist_ok=True)

        self.db_path = os.path.join(self.carpeta_datos, db_name)
        self._inicializar_tablas()

    # CONEXION Y CONFIGURACION INICIAL

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _inicializar_tablas(self):
        conexion = self._conectar()
        cursor = conexion.cursor()

        # 1. Tabla principal de auditorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                archivo TEXT,
                modo TEXT,
                resumen_ejecutivo TEXT,
                nivel_riesgo TEXT,
                analisis_completo TEXT
            )
        ''')

        # 2. Tabla para entidades tecnicas extraidas por el Escudo (IPs, correos, URLs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auditoria_id INTEGER,
                tipo_entidad TEXT,
                valor TEXT,
                FOREIGN KEY(auditoria_id) REFERENCES auditorias(id)
            )
        ''')

        # 3. NUEVA: Tabla para datos importantes encontrados por la IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hallazgos_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auditoria_id INTEGER,
                categoria TEXT,
                importancia TEXT,
                detalle TEXT,
                fecha_registro TEXT,
                FOREIGN KEY(auditoria_id) REFERENCES auditorias(id)
            )
        ''')

        conexion.commit()
        conexion.close()

    # METODOS DE ESCRITURA

    def guardar_registro(self, archivo, modo, analisis_completo, resumen_ejecutivo="", nivel_riesgo="Medio"):
        """
        Guarda el reporte principal de la auditoria y devuelve su ID.
        """
        conexion = self._conectar()
        cursor = conexion.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO auditorias (fecha, archivo, modo, resumen_ejecutivo, nivel_riesgo, analisis_completo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha_actual, archivo, modo, resumen_ejecutivo, nivel_riesgo, analisis_completo))

        auditoria_id = cursor.lastrowid
        conexion.commit()
        conexion.close()

        return auditoria_id

    def guardar_entidades(self, auditoria_id, datos_escudo):
        """
        Guarda IPs, correos y enlaces detectados por el Escudo.
        """
        conexion = self._conectar()
        cursor = conexion.cursor()

        try:
            for correo in datos_escudo.get("correos", []):
                cursor.execute(
                    "INSERT INTO entidades (auditoria_id, tipo_entidad, valor) VALUES (?, ?, ?)",
                    (auditoria_id, "correo", str(correo))
                )

            for ip_info in datos_escudo.get("ips", []):
                cursor.execute(
                    "INSERT INTO entidades (auditoria_id, tipo_entidad, valor) VALUES (?, ?, ?)",
                    (auditoria_id, "ip", str(ip_info.get("ip")))
                )

            for enlace_info in datos_escudo.get("enlaces", []):
                cursor.execute(
                    "INSERT INTO entidades (auditoria_id, tipo_entidad, valor) VALUES (?, ?, ?)",
                    (auditoria_id, "url", str(enlace_info.get("url")))
                )

            conexion.commit()
        except Exception as e:
            print(f"Error al guardar entidades en la boveda: {e}")
        finally:
            conexion.close()

    def guardar_hallazgos_ia(self, auditoria_id, lista_hallazgos):
        """
        Guarda los datos importantes encontrados por la IA.
        Espera una lista de diccionarios con el formato:
        [
            {"categoria": "Clausula Critica", "importancia": "Alta", "detalle": "Penalizacion del 20% por retraso"},
            {"categoria": "Fecha Limite", "importancia": "Media", "detalle": "Vencimiento el 15 de diciembre de 2026"}
        ]
        """
        if not lista_hallazgos:
            return

        conexion = self._conectar()
        cursor = conexion.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            for item in lista_hallazgos:
                categoria = item.get("categoria", "General")
                importancia = item.get("importancia", "Media")
                detalle = item.get("detalle", "")

                if detalle.strip():
                    cursor.execute('''
                        INSERT INTO hallazgos_ia (auditoria_id, categoria, importancia, detalle, fecha_registro)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (auditoria_id, categoria, importancia, detalle.strip(), fecha_actual))

            conexion.commit()
        except Exception as e:
            print(f"Error al guardar hallazgos de la IA: {e}")
        finally:
            conexion.close()

    # METODOS DE LECTURA Y BUSQUEDA

    def obtener_historial(self):
        """Devuelve un resumen de todas las auditorias realizadas."""
        conexion = self._conectar()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, fecha, archivo, modo, nivel_riesgo FROM auditorias ORDER BY id DESC"
        )
        registros = cursor.fetchall()
        conexion.close()
        return registros

    def obtener_hallazgos_importantes(self, auditoria_id=None, solo_alta=False):
        """
        Consulta los datos importantes guardados por la IA.
        Puede filtrar por una auditoria especifica o traer solo los de importancia Alta.
        """
        conexion = self._conectar()
        cursor = conexion.cursor()

        query = '''
            SELECT h.id, a.archivo, h.categoria, h.importancia, h.detalle, h.fecha_registro
            FROM hallazgos_ia h
            JOIN auditorias a ON h.auditoria_id = a.id
            WHERE 1=1
        '''
        params = []

        if auditoria_id is not None:
            query += " AND h.auditoria_id = ?"
            params.append(auditoria_id)

        if solo_alta:
            query += " AND LOWER(h.importancia) = 'alta'"

        query += " ORDER BY h.id DESC"

        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conexion.close()
        return resultados

    def buscar_en_hallazgos(self, palabra_clave):
        """Busca una palabra clave dentro de los datos importantes guardados por la IA."""
        conexion = self._conectar()
        cursor = conexion.cursor()
        patron = f"%{palabra_clave}%"

        cursor.execute('''
            SELECT a.archivo, h.categoria, h.importancia, h.detalle, h.fecha_registro
            FROM hallazgos_ia h
            JOIN auditorias a ON h.auditoria_id = a.id
            WHERE h.detalle LIKE ? OR h.categoria LIKE ?
            ORDER BY h.id DESC
        ''', (patron, patron))

        resultados = cursor.fetchall()
        conexion.close()
        return resultados