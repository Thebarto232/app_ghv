# Cómo comprobar que la firma digital está en funcionamiento

## 1. Configurar la imagen de firma

En el archivo **`.env`** (raíz del proyecto) agrega o edita:

```env
SIGNATURE_IMAGE_PATH=ruta/a/tu/imagen_firma.png
```

- **Ruta absoluta (recomendado para pruebas):**  
  `SIGNATURE_IMAGE_PATH=C:\Users\TuUsuario\Downloads\firma.png`
- **Ruta relativa al proyecto:**  
  Crea la carpeta `instance/static/`, guarda ahí la imagen (por ejemplo `firma_coordinacion.png`) y pon:  
  `SIGNATURE_IMAGE_PATH=instance/static/firma_coordinacion.png`

La imagen puede ser **PNG o JPG** (fondo transparente en PNG se ve mejor sobre el PDF).

Reinicia la aplicación después de cambiar `.env`.

---

## 2. Condiciones para que se firme el PDF

La firma solo se aplica cuando **se cumplen todas** estas condiciones:

| Requisito | Descripción |
|-----------|-------------|
| **SIGNATURE_IMAGE_PATH** | Definido en `.env` y la ruta existe. |
| **Evidencia en PDF** | La solicitud tiene “evidencia” adjunta y el archivo es **PDF** (no solo imagen). |
| **Acción** | Coordinación **aprueba** la solicitud (no al rechazar). |

Si la evidencia es JPG/PNG, no se genera PDF firmado (solo se firma sobre PDFs).

---

## 3. Prueba rápida (flujo completo)

1. **Crear una imagen de firma**  
   - Cualquier PNG/JPG con tu firma (foto, escaneo o dibujo).  
   - Guardarla en una ruta fija, por ejemplo:  
     `d:\proyectos\gestio_humana\instance\static\firma.png`

2. **Configurar `.env`**  
   - `SIGNATURE_IMAGE_PATH=d:\proyectos\gestio_humana\instance\static\firma.png`  
   - O la ruta absoluta que estés usando.

3. **Solicitud con evidencia PDF**  
   - Entra como **empleado** (o como gestor/coordinación en nombre de un empleado).  
   - Nueva solicitud de permiso → **No remunerado** → adjuntar un **PDF** (por ejemplo el “Formato de autorización de permiso o licencia”).  
   - Enviar la solicitud.

4. **Aprobar como coordinación**  
   - Entra como **COORD. GH** (o ADMIN).  
   - Ir a **Solicitudes de permiso** → abrir la solicitud pendiente.  
   - Opcional: usar **“Ver evidencia”** para confirmar que el PDF está bien.  
   - Pulsar **Aprobar** (con o sin observaciones).

5. **Comprobar que funcionó**  
   - **En la app:** debe salir el mensaje verde:  
     *“Solicitud aprobada. Se notificó al empleado por correo **con el formato firmado adjunto**.”*  
   - **En el correo del empleado:** debe llegar un mensaje de “Resolución: permiso Aprobada” con un adjunto llamado **`Formato_permiso_firmado.pdf`**.  
   - Al abrir ese PDF, en la **esquina inferior derecha** de la primera página debe verse la imagen de firma superpuesta.

---

## 4. Probar solo el módulo de firma (sin correo)

Para verificar que la firma se estampa bien en un PDF, puedes usar un script:

```bash
py -c "
from pdf_firma import firmar_pdf
# Sustituye las rutas por las tuyas:
pdf_original = r'instance\uploads\permisos\ALGUN_ARCHIVO.pdf'
imagen_firma = r'instance\static\firma.png'
salida = r'test_firmado.pdf'
ok = firmar_pdf(pdf_original, imagen_firma, salida)
print('OK: PDF firmado guardado en', salida if ok else 'Fallo al firmar')
"
```

Si `ok` es `True`, abre `test_firmado.pdf` y comprueba que la firma aparece abajo a la derecha.

---

## 5. Si no se adjunta el PDF firmado

Revisa:

- **`.env`:** `SIGNATURE_IMAGE_PATH` sin espacios raros y ruta que exista.  
- **Evidencia:** que sea un **PDF** (extensión `.pdf` y archivo subido como evidencia).  
- **Carpeta de uploads:** que el archivo exista en `instance/uploads/permisos/...`.  
- **Consola de la app:** si hay errores al importar `pdf_firma` o al llamar a `firmar_pdf`, aparecerán ahí.

Si el mensaje al aprobar dice “con el formato firmado adjunto”, la firma se aplicó y el adjunto se envió; si no llega el correo, revisa SMTP (MAIL_* en `.env`).
