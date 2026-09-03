"""
=========================================================
memoria_sql.py

Sistema de almacenamiento historico (Boveda SQLite).
Registra metadatos de auditorias, analisis e historial
de entidades (IPs, correos, enlaces) para cruces de datos.
=========================================================
"""

import sqlite3
from datetime import datetime

class BovedaSQL:
    def __init__(self, db_name="memoria_nexluk.db"):
        self.db_name = db_name
        self._inicializar_tablas()

    # =========================================================
    # CONEXION Y CONFIGURACION INICIAL
    # =========================================================

    def _conectar(self):
        return sqlite3.connect(self.db_name)

    def _inicializar_tablas(self):
        conexion = self._conectar()
        cursor = conexion.cursor()
        
        # Tabla principal de auditorias y analisis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                archivo TEXT,
                modo TEXT,
                analisis_completo TEXT
            )
        ''')
        
        # Tabla secundaria para entidades extraidas (IPs, correos, URLs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auditoria_id INTEGER,
                tipo_entidad TEXT,
                valor TEXT,
                FOREIGN KEY(auditoria_id) REFERENCES auditorias(id)
            )
        ''')
        
        conexion.commit()
        conexion.close()

    # =========================================================
    # METODOS DE ESCRITURA
    # =========================================================

    def guardar_registro(self, archivo, modo, analisis_completo):
        """
        Guarda el reporte principal de la auditoria o analisis
        y devuelve el ID asignado en la base de datos.
        """
        conexion = self._conectar()
        cursor = conexion.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO auditorias (fecha, archivo, modo, analisis_completo)
            VALUES (?, ?, ?, ?)
        ''', (fecha_actual, archivo, modo, analisis_completo))
        
        auditoria_id = cursor.lastrowid
        
        conexion.commit()
        conexion.close()
        
        return auditoria_id

    def guardar_entidades(self, auditoria_id, datos_escudo):
        """
        Toma el diccionario generado por el Escudo (IPs, correos, enlaces)
        y los almacena asociados a la auditoria correspondiente.
        """
        conexion = self._conectar()
        cursor = conexion.cursor()

        try:
            # Guardar correos
            for correo in datos_escudo.get("correos", []):
                cursor.execute('''
                    INSERT INTO entidades (auditoria_id, tipo_entidad, valor)
                    VALUES (?, ?, ?)
                ''', (auditoria_id, "correo", str(correo)))

            # Guardar IPs
            for ip_info in datos_escudo.get("ips", []):
                cursor.execute('''
                    INSERT INTO entidades (auditoria_id, tipo_entidad, valor)
                    VALUES (?, ?, ?)
                ''', (auditoria_id, "ip", str(ip_info.get("ip"))))

            # Guardar Enlaces
            for enlace_info in datos_escudo.get("enlaces", []):
                cursor.execute('''
                    INSERT INTO entidades (auditoria_id, tipo_entidad, valor)
                    VALUES (?, ?, ?)
                ''', (auditoria_id, "url", str(enlace_info.get("url"))))

            conexion.commit()
        except Exception as e:
            print(f"Error al guardar entidades en la boveda: {e}")
        finally:
            conexion.close()

    # =========================================================
    # METODOS DE CONSULTA
    # =========================================================

    def obtener_historial(self):
        """Devuelve un resumen de todas las auditorias realizadas."""
        conexion = self._conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, fecha, archivo, modo FROM auditorias ORDER BY id DESC")
        registros = cursor.fetchall()
        conexion.close()
        return registros