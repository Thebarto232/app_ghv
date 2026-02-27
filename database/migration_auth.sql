-- ============================================================
-- MIGRACIÓN: Agregar campo password a tabla usuario
-- Ejecutar en MySQL Workbench después de schema.sql
-- ============================================================

USE gestio_humana;

ALTER TABLE usuario
    ADD COLUMN password_hash VARCHAR(256) DEFAULT NULL AFTER email;

-- Contraseña temporal para todos los usuarios: Colbeef2026*
-- Se actualiza desde el script Python (hashed con werkzeug)
