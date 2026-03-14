-- Firma digital por usuario
-- Agrega una columna opcional en usuario para guardar la ruta de la imagen de firma.

USE gestio_humana;

-- Nota: MySQL versiones antiguas no aceptan "ADD COLUMN IF NOT EXISTS".
-- Si la columna ya existe, este ALTER dará error la segunda vez; basta con ejecutarlo una sola vez.
-- Esta migración ya no es necesaria para la lógica principal (la firma se toma del SIGNATURE_IMAGE_PATH global).
-- Si ya ejecutaste el ALTER y la columna existe, no pasa nada; simplemente queda sin uso.
-- Puedes dejar este archivo solo como referencia histórica.
-- ALTER TABLE usuario ADD COLUMN firma_path VARCHAR(255) NULL AFTER acciones;

-- Para ver qué usuarios tienen firma configurada:
-- SELECT id_user, nombre, email, firma_path FROM usuario WHERE firma_path IS NOT NULL;

