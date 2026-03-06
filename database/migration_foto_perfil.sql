-- Foto de perfil por usuario (ruta relativa a static, ej: avatars/US-0001.jpg)
USE gestio_humana;

ALTER TABLE usuario ADD COLUMN foto_perfil VARCHAR(255) NULL COMMENT 'Ruta relativa a static: avatars/id_user.ext';
