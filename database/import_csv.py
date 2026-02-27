"""
Importa los datos de los CSV (DBase, Retirados, Hijos) a MySQL.
Ejecutar después de correr schema.sql en MySQL Workbench.

Uso:
    python database/import_csv.py
"""

import csv
import os
import sys
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

CSV_DIR = r"C:\Users\johan\Downloads"

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "gh_admin"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "gestio_humana"),
}

FILES = {
    "dbase": os.path.join(CSV_DIR, "BDatos_APPGH - DBase.csv"),
    "retirados": os.path.join(CSV_DIR, "BDatos_APPGH - Retirados.csv"),
    "hijos": os.path.join(CSV_DIR, "BDatos_APPGH - Hijos.csv"),
}


def read_csv(filepath):
    rows = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def clean(val):
    if val is None:
        return None
    val = val.strip()
    return val if val else None


def import_empleados(cursor):
    rows = read_csv(FILES["dbase"])
    sql = """
        INSERT IGNORE INTO empleado (
            id_cedula, apellidos_nombre, lugar_expedicion, fecha_expedicion,
            departamento, area, id_perfil_ocupacional, fecha_ingreso,
            sexo, rh, direccion_residencia, barrio_residencia,
            ciudad_residencia, telefono, celular, direccion_email,
            eps, fondo_pensiones, fecha_nacimiento, hijos, estado,
            tipo_documento, nivel_educativo, profesion,
            contacto_emergencia, telefono_contacto, parentezco
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
    """
    count = 0
    for row in rows:
        values = (
            clean(row.get("ID_Cedula")),
            clean(row.get("Apellidos_Nombre")),
            clean(row.get("Lugar_Expedicion")),
            clean(row.get("Fecha_Expedicion")),
            clean(row.get("Departamento")),
            clean(row.get("Area")),
            clean(row.get("ID_Perfil_Ocupacional")),
            clean(row.get("Fecha_Ingreso")),
            clean(row.get("Sexo")),
            clean(row.get("Rh")),
            clean(row.get("Direccion_Residencia")),
            clean(row.get("Barrio_Residencia")),
            clean(row.get("Ciudad_Residencia")),
            clean(row.get("Telefono")),
            clean(row.get("Celular")),
            clean(row.get("Direccion_Email")),
            clean(row.get("EPS")),
            clean(row.get("Fondo_Pensiones")),
            clean(row.get("Fecha_Nacimiento")),
            clean(row.get("Hijos")),
            clean(row.get("Estado")),
            clean(row.get("Tipo_Documento")),
            clean(row.get("Nivel_Educativo")),
            clean(row.get("Profesion")),
            clean(row.get("contactoEmergencia")),
            clean(row.get("TelefonoContacto")),
            clean(row.get("parentezco")),
        )
        if values[0]:
            cursor.execute(sql, values)
            count += 1
    return count


def import_retirados(cursor):
    rows = read_csv(FILES["retirados"])
    sql = """
        INSERT IGNORE INTO retirado (
            id_retiro, id_cedula, apellidos_nombre, departamento, area,
            id_perfil_ocupacional, fecha_ingreso, fecha_retiro,
            dias_laborados, tipo_retiro, motivo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    count = 0
    for row in rows:
        dias = clean(row.get("Dias_Laborados"))
        try:
            dias = int(dias) if dias else None
        except ValueError:
            dias = None

        values = (
            clean(row.get("ID_Retiro")),
            clean(row.get("ID_Cedula")),
            clean(row.get("Apellidos_Nombre")),
            clean(row.get("Departamento")),
            clean(row.get("Area")),
            clean(row.get("ID_Perfil_Ocupacional")),
            clean(row.get("Fecha_Ingreso")),
            clean(row.get("Fecha_Retiro")),
            dias,
            clean(row.get("Tipo_Retiro")),
            clean(row.get("Motivo")),
        )
        if values[0]:
            cursor.execute(sql, values)
            count += 1
    return count


def import_hijos(cursor):
    rows = read_csv(FILES["hijos"])
    sql = """
        INSERT IGNORE INTO hijo (
            id_hijo, identificacion_hijo, id_cedula,
            apellidos_nombre, fecha_nacimiento, sexo, estado
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    count = 0
    for row in rows:
        values = (
            clean(row.get("ID_Hijo")),
            clean(row.get("Identificacion_Hijo")),
            clean(row.get("ID_Cedula")),
            clean(row.get("Apellidos_Nombre")),
            clean(row.get("Fecha_Nacimiento")),
            clean(row.get("Sexo")),
            clean(row.get("Estado")),
        )
        if values[0]:
            cursor.execute(sql, values)
            count += 1
    return count


def main():
    print("Conectando a MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Conexion exitosa.\n")

        print("Importando empleados (DBase)...")
        n = import_empleados(cursor)
        conn.commit()
        print(f"  -> {n} empleados importados.")

        print("Importando retirados...")
        n = import_retirados(cursor)
        conn.commit()
        print(f"  -> {n} retirados importados.")

        print("Importando hijos...")
        n = import_hijos(cursor)
        conn.commit()
        print(f"  -> {n} hijos importados.")

        print("\nImportacion completada con exito.")
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Error de MySQL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
