# Resumen del proyecto – Para presentación

## Qué es el sistema

**Sistema de Gestión Humana – Colbeef**: aplicación web interna para recursos humanos. Gestiona personal, organización, permisos, licencias, vacaciones, eventos (cumpleaños, aniversarios), EPS, fondos de pensiones, reportes y usuarios con roles.

- **Tecnologías:** Python, Flask, MySQL, HTML/CSS/JS, correo SMTP, generación y firma de PDF.
- **Usuarios:** coordinación GH, gestor de contratación, bienestar social, nómina, SST, administrador, empleados (portal limitado).

---

## 1. Instalación y puesta en marcha en otra máquina

**Objetivo:** Poder clonar o copiar el proyecto e instalarlo en otro equipo (por ejemplo otro PC o servidor).

**Hecho:**
- **README** ampliado con guía paso a paso: clonar/copiar, entorno virtual, `pip`/`py -m pip`, MySQL (script `crear_bd_completo.sql`), archivo `.env`, ejecutar `python app.py` o `py app.py`.
- Indicaciones para cuando **no existe `pip`** en PATH (usar `py -m pip`) o cuando **no existe `requirements.txt`** (estar en la carpeta correcta del proyecto).
- Aclaración de qué **sí debe pasarse** a otra máquina: **proyecto completo** + archivo **`.env`** (no va en Git). Opcional: crear `.gitignore` en la otra máquina.
- **Base de datos:** un solo script `database/crear_bd_completo.sql` para crear BD, usuario y tablas.

**Mensaje para la presentación:** “El sistema está documentado para instalarse en cualquier máquina: README, .env, MySQL y un solo script de base de datos.”

---

## 2. Rol “GH INFORMADA” y notificación a gestionhumana@colbeef.com

**Objetivo:** Que **gestionhumana@colbeef.com** reciba la misma información que coordinación sobre permisos (correos y vista del módulo), pero **solo como informada**, sin aprobar ni rechazar.

**Hecho:**
- **Variable de entorno** `MAIL_GH_INFORMADA` (por defecto `gestionhumana@colbeef.com`). Recibe un correo en cada **nueva solicitud de permiso**, con el mismo detalle pero con texto “solo informativo; coordinación es quien aprueba o rechaza”.
- **Rol “GH INFORMADA”** en el sistema: mismo menú que coordinación (incluido el módulo Permisos), pero en el listado de permisos **no** ve botones Aprobar/Rechazar; solo consulta.
- **Migración SQL** `database/migration_rol_gh_informada.sql`: crea el rol, permisos READ y módulos visibles. Asignación del rol al usuario con correo gestionhumana@colbeef.com (por BD o desde administración de usuarios).
- **Ajuste en la vista de permisos:** quien tiene módulo “permisos” puede ver el listado; solo COORD. GH y ADMIN ven los botones de aprobar/rechazar (`puede_aprobar`).

**Mensaje para la presentación:** “Hay un rol solo informado: recibe los mismos correos y ve el mismo módulo de permisos que coordinación, pero no toma decisiones; eso lo hace solo coordinación.”

---

## 3. Coordinadora puede ver la evidencia adjunta

**Objetivo:** Que la coordinación pueda **revisar el archivo** (PDF o imagen) que el empleado adjuntó en permisos no remunerados, antes de aprobar o rechazar.

**Hecho:**
- **Ruta** `GET /permisos/<id>/evidencia`: solo usuarios con acceso al módulo Permisos pueden abrir/descargar el archivo de evidencia de esa solicitud.
- En la **tarjeta de cada solicitud** (listado de permisos) se muestra, cuando hay evidencia, la fila **“Evidencia adjunta”** con el enlace **“Ver evidencia”** (abre en nueva pestaña el PDF o imagen).
- La evidencia solo existe cuando el empleado marcó “no remunerado” y subió un archivo; si no hay adjunto, la fila no aparece.

**Mensaje para la presentación:** “La coordinación ya no solo aprueba o rechaza: puede abrir y revisar el documento adjunto antes de decidir.”

---

## 4. Firma digital sobre el formato de permiso (PDF)

**Objetivo:** Al **aprobar** una solicitud cuya evidencia es un **PDF**, generar una copia del PDF con una **imagen de firma** superpuesta y enviarla al empleado por correo.

**Hecho:**
- **Módulo** `pdf_firma.py`: función que, dado un PDF y una imagen de firma (PNG/JPG), genera un nuevo PDF con la firma en una esquina (por defecto inferior derecha). Usa **pypdf**, **reportlab** y **Pillow**.
- **Configuración** en `.env`: `SIGNATURE_IMAGE_PATH` con la ruta a la imagen de firma. Si está vacío, no se firma ni se adjunta PDF.
- **Flujo:** al aprobar una solicitud que tiene evidencia en PDF, se llama a `firmar_pdf`, se genera un archivo temporal “Formato_permiso_firmado.pdf” y se **adjunta al correo** de resolución al empleado. Luego se borra el temporal.
- **Feedback en la app:** si se adjuntó el PDF firmado, el mensaje verde dice: “Solicitud aprobada. Se notificó al empleado por correo **con el formato firmado adjunto**.”
- **Documentación** en `docs/PRUEBA_FIRMA_DIGITAL.md`: cómo configurar, condiciones (evidencia PDF, aprobación, SIGNATURE_IMAGE_PATH) y cómo comprobar que funciona.

**Mensaje para la presentación:** “Cuando coordinación aprueba y el empleado subió un PDF, el sistema estampa la firma digital sobre ese PDF y lo envía al empleado por correo como formato firmado.”

---

## 5. Presentación en PowerPoint y descarga

**Objetivo:** Tener una **presentación** del proyecto y poder **descargarla** fácilmente.

**Hecho:**
- **Script** `scripts/generar_presentacion.py`: genera el archivo `presentacion_gestio_humana.pptx` en la raíz del proyecto. Diapositivas: portada, introducción, objetivos, tecnologías, módulos, flujo de permisos, roles, seguridad, resumen, cierre.
- **Dependencia** `python-pptx` en `requirements.txt`. Comando: `py scripts/generar_presentacion.py` para regenerar.
- **Ruta en la app** `GET /descargar/presentacion`: usuario autenticado puede descargar `presentacion_gestio_humana.pptx` desde el navegador.

**Mensaje para la presentación:** “El propio proyecto incluye una presentación en PowerPoint que se puede regenerar con un script y descargar desde la aplicación.”

---

## 6. Resumen en una frase por bloque

| Tema | En una frase |
|------|----------------|
| **Instalación** | README y .env permiten instalar el sistema en otra máquina; solo hay que clonar, configurar BD y .env. |
| **GH INFORMADA** | Rol y correo para estar informada de permisos sin aprobar; misma información que coordinación, sin botones de decisión. |
| **Evidencia** | La coordinación puede ver y descargar el archivo adjunto de cada solicitud con el enlace “Ver evidencia”. |
| **Firma digital** | Al aprobar una solicitud con evidencia PDF, se estampa la firma y se envía el PDF firmado por correo al empleado. |
| **Presentación** | PowerPoint del proyecto generado por script y descargable desde la app para presentar el sistema. |

---

## Orden sugerido para la presentación

1. **Qué es el sistema** (portada e introducción del propio PowerPoint).
2. **Objetivos y tecnologías** (diapositivas ya hechas).
3. **Módulos** (organización, personal, permisos, vacaciones, etc.).
4. **Permisos en detalle:** flujo empleado → coordinación; **evidencia** (ver adjunto); **aprobación**; **firma digital** (PDF firmado por correo); **GH INFORMADA** (informada sin decidir).
5. **Roles** (quién hace qué).
6. **Instalación y despliegue** (README, .env, otra máquina).
7. **Cierre:** presentación descargable, documentación, próximos pasos.

Con este resumen puedes explicar todo el contexto de lo que se ha hecho y enlazarlo con las diapositivas de `presentacion_gestio_humana.pptx`.
