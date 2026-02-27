# Gestión Humana

Sistema de gestión de recursos humanos con Python Flask y MySQL.

## Requisitos

- Python 3.10+
- MySQL Server (MySQL Workbench)

## Instalación

1. **Crear entorno virtual:**

```bash
python -m venv venv
venv\Scripts\activate
```

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

3. **Crear la base de datos en MySQL Workbench:**

Abre MySQL Workbench y ejecuta:

```sql
CREATE DATABASE IF NOT EXISTS gestio_humana;
```

4. **Configurar variables de entorno:**

Edita el archivo `.env` con tus credenciales de MySQL:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DATABASE=gestio_humana
```

5. **Ejecutar la aplicación:**

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000
