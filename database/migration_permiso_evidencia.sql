-- Evidencia adjunta para permiso no remunerado (ruta del archivo subido)
USE gestio_humana;

ALTER TABLE solicitud_permiso ADD COLUMN evidencia VARCHAR(500) NULL COMMENT 'Ruta del archivo adjunto (permiso no remunerado)';
