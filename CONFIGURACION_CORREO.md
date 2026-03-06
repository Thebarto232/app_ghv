# Configuración de correo (Gmail / Colbeef) – Gestión Humana

Todo el tema de envío de correos y adjuntos está resuelto en el código. Solo hay que configurar las variables en `.env`.

---

## 1. Activar el envío

En tu archivo `.env`:

```env
MAIL_ENABLED=1
```

Si está en `0` o no existe, **no se envía ningún correo** (las solicitudes se guardan igual).

---

## 2. Servidor SMTP

### Opción A: Gmail

- **MAIL_HOST=smtp.gmail.com**
- **MAIL_PORT=587** (o 465 con SSL)
- **MAIL_USE_SSL=0** para 587, o **MAIL_USE_SSL=1** para 465
- **MAIL_USER** = tu correo (ej: `gestiónhumana@colbeef.com`)
- **MAIL_PASSWORD** = **Contraseña de aplicación** (App Password), **no** la contraseña normal de Gmail.

Para obtener la contraseña de aplicación en Gmail:

1. Cuenta de Google → Seguridad → Verificación en dos pasos (activada).
2. Seguridad → Contraseñas de aplicaciones → Generar una para “Correo” / “Otro (gestio_humana)”.
3. Copiar la contraseña de 16 caracteres y ponerla en **MAIL_PASSWORD** en `.env`.

**MAIL_FROM** puede ser el mismo que **MAIL_USER** o el correo que quieras que aparezca como remitente.

### Opción B: Servidor Colbeef (mail.colbeef.com.co)

- **MAIL_HOST=mail.colbeef.com.co**
- **MAIL_PORT=465**
- **MAIL_USE_SSL=1**
- **MAIL_USER** y **MAIL_PASSWORD** los que te dé sistemas/Colbeef.
- **MAIL_FROM** normalmente igual que **MAIL_USER**.

---

## 3. Quién recibe las notificaciones

- **MAIL_GH_PERMISOS**: correo de Coordinación Gestión Humana (quien aprueba o rechaza permisos).
- **MAIL_GESTOR_CONTRATACION**: correo del Gestor de Contratación (se le informa que el empleado diligenció el formato).

En **solicitud de permiso** (y permiso no remunerado con evidencia):

- A ambos se les envía el mismo correo con el detalle de la solicitud.
- Si el empleado adjuntó **evidencia** (permiso no remunerado), ese archivo va **adjunto al correo** (PDF o imagen) para ambos.

---

## 4. Adjuntos (evidencia) – ya está cuadrado

- El empleado sube la evidencia en el formulario (permiso **no remunerado**).
- El archivo se guarda en el servidor y su ruta en la base de datos.
- Al enviar la notificación a Coordinación GH y al Gestor de Contratación, **ese archivo se adjunta al correo** automáticamente.
- No hace falta configurar nada más para que Gmail (o Colbeef) reciba el adjunto; el código usa MIME estándar y base64.

---

## 5. Resumen de variables en `.env`

| Variable | Descripción |
|----------|-------------|
| **MAIL_ENABLED** | 1 = enviar correos, 0 = no enviar |
| **MAIL_HOST** | smtp.gmail.com o mail.colbeef.com.co |
| **MAIL_PORT** | 587 (TLS) o 465 (SSL) |
| **MAIL_USE_SSL** | 1 si usas 465, 0 si usas 587 |
| **MAIL_USER** | Cuenta que envía (login SMTP) |
| **MAIL_PASSWORD** | Contraseña o App Password (Gmail) |
| **MAIL_FROM** | Correo que aparece como “De” (puede ser = MAIL_USER) |
| **MAIL_GH_PERMISOS** | Correo de Coordinación GH |
| **MAIL_GESTOR_CONTRATACION** | Correo del Gestor de Contratación |
| **MAIL_PRUEBAS_CC** | (Opcional) Correo que recibe copia en cada envío; útil para pruebas |

Con esto el tema de Gmail (y correo en general) queda cuadrado de una vez: activar envío, configurar SMTP y destinatarios; los adjuntos de evidencia se envían solos.
