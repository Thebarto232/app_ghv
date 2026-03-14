# -*- coding: utf-8 -*-
"""
Genera el informe PDF del formulario GH-FR-007 (FORMATO DE AUTORIZACION DE PERMISOS / LICENCIAS)
tal cual se ve en el formulario web: caja informativa superior, encabezado, campos con borde,
bloque de firmas con celda verde para la firma digital de Coordinación. Los datos que la persona
diligenció al enviar la solicitud se rellenan automáticamente en cada campo. Este PDF se envía
por correo al aprobar la solicitud.
"""
import os
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
except ImportError:  # pragma: no cover
    letter = None
    canvas = None
    HexColor = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

# Colores del formulario web (permiso_form.html)
VERDE_TITULO = HexColor("#0b3518") if HexColor else "black"
GRIS_LABEL = HexColor("#374151") if HexColor else "gray"
BORDE = HexColor("#e5e7eb") if HexColor else "gray"
FONDO_HEADER = HexColor("#fafafa") if HexColor else "white"
FONDO_FIRMA = HexColor("#fafafa") if HexColor else "white"
FONDO_HINT = HexColor("#f9fafb") if HexColor else "white"
CELDA_VERDE = HexColor("#f0fdf4") if HexColor else "white"
VERDE_TEXTO = HexColor("#166534") if HexColor else "darkgreen"
VERDE_NOTA = HexColor("#15803d") if HexColor else "darkgreen"

ANCHO_PAG, ALTO_PAG = (612, 792) if letter is None else letter
MARGEN = 48
ANCHO_CONT = ANCHO_PAG - 2 * MARGEN
RADIO = 8
ALTO_CAMPO = 22
ESP = 14
# Padding interno para que nada se desborde (márgenes visuales)
PAD = 24
# Altura del logo en el encabezado (puntos)
LOGO_HEADER_H = 44
LOGO_HEADER_W_MAX = 130

# Texto de la caja informativa superior (tal cual en la imagen)
TEXTO_INFO_FORMATO = (
    "Este es el formato oficial de autorización de permisos / licencias (GH-FR-007). "
    "El mismo formato es el que usa toda la empresa. Al aprobar, Coordinación Gestión Humana "
    "(coordinacion.gestionhumana@colbeef.com) firmará digitalmente en la celda "
    "'Firma Recibido Gestión Humana' y recibirá el documento por correo."
)


def _fecha_display(val):
    """Devuelve fecha DD-MM-YYYY."""
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


def _hora_display(val):
    """Devuelve hora HH:MM."""
    if val is None:
        return "—"
    if hasattr(val, "strftime"):
        return val.strftime("%H:%M")
    s = str(val).strip()
    if not s:
        return "—"
    if ":" in s:
        return s[:5]
    return s


def _draw_label(c, x, y, texto, font="Helvetica", size=10):
    c.setFont(font, size)
    c.setFillColor(GRIS_LABEL)
    c.drawString(x, y, texto)


def _draw_box_value(c, x, y, w, h, valor, font="Helvetica", size=10):
    c.setStrokeColor(BORDE)
    c.setLineWidth(0.5)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFillColor("black")
    c.setFont(font, size)
    text = str(valor)[:60] + ("..." if len(str(valor)) > 60 else "")
    c.drawString(x + 6, y + (h - size) / 2 - 2, text)


def _draw_paragraph(c, x, y, width, text, font="Helvetica", size=10, leading=14):
    """Dibuja un párrafo con salto de línea por ancho; recorta cada línea al ancho para que no se salga."""
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        if c.stringWidth(test, font, size) <= width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    for i, line in enumerate(lines):
        # Recortar línea al ancho máximo para que no desborde la caja
        orig = line
        while line and c.stringWidth(line, font, size) > width:
            line = line[:-1]
        if len(line) < len(orig) and len(line) > 2:
            line = line.rstrip()[:-2].rstrip() + ".."
        c.drawString(x, y - i * leading, line)
    return y - len(lines) * leading


def _resolver_firma(firma_image_path):
    """Usa la ruta recibida o busca 'firma digital cindy.png' en raíz, static o carpeta superior."""
    if firma_image_path and os.path.isfile(firma_image_path):
        return firma_image_path
    root = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(root)
    for candidate in (
        os.path.join(root, "firma digital cindy.png"),
        os.path.join(root, "static", "firma digital cindy.png"),
        os.path.join(parent, "firma digital cindy.png"),
    ):
        if os.path.isfile(candidate):
            return candidate
    return None


def _resolver_logo():
    """Ruta al logo Colbeef (PNG o JPG) en static/img."""
    root = os.path.dirname(os.path.abspath(__file__))
    for name in ("logo_colbeef.png", "logo_colbeef.jpg"):
        path = os.path.join(root, "static", "img", name)
        if os.path.isfile(path):
            return path
    return None


def generar_informe_permiso_pdf(solicitud, empleado_nombre, output_path, firma_image_path=None):
    """
    Genera el informe PDF tal cual el formulario: datos diligenciados y firma digital cindy.png
    en la celda Firma Recibido Gestión Humana. Se envía por correo al aprobar.
    """
    if canvas is None:
        return False
    firma_image_path = _resolver_firma(firma_image_path)
    try:
        c = canvas.Canvas(output_path, pagesize=(ANCHO_PAG, ALTO_PAG))
        x_cont = MARGEN
        w_cont = ANCHO_CONT

        # Origen desde arriba: vamos restando Y
        y = ALTO_PAG - MARGEN - 20

        # —— Caja informativa superior (márgenes generosos para que no se desborde) ——
        ancho_info = w_cont
        x_info = x_cont
        alto_caja_info = 58
        y_caja_info = y - alto_caja_info
        c.setFillColor(FONDO_HINT)
        c.setStrokeColor(BORDE)
        c.setLineWidth(1)
        c.roundRect(x_info, y_caja_info, ancho_info, alto_caja_info, RADIO, stroke=1, fill=1)
        c.setFillColor(GRIS_LABEL)
        c.setFont("Helvetica", 10)
        _draw_paragraph(c, x_info + PAD, y_caja_info + alto_caja_info - 12, ancho_info - 2 * PAD, TEXTO_INFO_FORMATO, size=9, leading=11)
        y = y_caja_info - 16

        # —— Contenedor principal del formulario (borde redondeado, blanco) ——
        alto_total = 600
        y_cont = y - alto_total
        c.setStrokeColor(BORDE)
        c.setFillColor("white")
        c.setLineWidth(1)
        c.roundRect(x_cont, y_cont, w_cont, alto_total, RADIO, stroke=1, fill=1)

        # —— Encabezado (fondo gris + logo Colbeef a la izquierda) ——
        alto_header = 60
        y_header = y - alto_header
        c.setFillColor(FONDO_HEADER)
        c.setStrokeColor(BORDE)
        c.rect(x_cont, y_header, w_cont, alto_header, stroke=1, fill=1)
        # Logo Colbeef (da presencia; si no existe, el texto sigue igual)
        logo_path = _resolver_logo()
        x_text_header = x_cont + PAD
        if logo_path and Image is not None:
            try:
                with Image.open(logo_path) as img_logo:
                    iw, ih = img_logo.size
                if iw > 0 and ih > 0:
                    logo_w = min(LOGO_HEADER_W_MAX, LOGO_HEADER_H * iw / ih)
                    logo_h = LOGO_HEADER_H
                    x_logo = x_cont + PAD
                    y_logo = y_header + (alto_header - logo_h) / 2
                    c.drawImage(logo_path, x_logo, y_logo, width=logo_w, height=logo_h)
                    x_text_header = x_logo + logo_w + 16
            except Exception:
                pass
        c.setFillColor("black")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_text_header, y_header + 36, "COLBEEF S.A.S")
        c.drawString(x_text_header, y_header + 20, "GESTION HUMANA")
        c.drawString(x_cont + w_cont - PAD - 120, y_header + 36, "Código: GH-FR-007")
        c.drawString(x_cont + w_cont - PAD - 120, y_header + 20, "Versión: 01")

        y = y_header - 4

        # —— Título verde ——
        c.setFillColor(VERDE_TITULO)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_cont + PAD, y, "FORMATO DE AUTORIZACION DE PERMISOS / LICENCIAS")
        y -= 20

        # Fecha del documento
        fecha_cabecera = _fecha_display(
            solicitud.get("fecha_solicitud")
            or solicitud.get("fecha_creacion")
            or solicitud.get("fecha_desde")
            or datetime.now()
        )
        c.setFillColor(GRIS_LABEL)
        c.setFont("Helvetica", 11)
        c.drawString(x_cont + PAD, y, f"Fecha: {fecha_cabecera}")
        y -= 28

        # —— Datos diligenciados ——
        id_cedula = str(solicitud.get("id_cedula") or "—")
        area = str(solicitud.get("area") or "—")
        nombre = empleado_nombre or "—"
        fecha_desde = _fecha_display(solicitud.get("fecha_desde"))
        fecha_hasta = _fecha_display(solicitud.get("fecha_hasta"))
        pr = solicitud.get("permiso_remunerado")
        remunerado_txt = "Remunerado" if pr == 1 else ("No Remunerado" if pr == 0 else "—")
        hora_inicio = _hora_display(solicitud.get("hora_inicio"))
        hora_fin = _hora_display(solicitud.get("hora_fin"))
        motivo = str(solicitud.get("motivo") or "—")
        tipo = str(solicitud.get("tipo") or "Permiso")

        # Fila 1: FECHA | ÁREA | DOCUMENTO DE IDENTIDAD (márgenes PAD)
        col_w = (w_cont - 2 * PAD - 24) / 3
        x1, x2, x3 = x_cont + PAD, x_cont + PAD + col_w + 12, x_cont + PAD + 2 * (col_w + 12)
        _draw_label(c, x1, y, "Fecha")
        _draw_label(c, x2, y, "Área")
        _draw_label(c, x3, y, "Documento de Identidad")
        y -= 18
        _draw_box_value(c, x1, y - ALTO_CAMPO, col_w, ALTO_CAMPO, fecha_cabecera)
        _draw_box_value(c, x2, y - ALTO_CAMPO, col_w, ALTO_CAMPO, area)
        _draw_box_value(c, x3, y - ALTO_CAMPO, col_w, ALTO_CAMPO, id_cedula)
        y -= ALTO_CAMPO + ESP

        # NOMBRE COMPLETO *
        _draw_label(c, x_cont + PAD, y, "Nombre Completo *")
        y -= 18
        _draw_box_value(c, x_cont + PAD, y - ALTO_CAMPO, w_cont - 2 * PAD, ALTO_CAMPO, nombre)
        y -= ALTO_CAMPO + ESP

        # FECHA DEL PERMISO / LICENCIA *
        _draw_label(c, x_cont + PAD, y, "Fecha del permiso / Licencia *")
        y -= 18
        _draw_box_value(c, x_cont + PAD, y - ALTO_CAMPO, w_cont - 2 * PAD, ALTO_CAMPO, f"{fecha_desde} a {fecha_hasta}")
        y -= ALTO_CAMPO + ESP

        # PERMISO REMUNERADO / NO REMUNERADO *
        _draw_label(c, x_cont + PAD, y, "Permiso remunerado / Permiso No Remunerado *")
        y -= 18
        medio_w = (w_cont - 2 * PAD) / 2
        _draw_box_value(c, x_cont + PAD, y - ALTO_CAMPO, medio_w - 6, ALTO_CAMPO, remunerado_txt)
        c.setFillColor(GRIS_LABEL)
        c.setFont("Helvetica", 9)
        c.drawString(x_cont + PAD, y - ALTO_CAMPO - 14, "Si es no remunerado debe adjuntar evidencia (PDF o imagen).")
        y -= ALTO_CAMPO + 32

        # HORA DE INICIO | HORA FINAL
        medio = (w_cont - 2 * PAD) / 2
        _draw_label(c, x_cont + PAD, y, "Hora de Inicio")
        _draw_label(c, x_cont + PAD + medio + 12, y, "Hora Final")
        y -= 18
        _draw_box_value(c, x_cont + PAD, y - ALTO_CAMPO, medio - 6, ALTO_CAMPO, hora_inicio)
        _draw_box_value(c, x_cont + PAD + medio + 12, y - ALTO_CAMPO, medio - 6, ALTO_CAMPO, hora_fin)
        y -= ALTO_CAMPO + ESP

        # MOTIVO
        _draw_label(c, x_cont + PAD, y, "Motivo")
        y -= 18
        alto_motivo = 50
        c.setStrokeColor(BORDE)
        c.rect(x_cont + PAD, y - alto_motivo, w_cont - 2 * PAD, alto_motivo, stroke=1, fill=0)
        c.setFillColor("black")
        c.setFont("Helvetica", 10)
        for i, line in enumerate((motivo[:90] + ("..." if len(motivo) > 90 else "")).split("\n")[:3]):
            c.drawString(x_cont + PAD + 6, y - 18 - i * 14, line[:85])
        y -= alto_motivo + ESP

        # TIPO *
        _draw_label(c, x_cont + PAD, y, "Tipo *")
        y -= 18
        _draw_box_value(c, x_cont + PAD, y - ALTO_CAMPO, 220, ALTO_CAMPO, tipo)
        y -= ALTO_CAMPO + 20

        # —— Línea separadora ——
        c.setStrokeColor(BORDE)
        c.line(x_cont + PAD, y, x_cont + w_cont - PAD, y)
        y -= 24

        # —— Bloque de firmas (3 celdas; más alto para que la firma no quede apretada) ——
        alto_celda = 108
        ancho_celda = (w_cont - 2 * PAD) / 3
        pad_celda = 10
        y_celda = y - alto_celda

        # Celda 1: Firma Solicitante (texto que quepa sin cortarse)
        c.setStrokeColor(BORDE)
        c.setFillColor(FONDO_FIRMA)
        c.rect(x_cont + PAD, y_celda, ancho_celda, alto_celda, stroke=1, fill=1)
        ancho_texto_celda = ancho_celda - 2 * pad_celda
        c.setFillColor("black")
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_cont + PAD + pad_celda, y_celda + alto_celda - 16, "FIRMA SOLICITANTE")
        c.setFont("Helvetica", 8)
        c.setFillColor(GRIS_LABEL)
        nom_line = f"Nombre: {nombre[:22]}{'...' if len(nombre) > 22 else ''}"
        if c.stringWidth(nom_line, "Helvetica", 8) > ancho_texto_celda:
            nom_line = "Nombre: " + nombre[:14] + ".."
        c.drawString(x_cont + PAD + pad_celda, y_celda + alto_celda - 34, nom_line)
        c.drawString(x_cont + PAD + pad_celda, y_celda + alto_celda - 46, f"C.C: {id_cedula}")

        # Celda 2: V.B Jefe Inmediato (título que quepa)
        c.setStrokeColor(BORDE)
        c.setFillColor(FONDO_FIRMA)
        c.rect(x_cont + PAD + ancho_celda, y_celda, ancho_celda, alto_celda, stroke=1, fill=1)
        c.setFillColor("black")
        c.setFont("Helvetica-Bold", 9)
        tit2 = "V.B JEFE INMEDIATO"
        if c.stringWidth(tit2, "Helvetica-Bold", 9) > ancho_texto_celda:
            tit2 = "V.B JEFE INMED."
        c.drawString(x_cont + PAD + ancho_celda + pad_celda, y_celda + alto_celda - 16, tit2)

        # Celda 3: Firma Recibido Gestión Humana (fondo verde + firma digital; texto que no se corte)
        c.setStrokeColor(BORDE)
        c.setFillColor(CELDA_VERDE)
        c.rect(x_cont + PAD + 2 * ancho_celda, y_celda, ancho_celda, alto_celda, stroke=1, fill=1)
        x_gh = x_cont + PAD + 2 * ancho_celda + pad_celda
        ancho_gh = ancho_celda - 2 * pad_celda
        c.setFillColor(VERDE_TEXTO)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x_gh, y_celda + alto_celda - 12, "FIRMA RECIBIDO")
        c.drawString(x_gh, y_celda + alto_celda - 24, "GESTIÓN HUMANA")
        c.setFont("Helvetica", 7)
        c.setFillColor(VERDE_NOTA)
        # Dos líneas que quepan en la celda sin cortarse
        ln1 = "Se firmará digitalmente"
        ln2 = "al aprobar (Coordinación)"
        if c.stringWidth(ln1, "Helvetica", 7) > ancho_gh:
            ln1 = "Se firmará digitalm."
        if c.stringWidth(ln2, "Helvetica", 7) > ancho_gh:
            ln2 = "al aprobar (Coord.)"
        c.drawString(x_gh, y_celda + alto_celda - 40, ln1)
        c.drawString(x_gh, y_celda + alto_celda - 50, ln2)

        # Imagen de firma en la celda verde (centrada, debajo del texto)
        if firma_image_path and os.path.isfile(firma_image_path) and Image is not None:
            try:
                with Image.open(firma_image_path) as img:
                    iw, ih = img.size
                if iw > 0 and ih > 0:
                    firma_w = min(90, 90 * iw / ih)
                    firma_h = min(38, 38 * ih / iw)
                    x_sig = x_cont + PAD + 2 * ancho_celda + (ancho_celda - firma_w) / 2
                    y_sig = y_celda + 44
                    c.drawImage(firma_image_path, x_sig, y_sig, width=firma_w, height=firma_h)
            except Exception:
                pass
        c.setFillColor("black")
        c.setFont("Helvetica", 7)
        pie1 = "Coordinación de Gestión Humana"
        if c.stringWidth(pie1, "Helvetica", 7) > ancho_gh:
            pie1 = "Coordinación Gestión Humana"
        c.drawString(x_gh, y_celda + 14, pie1)
        c.drawString(x_gh, y_celda + 4, "Colbeef")

        c.save()
        return True
    except Exception:
        return False
