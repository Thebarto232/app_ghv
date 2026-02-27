"""
Establece contraseñas iniciales para los usuarios existentes.
Ejecutar después de migration_auth.sql.

Uso:
    python database/seed_passwords.py
"""

import os
import sys
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "gh_admin"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "gestio_humana"),
}

DEFAULT_PASSWORD = "Colbeef2026*"


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_user, email, nombre FROM usuario")
    users = cursor.fetchall()

    if not users:
        print("No se encontraron usuarios en la tabla.")
        sys.exit(1)

    hashed = generate_password_hash(DEFAULT_PASSWORD)

    for u in users:
        cursor.execute(
            "UPDATE usuario SET password_hash = %s WHERE id_user = %s",
            (hashed, u["id_user"]),
        )
        print(f"  {u['id_user']} ({u['email']}) -> password establecida")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n{len(users)} usuarios actualizados con contraseña: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    main()
