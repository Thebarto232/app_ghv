-- Solicitud de vacaciones (formato Gestión Humana - Colbeef)
USE gestio_humana;

CREATE TABLE IF NOT EXISTS solicitud_vacaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cedula VARCHAR(50) NOT NULL,
    fecha_solicitud DATE NOT NULL,
    periodo_causado VARCHAR(100) NULL COMMENT 'Periodo de vacaciones causadas',
    dias_en_tiempo INT NULL COMMENT 'Días solicitados en tiempo',
    dias_compensados_dinero INT NULL COMMENT 'Días compensados en dinero',
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    fecha_regreso DATE NOT NULL,
    pago_anticipado TINYINT(1) NULL COMMENT '1=Sí, 0=No',
    solicitante_email VARCHAR(150) NULL,
    estado ENUM('PENDIENTE','APROBADO','RECHAZADO') NOT NULL DEFAULT 'PENDIENTE',
    observaciones TEXT NULL,
    resuelto_por VARCHAR(100) NULL,
    fecha_resolucion DATETIME NULL,
    INDEX idx_estado (estado),
    INDEX idx_id_cedula (id_cedula),
    INDEX idx_fecha_solicitud (fecha_solicitud),
    FOREIGN KEY (id_cedula) REFERENCES empleado(id_cedula) ON DELETE CASCADE
) ENGINE=InnoDB;
