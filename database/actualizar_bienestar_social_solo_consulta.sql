-- BIENESTAR SOCIAL: solo consulta (sin botón Agregar en Personal, etc.)
-- Ejecutar si usas la tabla rol_permiso para que bienestarsocial@colbeef.com solo pueda consultar.

USE gestio_humana;

UPDATE rol_permiso SET nivel = 'READ' WHERE rol_nombre = 'BIENESTAR SOCIAL';

-- Actualizar el texto de acciones del usuario Bienestar Social (se muestra en pantalla Usuarios)
-- Usamos id_user (clave primaria) para evitar error 1175 (safe update mode)
UPDATE usuario SET acciones = 'VISTA' WHERE id_user = 'US-0005' AND rol = 'BIENESTAR SOCIAL';
