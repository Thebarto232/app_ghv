"""
Update the gestio_humana database from the master Excel file.
Truncates and re-imports all tables to ensure data is in sync.
"""
import os
import sys
from datetime import datetime, date
import openpyxl
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

XLSX_PATH = r"c:\Users\johan\Downloads\BDatos_APPGH (1).xlsx"

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "gh_admin"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "gestio_humana"),
}


def read_sheet(wb, sheet_name):
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    data = []
    for row in rows[1:]:
        if any(v is not None for v in row):
            data.append(dict(zip(headers, row)))
    return headers, data


def clean_str(val, max_len=None):
    if val is None:
        return None
    s = str(val).strip()
    if s in ('', 'None', 'nan'):
        return None
    if max_len:
        s = s[:max_len]
    return s


def clean_int(val):
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def clean_date_str(val):
    """Convert datetime/date/string to 'M/D/YYYY' string for VARCHAR storage."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return f"{val.month}/{val.day}/{val.year}"
    if isinstance(val, date):
        return f"{val.month}/{val.day}/{val.year}"
    s = str(val).strip()
    if not s or s in ('None', 'nan'):
        return None
    return s


def import_lookup_tables(cursor, wb):
    """Import small lookup tables: rol, tipo_documento, nivel_educativo, profesion,
    eps, fondo_pensiones, motivo_retiro, departamento."""

    # Rol
    _, data = read_sheet(wb, 'Rol')
    cursor.execute("DELETE FROM rol")
    for r in data:
        val = clean_str(r.get('Rol'))
        if val:
            cursor.execute("INSERT IGNORE INTO rol (nombre) VALUES (%s)", (val,))
    print(f"  rol: {len(data)} rows")

    # Tipo Documento
    _, data = read_sheet(wb, 'Tipo_Documento')
    cursor.execute("DELETE FROM tipo_documento")
    for r in data:
        tid = clean_str(r.get('id_tipodocuemnto'))
        nombre = clean_str(r.get('tipo_documento'))
        if tid and nombre:
            cursor.execute(
                "INSERT IGNORE INTO tipo_documento (id_tipo_documento, tipo_documento) VALUES (%s, %s)",
                (tid, nombre)
            )
    print(f"  tipo_documento: {len(data)} rows")

    # Nivel Educativo
    _, data = read_sheet(wb, 'Nivel_educativo')
    cursor.execute("DELETE FROM nivel_educativo")
    for r in data:
        nid = clean_str(r.get('id_nivel'))
        nombre = clean_str(r.get('Nivel'))
        if nid and nombre:
            cursor.execute(
                "INSERT IGNORE INTO nivel_educativo (id_nivel, nivel) VALUES (%s, %s)",
                (nid, nombre)
            )
    print(f"  nivel_educativo: {len(data)} rows")

    # Profesion
    _, data = read_sheet(wb, 'Profesion')
    cursor.execute("DELETE FROM profesion")
    for r in data:
        pid = clean_str(r.get('id_profesion'))
        nombre = clean_str(r.get('Profesion'))
        if pid and nombre:
            cursor.execute(
                "INSERT IGNORE INTO profesion (id_profesion, profesion) VALUES (%s, %s)",
                (pid, nombre)
            )
    print(f"  profesion: {len(data)} rows")

    # EPS
    _, data = read_sheet(wb, 'EPS')
    cursor.execute("DELETE FROM eps")
    for r in data:
        val = clean_str(r.get('EPS'))
        if val:
            cursor.execute("INSERT IGNORE INTO eps (nombre) VALUES (%s)", (val,))
    print(f"  eps: {len(data)} rows")

    # Fondo Pensiones
    _, data = read_sheet(wb, 'FondoPensiones')
    cursor.execute("DELETE FROM fondo_pensiones")
    for r in data:
        val = clean_str(r.get('Fondo_Pensiones'))
        if val:
            cursor.execute("INSERT IGNORE INTO fondo_pensiones (nombre) VALUES (%s)", (val,))
    print(f"  fondo_pensiones: {len(data)} rows")

    # Motivos Retiros
    _, data = read_sheet(wb, 'Motivos_Retiros')
    cursor.execute("DELETE FROM motivo_retiro")
    for r in data:
        val = clean_str(r.get('Tipo_Retiro'))
        if val:
            cursor.execute("INSERT IGNORE INTO motivo_retiro (tipo_retiro) VALUES (%s)", (val,))
    print(f"  motivo_retiro: {len(data)} rows")

    # Departamento
    _, data = read_sheet(wb, 'Departamento')
    cursor.execute("DELETE FROM perfil_ocupacional")
    cursor.execute("DELETE FROM area")
    cursor.execute("DELETE FROM departamento")
    for r in data:
        nombre = clean_str(r.get('Departamento'))
        pres = clean_int(r.get('Presupuestados'))
        if nombre:
            cursor.execute(
                "INSERT INTO departamento (nombre, presupuestados) VALUES (%s, %s)",
                (nombre, pres)
            )
    print(f"  departamento: {len(data)} rows")


def import_areas(cursor, wb):
    _, data = read_sheet(wb, 'Area')
    for r in data:
        depto = clean_str(r.get('Departamento'))
        area = clean_str(r.get('Area'))
        pres = clean_int(r.get('Presupuestados'))
        if not depto or not area:
            continue
        cursor.execute("SELECT id FROM departamento WHERE nombre = %s", (depto,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO departamento (nombre) VALUES (%s)", (depto,))
            depto_id = cursor.lastrowid
        else:
            depto_id = row[0]
        cursor.execute(
            "INSERT INTO area (departamento_id, nombre, presupuestados) VALUES (%s, %s, %s)",
            (depto_id, area, pres)
        )
    print(f"  area: {len(data)} rows")


def import_perfiles(cursor, wb):
    _, data = read_sheet(wb, 'Perfil_Ocupacional')
    for r in data:
        area_name = clean_str(r.get('Area'))
        pid = clean_str(r.get('ID_Perfil_Ocupacional'))
        perfil = clean_str(r.get('Perfil_Ocupacional'))
        pres = clean_int(r.get('Presupuestados'))
        if not area_name or not pid:
            continue
        cursor.execute("SELECT id FROM area WHERE nombre = %s", (area_name,))
        row = cursor.fetchone()
        if not row:
            continue
        area_id = row[0]
        cursor.execute(
            "INSERT IGNORE INTO perfil_ocupacional (id_perfil, area_id, perfil_ocupacional, presupuestados) "
            "VALUES (%s, %s, %s, %s)",
            (pid, area_id, perfil or pid, pres)
        )
    print(f"  perfil_ocupacional: {len(data)} rows")


def import_empleados(cursor, wb):
    _, data = read_sheet(wb, 'DBase')
    cursor.execute("DELETE FROM hijo")
    cursor.execute("DELETE FROM empleado")
    count = 0
    for r in data:
        cedula = clean_str(r.get('ID_Cedula'))
        if not cedula:
            continue
        try:
            cedula = str(int(float(cedula)))
        except (ValueError, TypeError):
            pass
        values = (
            cedula,
            clean_str(r.get('Apellidos_Nombre'), 200),
            clean_str(r.get('Lugar_Expedicion'), 150),
            clean_date_str(r.get('Fecha_Expedicion')),
            clean_str(r.get('Departamento'), 100),
            clean_str(r.get('Area'), 100),
            clean_str(r.get('ID_Perfil_Ocupacional'), 50),
            clean_date_str(r.get('Fecha_Ingreso')),
            clean_str(r.get('Sexo'), 1),
            clean_str(r.get('Rh'), 5),
            clean_str(r.get('Direccion_Residencia'), 250),
            clean_str(r.get('Barrio_Residencia'), 100),
            clean_str(r.get('Ciudad_Residencia'), 100),
            clean_str(r.get('Telefono'), 30),
            clean_str(r.get('Celular'), 30),
            clean_str(r.get('Direccion_Email'), 200),
            clean_str(r.get('EPS'), 100),
            clean_str(r.get('Fondo_Pensiones'), 100),
            clean_date_str(r.get('Fecha_Nacimiento')),
            clean_str(r.get('Hijos'), 5),
            clean_str(r.get('Estado'), 20) or 'ACTIVO',
            clean_str(r.get('Tipo_Documento'), 50),
            clean_str(r.get('Nivel_Educativo'), 50),
            clean_str(r.get('Profesion'), 100),
            clean_str(r.get('contactoEmergencia'), 200),
            clean_str(r.get('TelefonoContacto'), 30),
            clean_str(r.get('parentezco'), 100),
        )
        cursor.execute(
            "INSERT IGNORE INTO empleado ("
            "id_cedula, apellidos_nombre, lugar_expedicion, fecha_expedicion, "
            "departamento, area, id_perfil_ocupacional, fecha_ingreso, "
            "sexo, rh, direccion_residencia, barrio_residencia, "
            "ciudad_residencia, telefono, celular, direccion_email, "
            "eps, fondo_pensiones, fecha_nacimiento, hijos, estado, "
            "tipo_documento, nivel_educativo, profesion, "
            "contacto_emergencia, telefono_contacto, parentezco"
            ") VALUES ("
            "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            "%s,%s,%s,%s,%s,%s,%s)",
            values,
        )
        count += 1
    print(f"  empleado: {count} rows")


def import_retirados(cursor, wb):
    _, data = read_sheet(wb, 'Retirados')
    cursor.execute("DELETE FROM retirado")
    count = 0
    for r in data:
        rid = clean_str(r.get('ID_Retiro'))
        cedula = clean_str(r.get('ID_Cedula'))
        if not rid or not cedula:
            continue
        try:
            cedula = str(int(float(cedula)))
        except (ValueError, TypeError):
            pass
        dias = clean_int(r.get('Dias_Laborados'))
        cursor.execute(
            "INSERT IGNORE INTO retirado ("
            "id_retiro, id_cedula, apellidos_nombre, departamento, area, "
            "id_perfil_ocupacional, fecha_ingreso, fecha_retiro, "
            "dias_laborados, tipo_retiro, motivo"
            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                rid,
                cedula,
                clean_str(r.get('Apellidos_Nombre'), 200),
                clean_str(r.get('Departamento'), 100),
                clean_str(r.get('Area'), 100),
                clean_str(r.get('ID_Perfil_Ocupacional'), 50),
                clean_date_str(r.get('Fecha_Ingreso')),
                clean_date_str(r.get('Fecha_Retiro')),
                dias,
                clean_str(r.get('Tipo_Retiro'), 100),
                clean_str(r.get('Motivo')),
            ),
        )
        count += 1
    print(f"  retirado: {count} rows")


def import_hijos(cursor, wb):
    _, data = read_sheet(wb, 'Hijos')
    count = 0
    for r in data:
        hid = clean_str(r.get('ID_Hijo'))
        cedula = clean_str(r.get('ID_Cedula'))
        if not hid or not cedula:
            continue
        try:
            cedula = str(int(float(cedula)))
        except (ValueError, TypeError):
            pass
        ident = clean_str(r.get('Identificacion_Hijo'))
        if ident:
            try:
                ident = str(int(float(ident)))
            except (ValueError, TypeError):
                pass
        cursor.execute(
            "INSERT IGNORE INTO hijo ("
            "id_hijo, identificacion_hijo, id_cedula, apellidos_nombre, "
            "fecha_nacimiento, sexo, estado"
            ") VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                hid,
                ident,
                cedula,
                clean_str(r.get('Apellidos_Nombre'), 200),
                clean_date_str(r.get('Fecha_Nacimiento')),
                clean_str(r.get('Sexo'), 1),
                clean_str(r.get('Estado'), 20),
            ),
        )
        count += 1
    print(f"  hijo: {count} rows")


def import_usuarios(cursor, wb):
    _, data = read_sheet(wb, 'User')
    for r in data:
        uid = clean_str(r.get('ID_User'))
        email = clean_str(r.get('Email'))
        nombre = clean_str(r.get('Nombre'))
        rol = clean_str(r.get('Rol'))
        estado = r.get('Estado')
        if isinstance(estado, bool):
            estado = 1 if estado else 0
        else:
            estado = 1 if str(estado).upper() in ('TRUE', '1', 'SI') else 0
        acciones = clean_str(r.get('Acciones'))
        if not uid or not email:
            continue
        cursor.execute(
            "INSERT INTO usuario (id_user, email, nombre, rol, estado, acciones) "
            "VALUES (%s,%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE email=%s, nombre=%s, rol=%s, estado=%s, acciones=%s",
            (uid, email, nombre, rol, estado, acciones,
             email, nombre, rol, estado, acciones),
        )
    print(f"  usuario: {len(data)} rows (upserted)")


def main():
    print(f"Opening: {XLSX_PATH}")
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)

    print("Connecting to database...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    try:
        print("\n1. Importing lookup tables...")
        import_lookup_tables(cursor, wb)

        print("\n2. Importing areas...")
        import_areas(cursor, wb)

        print("\n3. Importing perfiles ocupacionales...")
        import_perfiles(cursor, wb)

        print("\n4. Importing empleados...")
        import_empleados(cursor, wb)

        print("\n5. Importing retirados...")
        import_retirados(cursor, wb)

        print("\n6. Importing hijos...")
        import_hijos(cursor, wb)

        print("\n7. Updating usuarios...")
        import_usuarios(cursor, wb)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("\n=== Database update complete! ===")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        wb.close()


if __name__ == "__main__":
    main()
