# -*- coding: utf-8 -*-
"""Envío de correos para notificaciones de solicitud de permiso."""
import os
import re
import smtplib
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.utils import formataddr
from html import escape as html_escape

try:
    from PIL import Image
except ImportError:
    Image = None

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
  .mail-signature { margin-top: 16px; padding-top: 10px; border-top: 1px solid #e5e7eb; }
  .mail-sign-name { font-family: 'Brush Script MT','Segoe Script','Segoe UI',cursive; font-size: 22px; color: #111827; }
  .mail-sign-role { font-size: 13px; color: #6b7280; }
  .mail-sign-company { font-size: 13px; color: #111827; font-weight: 600; }
  /* Informe formato GH-FR-007 (igual que el formulario) */
  .informe-doc { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; margin: 0; }
  .informe-header { display: table; width: 100%; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; background: #fafafa; }
  .informe-meta { font-size: 13px; }
  .informe-meta .celda-izq { font-weight: 600; color: #111; }
  .informe-meta .celda-der { color: #374151; }
  .informe-titulo { padding: 14px 20px 8px; font-size: 17px; font-weight: 700; color: #0b3518; }
  .informe-titulo-sub { padding: 0 20px 14px; font-size: 12px; color: #6b7280; }
  .informe-body { padding: 12px 20px 20px; }
  .informe-fila { margin-bottom: 12px; }
  .informe-label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .3px; margin-bottom: 2px; }
  .informe-valor { font-size: 14px; color: #111; padding: 6px 0; border-bottom: 1px solid #e5e7eb; }
  .informe-divider { height: 1px; background: #e5e7eb; margin: 20px 0 16px; }
  .informe-firmas { display: table; width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
  .informe-firma-celda { display: table-cell; padding: 14px 12px; text-align: center; border-right: 1px solid #e5e7eb; background: #fafafa; vertical-align: top; width: 33%; }
  .informe-firma-celda:last-child { border-right: none; }
  .informe-firma-celda .tit { font-size: 11px; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: .3px; margin-bottom: 8px; }
  .informe-firma-celda .sub { font-size: 12px; color: #4b5563; margin-top: 8px; line-height: 1.4; }
  .informe-firma-gh { background: #f0fdf4; }
  .informe-firma-gh .tit { color: #166534; }
  .informe-estado { display: inline-block; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 600; margin-bottom: 12px; }
  .informe-estado.aprobado { background: #d1fae5; color: #047857; }
</style>
"""


def _fecha_display(val):
    """Formatea fecha para mostrar en informe (DD-MM-YYYY)."""
    if val is None:
        return "—"
    if hasattr(val, "strftime"):
        return val.strftime("%d-%m-%Y")
    s = str(val).strip()
    if not s:
        return "—"
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return f"{s[8:10]}-{s[5:7]}-{s[0:4]}"
    return s


def _cargar_imagen_firma(ruta):
    """
    Carga la imagen de firma con Pillow y devuelve bytes PNG para embeber en el correo.
    La firma se muestra como imagen real (librería), no como HTML.
    """
    if not ruta or not os.path.isfile(ruta):
        return None
    if Image is not None:
        try:
            with Image.open(ruta) as img:
                img.load()
                buf = BytesIO()
                if img.mode in ("RGBA", "P"):
                    img.save(buf, "PNG")
                else:
                    img.convert("RGB").save(buf, "PNG")
                return buf.getvalue()
        except Exception:
            pass
    try:
        with open(ruta, "rb") as f:
            return f.read()
    except Exception:
        return None


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


def send_mail(to_emails, subject, body_html, body_text=None, cc=None, app=None, attachments=None, inline_images=None):
    """
    Envía un correo vía SMTP.
    to_emails: lista de correos o un solo string.
    cc: lista opcional de CC (para pruebas).
    app: instancia Flask (usa app.config). Si no se pasa, no envía.
    attachments: lista opcional de (nombre_archivo, ruta_archivo) para adjuntar al correo.
    inline_images: lista opcional de (cid, ruta_archivo) para imágenes que se muestran en el HTML con src="cid:xxx".
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
        has_inline = inline_images and len(inline_images) > 0
        msg = MIMEMultipart("mixed" if has_attachments else ("related" if has_inline else "alternative"))
        msg["Subject"] = subject
        msg["From"] = formataddr(("Gestión Humana Colbeef", app.config.get("MAIL_FROM") or app.config.get("MAIL_USER")))
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        if has_attachments:
            part_body = MIMEMultipart("alternative")
            part_body.attach(MIMEText(body_text or body_html, "plain", "utf-8"))
            if has_inline:
                part_related = MIMEMultipart("related")
                part_related.attach(MIMEText(body_html, "html", "utf-8"))
                for cid, ruta in inline_images:
                    payload = _cargar_imagen_firma(ruta) if isinstance(ruta, str) else None
                    if not payload:
                        continue
                    ext = os.path.splitext(ruta)[1].lower() if isinstance(ruta, str) else ".png"
                    subtype = "png" if ext == ".png" else "jpeg"
                    img_part = MIMEImage(payload, _subtype=subtype)
                    img_part.add_header("Content-Disposition", "inline", filename=os.path.basename(ruta) if isinstance(ruta, str) else "firma.png")
                    img_part.add_header("Content-ID", f"<{cid}>")
                    part_related.attach(img_part)
                part_body.attach(part_related)
            else:
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
        elif has_inline:
            msg.attach(MIMEText(body_text or body_html, "plain", "utf-8"))
            part_related = MIMEMultipart("related")
            part_related.attach(MIMEText(body_html, "html", "utf-8"))
            for cid, ruta in inline_images:
                payload = _cargar_imagen_firma(ruta) if isinstance(ruta, str) else None
                if not payload:
                    continue
                ext = os.path.splitext(ruta)[1].lower() if isinstance(ruta, str) else ".png"
                subtype = "png" if ext == ".png" else "jpeg"
                img_part = MIMEImage(payload, _subtype=subtype)
                img_part.add_header("Content-Disposition", "inline", filename=os.path.basename(ruta) if isinstance(ruta, str) else "firma.png")
                img_part.add_header("Content-ID", f"<{cid}>")
                part_related.attach(img_part)
            msg.attach(part_related)
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
    - gestionhumana@colbeef.com (MAIL_GH_INFORMADA): misma info, solo informativa; no aprueba ni rechaza.
    - gestor.contratacion@colbeef.com (MAIL_GESTOR_CONTRATACION): se le informa que el empleado ya diligenció el formato.
    evidencia_path: ruta absoluta del archivo adjunto (permiso no remunerado); se incluye en el correo.
    """
    tabla = _tabla_detalle_solicitud(solicitud, empleado_nombre=empleado_nombre, incluir_empleado=True)
    ok = False
    attachments = []
    if evidencia_path and os.path.isfile(evidencia_path):
        attachments = [(os.path.basename(evidencia_path), evidencia_path)]

    nota_evidencia = "<p><strong>Se adjunta la evidencia</strong> enviada por el empleado (permiso no remunerado).</p>" if attachments else ""

    # Correo a Coordinación GH (quien aprueba/rechaza)
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

    # Correo a GH Informada (solo informativa; coordinación es quien aprueba/rechaza)
    informada = (app.config.get("MAIL_GH_INFORMADA") or "").strip()
    if informada:
        subject_inf = f"Solicitud de permiso (informativo) – {solicitud.get('fecha_desde', '')} – {empleado_nombre}"
        body_inf_content = f"""
        <p>Estimado/a Gestión Humana,</p>
        <p>Se ha registrado una <strong>nueva solicitud de permiso</strong> en el sistema. A continuación el detalle:</p>
        {tabla}
        {nota_evidencia}
        <div class="mail-divider"></div>
        <p><strong>Este correo es solo informativo.</strong> Coordinación Gestión Humana es quien aprueba o rechaza las solicitudes. Usted puede ingresar al sistema para consultar el estado de los permisos.</p>
        <p>Saludos cordiales,<br/><strong>Sistema de Gestión Humana – Colbeef</strong></p>
        """
        body_inf = _wrap_html(body_inf_content, title=subject_inf, subtitle="Nueva solicitud de permiso (informativo)")
        plain_inf = _strip_html(body_inf_content)
        if send_mail(informada, subject_inf, body_inf, body_text=plain_inf, app=app, attachments=attachments):
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
        app.logger.info(f"[Permisos] Notificación nueva solicitud: GH={bool(gh)}, Informada={bool(informada)}, Gestor={bool(gestor)}, enviados_ok={ok}")
    return ok


def _body_informe_permiso_aprobado(solicitud, empleado_nombre, firma_img_html, fecha_resolucion_display, observaciones=None):
    """
    Genera el cuerpo del correo como informe del formulario GH-FR-007: mismo diseño que el formulario web.
    Usa solo tablas y estilos inline para que Gmail y otros clientes muestren el diseño correctamente.
    """
    id_cedula = html_escape(str(solicitud.get("id_cedula") or "—"))
    nombre = html_escape(empleado_nombre or "—")
    area = html_escape(str(solicitud.get("area") or "—"))
    tipo = html_escape(str(solicitud.get("tipo") or "Permiso"))
    fecha_desde = _fecha_display(solicitud.get("fecha_desde"))
    fecha_hasta = _fecha_display(solicitud.get("fecha_hasta"))
    pr = solicitud.get("permiso_remunerado")
    remunerado_txt = "Remunerado" if pr == 1 else ("No Remunerado" if pr == 0 else "—")
    hora_inicio = (solicitud.get("hora_inicio") or "—")
    if hasattr(hora_inicio, "strftime"):
        hora_inicio = hora_inicio.strftime("%H:%M") if hora_inicio else "—"
    else:
        hora_inicio = str(hora_inicio) if hora_inicio else "—"
    hora_fin = (solicitud.get("hora_fin") or "—")
    if hasattr(hora_fin, "strftime"):
        hora_fin = hora_fin.strftime("%H:%M") if hora_fin else "—"
    else:
        hora_fin = str(hora_fin) if hora_fin else "—"
    motivo = html_escape(str(solicitud.get("motivo") or "—"))
    # Estilos inline para compatibilidad con Gmail/Outlook
    lbl = "font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.3px;margin-bottom:2px;font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;"
    val = "font-size:14px;color:#111;padding:6px 0;border-bottom:1px solid #e5e7eb;font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;"
    obs_row = ""
    if observaciones:
        obs_row = f'<tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top"><p style="{lbl}margin:0">Observaciones</p><p style="{val}margin:0">{html_escape(observaciones)}</p></td></tr>'
    return f"""
<p style="margin:0 0 16px 0;font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;"><span style="display:inline-block;padding:6px 12px;border-radius:8px;font-size:13px;font-weight:600;background:#d1fae5;color:#047857;">Permiso aprobado</span></p>
<p style="margin:0 0 20px 0;font-size:14px;color:#374151;font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;">Se adjunta el <strong>informe en PDF</strong> (Formato GH-FR-007) con los datos que diligenció y la firma digital de Coordinación Gestión Humana.</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:720px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;border-collapse:separate;border-spacing:0;overflow:hidden;">
  <tr>
    <td style="padding:16px 20px;border-bottom:1px solid #e5e7eb;background:#fafafa;">
      <table cellpadding="0" cellspacing="0" border="0"><tr><td style="font-size:13px;font-weight:600;color:#111;">COLBEEF S.A.S</td><td style="font-size:13px;color:#374151;padding-left:16px;">Código: GH-FR-007</td></tr><tr><td style="font-size:13px;font-weight:600;color:#111;">GESTION HUMANA</td><td style="font-size:13px;color:#374151;padding-left:16px;">Versión: 01</td></tr></table>
    </td>
  </tr>
  <tr>
    <td style="padding:14px 20px 8px;font-size:17px;font-weight:700;color:#0b3518;font-family:Segoe UI,Tahoma,Geneva,Verdana,sans-serif;">FORMATO DE AUTORIZACION DE PERMISOS / LICENCIAS</td>
  </tr>
  <tr>
    <td style="padding:0 20px 14px;font-size:12px;color:#6b7280;">Fecha: {html_escape(fecha_resolucion_display)}</td>
  </tr>
  <tr>
    <td style="padding:12px 20px 20px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
        <tr>
          <td width="33%" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Fecha</p><p style="{val}margin:0">{html_escape(fecha_resolucion_display)}</p></td>
          <td width="33%" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Área</p><p style="{val}margin:0">{area}</p></td>
          <td width="34%" style="padding:0 0 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Documento de Identidad</p><p style="{val}margin:0">{id_cedula}</p></td>
        </tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Nombre Completo</p><p style="{val}margin:0">{nombre}</p></td></tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Fecha del permiso / Licencia</p><p style="{val}margin:0">{fecha_desde} a {fecha_hasta}</p></td></tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Permiso remunerado / Permiso No Remunerado</p><p style="{val}margin:0">{html_escape(remunerado_txt)}</p></td></tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Hora de Inicio / Hora Final</p><p style="{val}margin:0">{html_escape(str(hora_inicio))} – {html_escape(str(hora_fin))}</p></td></tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Motivo</p><p style="{val}margin:0">{motivo}</p></td></tr>
        <tr><td colspan="3" style="padding:0 8px 12px 0;vertical-align:top;"><p style="{lbl}margin:0">Tipo</p><p style="{val}margin:0">{tipo}</p></td></tr>
        {obs_row}
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px;border:1px solid #e5e7eb;border-radius:8px;border-collapse:collapse;">
        <tr>
          <td width="33%" style="padding:14px 12px;text-align:center;border-right:1px solid #e5e7eb;background:#fafafa;vertical-align:top;">
            <p style="font-size:11px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.3px;margin:0 0 8px 0;">Firma Solicitante</p>
            <p style="font-size:12px;color:#4b5563;margin:8px 0 0;line-height:1.4;">Nombre: {nombre}<br>C.C: {id_cedula}</p>
          </td>
          <td width="33%" style="padding:14px 12px;text-align:center;border-right:1px solid #e5e7eb;background:#fafafa;vertical-align:top;">
            <p style="font-size:11px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.3px;margin:0 0 8px 0;">V.B Jefe Inmediato</p>
            <p style="font-size:12px;color:#4b5563;margin:8px 0 0;">—</p>
          </td>
          <td width="34%" style="padding:14px 12px;text-align:center;background:#f0fdf4;vertical-align:top;">
            <p style="font-size:11px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.3px;margin:0 0 8px 0;">Firma Recibido Gestión Humana</p>
            {firma_img_html}
            <p style="font-size:12px;color:#166534;margin:8px 0 0;line-height:1.4;">Coordinación de Gestión Humana<br>Colbeef</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
"""


def notificar_resolucion_permiso(app, solicitud, empleado_nombre, empleado_email, aprobado, observaciones=None, attachments=None):
    """Notifica al empleado que su solicitud fue aprobada o rechazada.
    El correo va al empleado (direccion_email en BD). Si está vacío, se usa el primer correo de MAIL_PRUEBAS_CC para pruebas.
    Si aprobado=True, el cuerpo del correo es un informe con la estructura del formulario GH-FR-007, datos completos y firma digital.
    attachments: lista opcional de (nombre_archivo, ruta_archivo), ej. PDF firmado al aprobar."""
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
    # Firma digital: imagen para informe (aprobado) o mensaje breve (rechazado)
    root = getattr(app, "root_path", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    firma_en_raiz = os.path.join(root, "firma digital cindy.png")
    firma_cfg = (app.config.get("SIGNATURE_IMAGE_PATH") or "").strip()
    firma_path = firma_en_raiz if os.path.isfile(firma_en_raiz) else (firma_cfg if firma_cfg and os.path.isfile(firma_cfg) else None)
    inline_images = [("firma_gh", firma_path)] if firma_path else []
    firma_img_html = (
        '<div style="margin:8px 0 6px"><img src="cid:firma_gh" alt="Firma Coordinación" style="max-height:72px; display:block;"></div>'
        if firma_path
        else '<div class="mail-sign-name" style="margin:8px 0">Coordinación Gestión Humana</div>'
    )
    if not aprobado:
        inline_images = []
    try:
        from datetime import datetime
        fecha_resolucion_display = datetime.now().strftime("%d-%m-%Y")
    except Exception:
        fecha_resolucion_display = _fecha_display(solicitud.get("fecha_resolucion"))
    if aprobado:
        body_content = _body_informe_permiso_aprobado(solicitud, empleado_nombre, firma_img_html, fecha_resolucion_display, observaciones=observaciones)
    else:
        tabla_filas = [
            ("<th>Tipo de permiso</th>", f"<td>{html_escape(str(solicitud.get('tipo', 'Permiso')))}</td>"),
            ("<th>Fecha desde</th>", f"<td>{html_escape(str(solicitud.get('fecha_desde', '—')))}</td>"),
            ("<th>Fecha hasta</th>", f"<td>{html_escape(str(solicitud.get('fecha_hasta', '—')))}</td>"),
        ]
        if observaciones:
            tabla_filas.append(("<th>Observaciones</th>", f"<td>{html_escape(observaciones)}</td>"))
        rows_html = "".join(f"<tr>{th}{td}</tr>" for th, td in tabla_filas)
        tabla = f'<table class="mail-table"><tbody>{rows_html}</tbody></table>'
        nombre_safe = html_escape(empleado_nombre)
        body_content = f"""
    <p>Estimado/a <strong>{nombre_safe}</strong>,</p>
    <p>Coordinación Gestión Humana ha resuelto su solicitud de permiso/licencia.</p>
    <p><span class="mail-badge {badge_class}">{estado_label}</span></p>
    <p>Su solicitud de permiso no ha sido aprobada. Si tiene dudas o desea más información, puede contactar a Coordinación Gestión Humana.</p>
    {tabla}
    """
    body = _wrap_html(body_content, title=subject, subtitle=f"Informe de permiso {estado_label}" if aprobado else f"Solicitud de permiso {estado_label}")
    plain = _strip_html(body_content)
    id_sol = solicitud.get("id")
    if app and hasattr(app, "logger"):
        app.logger.info(f"[Permisos] Resolución solicitud id={id_sol} → enviando a {empleado_email} ({estado})")
    ok = send_mail(empleado_email, subject, body, body_text=plain, app=app, attachments=attachments or [], inline_images=inline_images)
    if app and hasattr(app, "logger"):
        app.logger.info(f"[Permisos] Resolución id={id_sol} → resultado_enviado={ok}")
    return ok
