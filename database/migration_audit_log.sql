-- Telemetría / auditoría para reportes a nivel empresarial
-- Ejecutar una vez en la BD del proyecto

CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(50) NULL,
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(80) NULL,
    detalle VARCHAR(500) NULL,
    INDEX idx_fecha (fecha_hora),
    INDEX idx_modulo (modulo),
    INDEX idx_user (id_user)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
