# -*- coding: utf-8 -*-
"""
Firma digital sobre PDF: superpone una imagen de firma en un PDF existente.
Formato: FORMATO DE AUTORIZACION DE PERMISO O LICENCIA (GH-FR-007) – tres celdas al pie:
  Firma Solicitante | V.B Jefe Inmediato | Firma Recibido Gestión Humana
La firma de Coordinación (coordinacion.gestionhumana@colbeef.com) se ubica en la celda
"Firma Recibido Gestión Humana" (tercera columna).
Usa pypdf para leer/escribir y reportlab para generar la capa de firma.
"""
import os
from io import BytesIO

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from PIL import Image
except ImportError:
    PdfReader = PdfWriter = canvas = Image = None


# Tamaño máximo de la firma en el PDF (puntos: 1/72 inch)
FIRMA_ANCHO_MAX = 110
FIRMA_ALTO_MAX = 48
MARGEN = 40

# Formato GH-FR-007 (FORMATO DE AUTORIZACION DE PERMISO O LICENCIA): página tipo carta ~612x792 pt.
# Celda "Firma Recibido Gestión Humana" = tercera columna (derecha). Origen PDF: abajo-izquierda.
ANCHO_CELDA_GH = 1.0 / 3.0   # un tercio del ancho de página
Y_FIRMA_GH_PT = 70           # distancia del borde inferior a la base de la firma (puntos)


def firmar_pdf(pdf_path, firma_image_path, output_path, posicion="bottom_right"):
    """
    Superpone la imagen de firma sobre la primera página del PDF y guarda en output_path.

    :param pdf_path: ruta del PDF original (ej. evidencia del permiso).
    :param firma_image_path: ruta de la imagen de firma (PNG/JPG recomendado).
    :param output_path: ruta donde guardar el PDF firmado.
    :param posicion: "gh_celda_firma" (celda Firma Recibido GH), "bottom_right", "bottom_left", "top_right", "top_left".
    :return: True si se generó correctamente, False si falta librería o archivo.
    """
    if PdfReader is None or canvas is None:
        return False
    if not os.path.isfile(pdf_path) or not os.path.isfile(firma_image_path):
        return False

    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return False
        page = reader.pages[0]
        mb = page.mediabox
        ancho_pag = float(mb.width)
        alto_pag = float(mb.height)

        # Imagen de firma: limitar tamaño para que quepa en la celda del formato
        with Image.open(firma_image_path) as img_pil:
            iw, ih = img_pil.size
        if iw <= 0 or ih <= 0:
            return False
        ratio = min(FIRMA_ANCHO_MAX / iw, FIRMA_ALTO_MAX / ih, 1.0)
        w_sig = iw * ratio
        h_sig = ih * ratio

        # Posición según parámetro (coordinación = celda "Firma Recibido Gestión Humana")
        if posicion == "gh_celda_firma":
            # Formato igual al PDF: Firma Solicitante | V.B Jefe Inmediato | Firma Recibido Gestión Humana.
            # Ubicar la firma en la celda derecha donde dice "Firma Recibido Gestión Humana".
            ancho_celda = ancho_pag * ANCHO_CELDA_GH
            x_centro_tercera = ancho_pag * (2.0/3.0) + ancho_celda / 2.0
            x = x_centro_tercera - w_sig / 2.0
            y = Y_FIRMA_GH_PT
        elif posicion == "bottom_right":
            x = ancho_pag - w_sig - MARGEN
            y = MARGEN
        elif posicion == "bottom_left":
            x = MARGEN
            y = MARGEN
        elif posicion == "top_right":
            x = ancho_pag - w_sig - MARGEN
            y = alto_pag - h_sig - MARGEN
        else:  # top_left
            x = MARGEN
            y = alto_pag - h_sig - MARGEN

        # Capa de firma (mismo tamaño que la página)
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(ancho_pag, alto_pag))
        c.drawImage(firma_image_path, x, y, width=w_sig, height=h_sig)
        c.save()
        buffer.seek(0)
        overlay_reader = PdfReader(buffer)
        overlay_page = overlay_reader.pages[0]

        # Fusionar firma sobre la primera página
        page.merge_transformed_page(overlay_page, over=True)

        writer = PdfWriter()
        writer.add_page(page)
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])
        with open(output_path, "wb") as f:
            writer.write(f)
        return True
    except Exception:
        return False
