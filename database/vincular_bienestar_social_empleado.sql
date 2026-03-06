-- Vincular el usuario Bienestar Social con su ficha de empleado para que pueda
-- solicitar permisos "para sí misma" (el formulario la identifica por id_cedula).
-- Reemplaza 1234567890 por la cédula real de la persona en la tabla empleado.

USE gestio_humana;

UPDATE usuario SET id_cedula = '1234567890' WHERE id_user = 'US-0005' AND rol = 'BIENESTAR SOCIAL';
