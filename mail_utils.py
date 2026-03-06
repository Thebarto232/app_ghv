# -*- coding: utf-8 -*-
"""Envío de correos para notificaciones de solicitud de permiso."""
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from html import escape as html_escape

# Colores y estilo para correos (Colbeef)
_MAIL_STYLE = """
<style>
  body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f4f0; }
  .mail-wrap { max-width: 560px; margin: 0 auto; padding: 24px 16px; }
  .mail-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.08); border: 1px solid #e5e7eb; }
  .mail-header { background: linear-gradient(135deg, #0b3518 0%, #2D9E3F 100%); color: #fff; padding: 20px 24px; }
  .mail-header h1 { margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }
  .mail-header p { margin: 6px 0 0; font-size: 13px; opacity: .95; }
  .mail-body { padding: 24px; color: #374151; line-height: 1.55; font-size: 15px; }
  .mail-body p { margin: 0 0 14px; }
  .mail-body p:last-of-type { margin-bottom: 0; }
  .mail-table { width: 100%; border-collapse: collapse; margin: 18px 0; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; }
  .mail-table th { background: #f9fafb; padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .5px; }
  .mail-table td { padding: 12px 16px; border-top: 1px solid #e5e7eb; font-size: 14px; }
  .mail-table tr:first-child td { border-top: none; }
  .mail-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
  .mail-badge.pendiente { background: #fef3c7; color: #b45309; }
  .mail-badge.aprobado { background: #d1fae5; color: #047857; }
  .mail-badge.rechazado { background: #fee2e2; color: #b91c1c; }
  .mail-footer { padding: 16px 24px; background: #f9fafb; border-top: 1px solid #e5e7eb; font-size: 13px; color: #6b7280; }
  .mail-footer strong { color: #111; }
  .mail-divider { height: 1px; background: #e5e7eb; margin: 20px 0; }
</style>
"""


def _wrap_html(content_body, title, subtitle=""):
    """Envolver el contenido en layout HTML con header Colbeef."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {_MAIL_STYLE}
</head>
<body>
  <div class="mail-wrap">
    <div class="mail-card">
      <div class="mail-header">
        <h1>Gestión Humana · Colbeef</h1>
        <p>{subtitle}</p>
      </div>
      <div class="mail-body">
        {content_body}
      </div>
      <div class="mail-footer">
        <strong>Colbeef</strong> — Sistema de Gestión Humana. Este correo es automático; no responder a esta dirección.
      </div>
    </div>
  </div>
</body>
</html>"""


def send_mail(to_emails, subject, body_html, body_text=None, cc=None, app=None, attachments=None):
    """
    Envía un correo vía SMTP.
    to_emails: lista de correos o un solo string.
    cc: lista opcional de CC (para pruebas).
    app: instancia Flask (usa app.config). Si no se pasa, no envía.
    attachments: lista opcional de (nombre_archivo, ruta_archivo) para adjuntar al correo.
    """
    if app is None:
        return False
    if not app.config.get("MAIL_ENABLED"):
        if app and hasattr(app, "logger"):
            app.logger.warning("[Permisos] SMTP no enviado: MAIL_ENABLED no está activo.")
        return False
    if not app.config.get("MAIL_USER"):
        if app and hasattr(app, "logger"):
            app.logger.warning("[Permisos] SMTP no enviado: MAIL_USER vacío.")
        return False
    if not app.config.get("MAIL_PASSWORD"):
        if app and hasattr(app, "logger"):
            app.logger.warning("[Permisos] SMTP no enviado: MAIL_PASSWORD vacío (configure .env para enviar correos).")
        return False
    to_list = [to_emails] if isinstance(to_emails, str) else list(to_emails)
    cc_list = cc or []
    if app.config.get("MAIL_PRUEBAS_CC"):
        cc_list = cc_list + [e.strip() for e in app.config["MAIL_PRUEBAS_CC"].split(",") if e.strip()]
    try:
        has_attachments = attachments and len(attachments) > 0
        msg = MIMEMultipart("mixed" if has_attachments else "alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr(("Gestión Humana Colbeef", app.config.get("MAIL_FROM") or app.config.get("MAIL_USER")))
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        if has_attachments:
            part_body = MIMEMultipart("alternative")
            part_body.attach(MIMEText(body_text or body_html, "plain", "utf-8"))
            part_body.attach(MIMEText(body_html, "html", "utf-8"))
            msg.attach(part_body)
            for nombre, ruta in attachments:
                if not ruta or not os.path.isfile(ruta):
                    continue
                with open(ruta, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment", filename=nombre)
                msg.attach(part)
        else:
            msg.attach(MIMEText(body_text or body_html, "plain", "utf-8"))
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        host = app.config.get("MAIL_HOST", "smtp.gmail.com")
        port = app.config.get("MAIL_PORT", 587)
        use_ssl = port == 465 or app.config.get("MAIL_USE_SSL", False)
        if use_ssl:
            with smtplib.SMTP_SSL(host, port) as s:
                s.login(app.config["MAIL_USER"], app.config["MAIL_PASSWORD"])
                s.sendmail(app.config.get("MAIL_FROM") or app.config["MAIL_USER"], to_list + cc_list, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as s:
                s.starttls()
                s.login(app.config["MAIL_USER"], app.config["MAIL_PASSWORD"])
                s.sendmail(app.config.get("MAIL_FROM") or app.config["MAIL_USER"], to_list + cc_list, msg.as_string())
        if app and hasattr(app, "logger"):
            app.logger.info(f"[Permisos] Correo enviado a {to_list}: {subject[:50]}...")
        return True
    except Exception as e:
        if app and hasattr(app, "logger"):
            app.logger.warning(f"[Permisos] Error al enviar correo a {to_list}: {e}")
        return False


def _tabla_detalle_solicitud(solicitud, empleado_nombre=None, incluir_empleado=True):
    """Genera tabla HTML con el detalle de la solicitud (contenido escapado)."""
    tipo = html_escape(str(solicitud.get("tipo", "Permiso")))
    desde = html_escape(str(solicitud.get("fecha_desde", "—")))
    hasta = html_escape(str(solicitud.get("fecha_hasta", "—")))
    motivo = html_escape(str(solicitud.get("motivo") or "—"))
    filas = []
    if incluir_empleado and empleado_nombre:
        filas.append(("<th>Empleado</th>", f"<td>{html_escape(empleado_nombre)}</td>"))
    filas.append(("<th>Tipo de permiso</th>", f"<td>{tipo}</td>"))
    filas.append(("<th>Fecha desde</th>", f"<td>{desde}</td>"))
    filas.append(("<th>Fecha hasta</th>", f"<td>{hasta}</td>"))
    filas.append(("<th>Motivo</th>", f"<td>{motivo}</td>"))
    rows_html = "".join(f"<tr>{th}{td}</tr>" for th, td in filas)
    return f'<table class="mail-table"><tbody>{rows_html}</tbody></table>'


def _strip_html(html):
    """Versión texto plano aproximada del HTML del cuerpo (solo contenido, sin layout)."""
    t = html.replace("</p>", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r" +", " ", t).replace("\n ", "\n").strip()
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def notificar_nueva_solicitud_permiso(app, solicitud, empleado_nombre, empleado_email, evidencia_path=None):
    """
    Notifica por separado:
    - coordinacion.gestionhumana@colbeef.com (MAIL_GH_PERMISOS): es quien APRUEBA o RECHAZA el permiso.
    - gestor.contratacion@colbeef.com (MAIL_GESTOR_CONTRATACION): se le informa que el empleado ya diligenció el formato.
    evidencia_path: ruta absoluta del archivo adjunto (permiso no remunerado); se incluye en el correo.
    """
    tabla = _tabla_detalle_solicitud(solicitud, empleado_nombre=empleado_nombre, incluir_empleado=True)
    ok = False
    attachments = []
    if evidencia_path and os.path.isfile(evidencia_path):
        attachments = [(os.path.basename(evidencia_path), evidencia_path)]

    nota_evidencia = "<p><strong>Se adjunta la evidencia</strong> enviada por el empleado (permiso no remunerado).</p>" if attachments else ""

    # Correo a Coordinación GH
    gh = (app.config.get("MAIL_GH_PERMISOS") or "").strip()
    if gh:
        subject_gh = f"Solicitud de permiso – {solicitud.get('fecha_desde', '')} – {empleado_nombre}"
        body_gh_content = f"""
        <p>Estimado/a Coordinación Gestión Humana,</p>
        <p>Se ha registrado una <strong>nueva solicitud de permiso</strong> en el sistema. Por favor revise los datos y resuelva la solicitud (aprobar o rechazar).</p>
        {tabla}
        {nota_evidencia}
        <div class="mail-divider"></div>
        <p><strong>Usted es quien aprueba o rechaza el permiso.</strong> Ingrese al sistema para resolver esta solicitud. Agradecemos una respuesta a la brevedad para confirmar que recibió esta notificación.</p>
        <p>Saludos cordiales,<br/><strong>Sistema de Gestión Humana – Colbeef</strong></p>
        """
        body_gh = _wrap_html(body_gh_content, title=subject_gh, subtitle="Nueva solicitud de permiso")
        plain_gh = _strip_html(body_gh_content)
        if send_mail(gh, subject_gh, body_gh, body_text=plain_gh, app=app, attachments=attachments):
            ok = True

    # Correo a Gestor de Contratación
    gestor = (app.config.get("MAIL_GESTOR_CONTRATACION") or "").strip()
    if gestor:
        subject_gestor = f"Formato de permiso diligenciado – {empleado_nombre}"
        body_gestor_content = f"""
        <p>Estimado/a Gestor de Contratación,</p>
        <p>El empleado <strong>{html_escape(empleado_nombre)}</strong> ya diligenció el formato de permiso en el sistema. A continuación el detalle de la solicitud:</p>
        {tabla}
        {nota_evidencia}
        <div class="mail-divider"></div>
        <p>Coordinación Gestión Humana es quien aprobará o rechazará esta solicitud. Si necesita más detalles, puede contactar al empleado o a Coordinación GH.</p>
        <p>Saludos cordiales,<br/><strong>Sistema de Gestión Humana – Colbeef</strong></p>
        """
        body_gestor = _wrap_html(body_gestor_content, title=subject_gestor, subtitle="Formato de permiso diligenciado")
        plain_gestor = _strip_html(body_gestor_content)
        if send_mail(gestor, subject_gestor, body_gestor, body_text=plain_gestor, app=app, attachments=attachments):
            ok = True

    if app and hasattr(app, "logger"):
        app.logger.info(f"[Permisos] Notificación nueva solicitud: GH={bool(gh)}, Gestor={bool(gestor)}, enviados_ok={ok}")
    return ok


def notificar_resolucion_permiso(app, solicitud, empleado_nombre, empleado_email, aprobado, observaciones=None):
    """Notifica al empleado que su solicitud fue aprobada o rechazada.
    El correo va al empleado (direccion_email en BD). Si está vacío, se usa el primer correo de MAIL_PRUEBAS_CC para pruebas."""
    original_email = (empleado_email or "").strip()
    if not original_email:
        empleado_email = app.config.get("MAIL_PRUEBAS_CC", "").split(",")[0].strip() or None
        if app and hasattr(app, "logger"):
            app.logger.info(f"[Permisos] Empleado {empleado_nombre} sin correo en BD; enviando a MAIL_PRUEBAS_CC={empleado_email or 'no configurado'}")
    else:
        empleado_email = original_email
    if not empleado_email:
        if app and hasattr(app, "logger"):
            app.logger.warning("[Permisos] No se envió correo de resolución: empleado sin direccion_email y MAIL_PRUEBAS_CC vacío")
        return False
    estado = "APROBADA" if aprobado else "RECHAZADA"
    estado_label = "Aprobada" if aprobado else "Rechazada"
    badge_class = "aprobado" if aprobado else "rechazado"
    subject = f"Resolución: permiso {estado_label} – {empleado_nombre}"
    tabla_filas = [
        ("<th>Tipo de permiso</th>", f"<td>{html_escape(str(solicitud.get('tipo', 'Permiso')))}</td>"),
        ("<th>Fecha desde</th>", f"<td>{html_escape(str(solicitud.get('fecha_desde', '—')))}</td>"),
        ("<th>Fecha hasta</th>", f"<td>{html_escape(str(solicitud.get('fecha_hasta', '—')))}</td>"),
    ]
    if observaciones:
        tabla_filas.append(("<th>Observaciones</th>", f"<td>{html_escape(observaciones)}</td>"))
    rows_html = "".join(f"<tr>{th}{td}</tr>" for th, td in tabla_filas)
    tabla = f'<table class="mail-table"><tbody>{rows_html}</tbody></table>'
    mensaje_estado = (
        "Su solicitud de permiso ha sido <strong>aprobada</strong>. Puede proceder según lo indicado en su solicitud."
        if aprobado
        else "Su solicitud de permiso no ha sido aprobada. Si tiene dudas o desea más información, puede contactar a Coordinación Gestión Humana."
    )
    nombre_safe = html_escape(empleado_nombre)
    body_content = f"""
    <p>Estimado/a <strong>{nombre_safe}</strong>,</p>
    <p>Coordinación Gestión Humana ha resuelto su solicitud de permiso/licencia.</p>
    <p><span class="mail-badge {badge_class}">{estado_label}</span></p>
    <p>{mensaje_estado}</p>
    {tabla}
    <div class="mail-divider"></div>
    <p>Saludos cordiales,<br/><strong>Gestión Humana – Colbeef</strong></p>
    """
    body = _wrap_html(body_content, title=subject, subtitle=f"Solicitud de permiso {estado_label}")
    plain = _strip_html(body_content)
    id_sol = solicitud.get("id")
    if app and hasattr(app, "logger"):
        app.logger.info(f"[Permisos] Resolución solicitud id={id_sol} → enviando a {empleado_email} ({estado})")
    ok = send_mail(empleado_email, subject, body, body_text=plain, app=app)
    if app and hasattr(app, "logger"):
        app.logger.info(f"[Permisos] Resolución id={id_sol} → resultado_enviado={ok}")
    return ok
