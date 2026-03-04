import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "gestio_humana")

    # SMTP (permisos: notificar a GH y al empleado). Colbeef: mail.colbeef.com.co:465 SSL
    MAIL_ENABLED = os.getenv("MAIL_ENABLED", "0") == "1"
    MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"  # True si puerto 465 (se detecta también por puerto)
    MAIL_USER = os.getenv("MAIL_USER", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "")
    # Quién recibe la notificación "Nueva solicitud" (los dos reciben el mismo correo).
    # Coordinación GH = quien APRUEBA o rechaza. Contratación = quien le dice al empleado "llene acá" el formato.
    MAIL_GH_PERMISOS = os.getenv("MAIL_GH_PERMISOS", "coordinacion.gestionhumana@colbeef.com")
    MAIL_GESTOR_CONTRATACION = os.getenv("MAIL_GESTOR_CONTRATACION", "gestor.contratacion@colbeef.com")
    # Pruebas: dejar vacío o poner un correo extra que reciba copia en cada envío.
    MAIL_PRUEBAS_CC = os.getenv("MAIL_PRUEBAS_CC", "")
    # Único correo que puede tener el rol ADMIN (seguridad).
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "tecnologia@colbeef.com").strip().lower()
