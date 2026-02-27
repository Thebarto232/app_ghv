-- ============================================================
-- GESTIÓN HUMANA - Script de creación de BD
-- ============================================================

-- ************************************************************
-- PASO 1: Ejecutar SOLO estas 4 líneas como usuario ROOT
-- (Clic derecho > Run Selected en MySQL Workbench)
-- ************************************************************
-- CREATE DATABASE IF NOT EXISTS gestio_humana CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- CREATE USER IF NOT EXISTS 'gh_admin'@'localhost' IDENTIFIED BY 'GH_2026$ecure';
-- GRANT ALL PRIVILEGES ON gestio_humana.* TO 'gh_admin'@'localhost';
-- FLUSH PRIVILEGES;

-- ************************************************************
-- PASO 2: Desde aquí ejecutar con usuario gh_admin o root
-- ************************************************************

USE gestio_humana;

-- ============================================================
-- TABLAS DE REFERENCIA / CATÁLOGOS
-- ============================================================

CREATE TABLE IF NOT EXISTS rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_documento (
    id_tipo_documento VARCHAR(50) PRIMARY KEY,
    tipo_documento VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nivel_educativo (
    id_nivel VARCHAR(50) PRIMARY KEY,
    nivel VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS profesion (
    id_profesion VARCHAR(100) PRIMARY KEY,
    profesion VARCHAR(200) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS eps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fondo_pensiones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motivo_retiro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_retiro VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS departamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    presupuestados INT DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS area (
    id INT AUTO_INCREMENT PRIMARY KEY,
    departamento_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    presupuestados INT DEFAULT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
    UNIQUE KEY uk_area_depto (departamento_id, nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS perfil_ocupacional (
    id_perfil VARCHAR(50) PRIMARY KEY,
    area_id INT NOT NULL,
    perfil_ocupacional VARCHAR(200) NOT NULL,
    presupuestados INT DEFAULT NULL,
    FOREIGN KEY (area_id) REFERENCES area(id)
) ENGINE=InnoDB;

-- ============================================================
-- TABLAS DE LA APLICACIÓN
-- ============================================================

CREATE TABLE IF NOT EXISTS menu (
    id_menu VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    vista VARCHAR(100),
    imagen VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario (
    id_user VARCHAR(20) PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(256) DEFAULT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    acciones VARCHAR(100)
) ENGINE=InnoDB;

-- ============================================================
-- TABLA PRINCIPAL DE EMPLEADOS (DBase)
-- ============================================================

CREATE TABLE IF NOT EXISTS empleado (
    id_cedula VARCHAR(50) PRIMARY KEY,
    apellidos_nombre VARCHAR(200) NOT NULL,
    lugar_expedicion VARCHAR(150),
    fecha_expedicion VARCHAR(20),
    departamento VARCHAR(100),
    area VARCHAR(100),
    id_perfil_ocupacional VARCHAR(50),
    fecha_ingreso VARCHAR(20),
    sexo CHAR(1),
    rh VARCHAR(5),
    direccion_residencia VARCHAR(250),
    barrio_residencia VARCHAR(100),
    ciudad_residencia VARCHAR(100),
    telefono VARCHAR(30),
    celular VARCHAR(30),
    direccion_email VARCHAR(200),
    eps VARCHAR(100),
    fondo_pensiones VARCHAR(100),
    fecha_nacimiento VARCHAR(20),
    hijos VARCHAR(5),
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    tipo_documento VARCHAR(50),
    nivel_educativo VARCHAR(50),
    profesion VARCHAR(100),
    contacto_emergencia VARCHAR(200),
    telefono_contacto VARCHAR(30),
    parentezco VARCHAR(100)
) ENGINE=InnoDB;

-- ============================================================
-- HIJOS DE EMPLEADOS
-- ============================================================

CREATE TABLE IF NOT EXISTS hijo (
    id_hijo VARCHAR(50) PRIMARY KEY,
    identificacion_hijo VARCHAR(50),
    id_cedula VARCHAR(50) NOT NULL,
    apellidos_nombre VARCHAR(200) NOT NULL,
    fecha_nacimiento VARCHAR(20),
    sexo CHAR(1),
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    INDEX idx_hijo_cedula (id_cedula)
) ENGINE=InnoDB;

-- ============================================================
-- EMPLEADOS RETIRADOS
-- ============================================================

CREATE TABLE IF NOT EXISTS retirado (
    id_retiro VARCHAR(50) PRIMARY KEY,
    id_cedula VARCHAR(50) NOT NULL,
    apellidos_nombre VARCHAR(200) NOT NULL,
    departamento VARCHAR(100),
    area VARCHAR(100),
    id_perfil_ocupacional VARCHAR(50),
    fecha_ingreso VARCHAR(20),
    fecha_retiro VARCHAR(20),
    dias_laborados INT,
    tipo_retiro VARCHAR(100),
    motivo TEXT,
    INDEX idx_retirado_cedula (id_cedula)
) ENGINE=InnoDB;

-- ============================================================
-- INSERTAR DATOS DE CATÁLOGOS
-- ============================================================

-- Roles
INSERT INTO rol (nombre) VALUES
    ('ADMIN'),
    ('BIENESTAR SOCIAL'),
    ('COORD. GH'),
    ('GESTOR DE CONTRATACION'),
    ('GESTOR DE NOMINA'),
    ('GESTOR SST');

-- Tipos de Documento
INSERT INTO tipo_documento (id_tipo_documento, tipo_documento) VALUES
    ('TI', 'TARJETA DE IDENTIDAD'),
    ('CC', 'CEDULA DE CIUDADANIA'),
    ('1abf0882', 'PT'),
    ('36d4a37c', 'PERMISO POR PROTECCION TEMPORAL');

-- Niveles Educativos
INSERT INTO nivel_educativo (id_nivel, nivel) VALUES
    ('PR', 'PRIMARIA'),
    ('BC', 'BACHILLER'),
    ('TC', 'TECNICO'),
    ('TG', 'TECNOLOGO'),
    ('PRF', 'PROFESIONAL'),
    ('2d1c8003', 'PRIMARIA'),
    ('a3ebf14f', 'PRIMARIA'),
    ('f77b9245', 'POSGRADO');

-- EPS
INSERT INTO eps (nombre) VALUES
    ('SURA'),
    ('NUEVA EPS'),
    ('SANITAS'),
    ('SALUD TOTAL'),
    ('FAMISANAR'),
    ('COOSALUD'),
    ('SALUD MIA'),
    ('SAVIA SALUD EPS'),
    ('ASMET SALUD'),
    ('EMMSANAR'),
    ('ALIANZA MEDELLIN ANTIOQUI EPS'),
    ('CAJACOPI'),
    ('REGIMEN EXCEPCION'),
    ('AVANZAR MEDICO'),
    ('COMPENSAR'),
    ('MUTUAL SER'),
    ('ADRES'),
    ('SURAMERICANA S.A');

-- Fondos de Pensiones
INSERT INTO fondo_pensiones (nombre) VALUES
    ('COLFONDOS'),
    ('COLPENSIONES'),
    ('PORVENIR'),
    ('PROTECCION'),
    ('N/A'),
    ('OLD MUTUAL');

-- Motivos de Retiro
INSERT INTO motivo_retiro (tipo_retiro) VALUES
    ('FINALIZACION PRACTICA'),
    ('RENUNCIA VOLUNTARIA'),
    ('TERMINACION CON JUSTA CAUSA'),
    ('TERMINACION SIN JUSTA CAUSA'),
    ('TERMINACION EN PERIODO DE PRUEBA');

-- Departamentos
INSERT INTO departamento (nombre, presupuestados) VALUES
    ('CORPORATIVOS', 2),
    ('DESPOSTE', 3),
    ('DPTO ADMON Y FINANCIERO', 10),
    ('DPTO CALIDAD', 8),
    ('DPTO COMERCIAL', NULL),
    ('DPTO DE OPERACIONES', 28),
    ('DPTO JURIDICO Y GESTION HUMANA', 12),
    ('PLANEACION Y PROYECTOS', NULL);

-- Áreas
INSERT INTO area (departamento_id, nombre, presupuestados) VALUES
    ((SELECT id FROM departamento WHERE nombre='CORPORATIVOS'), 'GERENCIA', 2),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'CALIDAD DESPOSTE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'L&D DESPOSTE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'LAVANDERIA DESPOSTE', 1),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'LINEA DESPOSTE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'LOGISTICA DESPOSTE', 9),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'MTTO DESPOSTE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'PORCIONADO', NULL),
    ((SELECT id FROM departamento WHERE nombre='DESPOSTE'), 'PRODUCCION DESPOSTE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'ADMINISTRACION', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'COMPRAS', 3),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'CONTABILIDAD', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'DIRECCION ADMON Y FINANCIERA', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'TESORERIA', 10),
    ((SELECT id FROM departamento WHERE nombre='DPTO ADMON Y FINANCIERO'), 'CONTROL INTERNO', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'AMBIENTAL', 3),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'DIRECCION DPTO CALIDAD', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'INVIMA', 3),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'LAVANDERIA', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'LIMPIEZA Y DESINFECCION', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'PTAP', 3),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'PTAR', 8),
    ((SELECT id FROM departamento WHERE nombre='DPTO CALIDAD'), 'JARDINERIA', 2),
    ((SELECT id FROM departamento WHERE nombre='DPTO COMERCIAL'), 'DIRECCION DPTO COMERCIAL', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO COMERCIAL'), 'FOMENTO GANADERO', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO COMERCIAL'), 'MERCADEO', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'DIRECCION PRODUCCION', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'LINEA DE SACRIFICIO', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'LOGISTICA', 28),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'MANTENIMIENTO', 20),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'RECEPCION Y PESAJE', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO DE OPERACIONES'), 'SUBPRODUCTOS COMESTIBLES', NULL),
    ((SELECT id FROM departamento WHERE nombre='DPTO JURIDICO Y GESTION HUMANA'), 'ACCIONISTAS', 1),
    ((SELECT id FROM departamento WHERE nombre='DPTO JURIDICO Y GESTION HUMANA'), 'DIRECCION DPTO JURIDICO Y GESTION HUMANA', 3),
    ((SELECT id FROM departamento WHERE nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTION HUMANA', 12),
    ((SELECT id FROM departamento WHERE nombre='DPTO JURIDICO Y GESTION HUMANA'), 'TECNOLOGIA', 4),
    ((SELECT id FROM departamento WHERE nombre='PLANEACION Y PROYECTOS'), 'PLANEACION', 3);

-- Menú
INSERT INTO menu (id_menu, nombre, vista, imagen) VALUES
    ('bedeaffb', 'Cumpleaños', 'Date Cumpleaños', 'Menu_Images/bedeaffb.Imagen.164538.jpg'),
    ('08ce0459', 'Aniversario Laboral', 'Date Cumpleaños Laboral', 'Menu_Images/08ce0459.Imagen.165430.jpg'),
    ('8d227f65', 'Áreas de Trabajo', 'View Áreas', 'Menu_Images/8d227f65.Imagen.165251.jpg'),
    ('0d64f1f1', 'EPS', 'EPS', 'Menu_Images/0d64f1f1.Imagen.165300.jpg'),
    ('a31b6092', 'Fondo de Pensiones', 'Fondo de Pensiones', 'Menu_Images/a31b6092.Imagen.165312.jpg'),
    ('b4aa163c', 'Dashboard', 'Dashboard', 'Menu_Images/b4aa163c.Imagen.165322.jpg');

-- Usuarios
INSERT INTO usuario (id_user, email, nombre, rol, estado, acciones) VALUES
    ('US-0001', 'coordinacion.logistico@colbeef.com', 'CJIMENEZ', 'ADMIN', TRUE, 'TODOS LOS CAMBIOS'),
    ('US-0002', 'cjimenez1408@gmail.com', 'Y2K', 'ADMIN', TRUE, 'TODOS LOS CAMBIOS'),
    ('US-0010', 'tecnologia@colbeef.com', 'DANIEL ALMEIDA', 'ADMIN', TRUE, 'TODOS LOS CAMBIOS'),
    ('US-0005', 'bienestarsocial@colbeef.com', 'BIENESTAR SOCIAL', 'BIENESTAR SOCIAL', TRUE, 'AGREGAR Y MODIFICAR'),
    ('US-0004', 'coordinacion.gestionhumana@colbeef.com', 'COORDINACIÓN GH', 'COORD. GH', TRUE, 'TODOS LOS CAMBIOS'),
    ('US-0003', 'gestor.contratacion@colbeef.com', 'GESTOR DE CONTRATACION', 'GESTOR DE CONTRATACION', TRUE, 'AGREGAR Y MODIFICAR'),
    ('US-0006', 'gestionhumana@colbeef.com', 'GERTOR DE NOMINA', 'GESTOR DE CONTRATACION', TRUE, 'AGREGAR Y MODIFICAR'),
    ('US-0007', 'Aux.siso@colbeef.com', 'AUXILIAR SST', 'GESTOR SST', TRUE, 'VISTA'),
    ('US-0008', 'Siso@colbeef.com', 'GESTOR SST', 'GESTOR SST', TRUE, 'VISTA'),
    ('US-0009', 'practicante.siso@colbeef.com', 'PRACTICANTE SISO', 'GESTOR SST', TRUE, 'VISTA');

-- Profesiones
INSERT INTO profesion (id_profesion, profesion) VALUES
    ('500a20a8', 'BACHILLER'),
    ('6f144e24', 'TECNICO SEGURIDAD OCUPACIONAL'),
    ('c3f1f995', 'TECNICO EN PRODUCCION AGROPECUARIA'),
    ('11eff05c', 'OPERARIO'),
    ('35953bab', 'TECNOLOGO INDUSTRIAL'),
    ('a43d5217', 'VETERINARIA Y ZOOTECNIA'),
    ('33d05455', 'ADMINISTRACION FINANCIERA'),
    ('8b666250', 'OPERARIO'),
    ('63c7cbb5', 'CONTADOR PUBLICO'),
    ('b8d95d42', 'TECNICO EN SISTEMAS'),
    ('76d5dd7d', 'TECNICO EN ASISTENCIA ADMINISTRATIVA- EN CURSO'),
    ('624d1205', 'TECNICO EN MANTENIMIENTO DE EQUIPOS DE COMPUTO'),
    ('7555dd38', 'MECANICA DENTAL'),
    ('c822daf6', 'TECNICO EN VENTAS DE PRODUCTOS Y SERVICIOS'),
    ('5cf95454', 'SISTEMAS'),
    ('0035dbba', 'ASISTENTE ADMINISTRATIVO'),
    ('f308c25e', 'TG ADMINISTRACION PROPIEDAD HORIZONTAL'),
    ('682ebb2e', 'PROCESAMIENTO DE ALIMENTOS'),
    ('d961ff2e', 'TECNICO EN SOLDADURA'),
    ('cdcb9c60', 'TECNICO EN ELECTRICIDAD'),
    ('b143673b', 'INGENIERO AMBIENTAL'),
    ('029d5a15', 'HSEQ'),
    ('90341ac5', 'AGROPECUARIO'),
    ('63d8b662', 'CONTROL DE CALIDAD DE ALIMENTOS'),
    ('46ed9a8c', 'MICROBIOLOGIA INDUSTRIAL'),
    ('3a0294a0', 'TECNOLOGO EN CONTABILIDAD Y FINANZAS'),
    ('3cb21113', 'ADMINISTRACION DE EMPRESAS'),
    ('3bf46957', 'ADMINISTRADOR DE EMPRESAS'),
    ('e6d81837', 'TECNOLOGO EN PROCESAMIENTO DE ALIMENTOS'),
    ('349a1c16', 'MENSAJERO'),
    ('7e5a9095', 'TECNOLOGA EN GESTION DEL TALENTO HUMANO'),
    ('d22946c2', 'PRODUCCION INDUSTRIAL'),
    ('a2599b12', 'CONTABILIDAD'),
    ('d0cc67af', 'TECNOLOGO EN SALUD OCUPACIONAL'),
    ('813e7d0f', 'TECNOLOGO EN ALIMENTOS'),
    ('c735d37a', 'ASISTENCIA JURIDICA'),
    ('b67f58e9', 'TECNOLOGA'),
    ('f721a347', 'TECNOLOGO EN GESTION AGROINDUSTRIAL'),
    ('a6104fa3', 'TECNOLOGA AGROINDUSTRIAL'),
    ('096be04c', 'ADMINISTRACION NEGOCIOS INTERNACIONALES'),
    ('addd14ef', 'GESTION EMPRESARIAL'),
    ('3b60f410', 'ABOGADA'),
    ('2e2d875f', 'TECNOLOGO INDUSTRIAL'),
    ('1ed77485', 'TECNICO EN GESTION DE NEGOCIOS'),
    ('INGENIERO DE TELECOMUNICACIONES', 'INGENIERO DE TELECOMUNICACIONES'),
    ('bac99bb0', 'MEDICO VETERINARIO Y ZOOTECNISTA'),
    ('c23f6c51', 'MECANICA INDUSTRIAL'),
    ('5a2fd220', 'TECNOLOGO ELECTROMECANICO'),
    ('71ac1e9e', 'TECNOLOGO EN MANEJO DE GASES'),
    ('1b88bea1', 'TECNICO EN REFRIGERACION'),
    ('89f07a3e', 'INGENIERO ELECTROMECANICO'),
    ('c2ff4715', 'APRENDIZ MTTO'),
    ('e62f250a', 'TECNOLOGO ELECTROMECANICO'),
    ('c5c17c3d', 'TECNOLOGO ELECTROMECANICO'),
    ('835e42a9', 'CORRALERO'),
    ('a5b464d0', 'TECNOLOGO EN SISTEMAS AGROPECUARIOS ECOLOGICOS'),
    ('987caf28', 'TECNOLOGA EN GESTION EMPRESAS AGROPECUARIAS'),
    ('9e2d2550', 'ADMINISTRACION FINANCIERA Y SISTEMAS'),
    ('8f75aa83', 'CONTADORA PUBLICA'),
    ('993dd4ed', 'TECNICO EN CONTABILIDAD'),
    ('683ab311', 'TECNICO EN ADMINISTRACION FINANCIERA'),
    ('677e48ce', 'TECNOLOGIA EN AMBIENTAL'),
    ('a29817da', 'TECNICO EN INSTALACION Y MTTO REDES INALAMBRICAS'),
    ('ab85f065', 'TECNICO EN SISTEMAS'),
    ('b9922bb3', 'TECNOLOGO EN SISTEMAS'),
    ('8dd7a290', 'TECNICO'),
    ('c04361b5', 'TECNOLOGIA EN OPERACION Y MTTO ELECTROMECANICO'),
    ('2bafacbf', 'GESTION BANCARIA Y FINANCIERA'),
    ('e8dcc63e', 'TECNOLOGO ELECTROMECANICO INDUSTRIAL'),
    ('eb56d56b', 'TECNICO'),
    ('be82eddc', 'TECNICO EN MERCADEO Y VENTAS'),
    ('e8af5ddc', 'TECNICO EN MTTO EQUIPOS COMPUTO'),
    ('4d86e442', 'TECNOLOGIA EN GESTION EMPRESARIAL'),
    ('a90aa75f', 'GESTION LOGISTICA'),
    ('870b351e', 'TECNOLOGO EN GESTION AGROINDUSTRIAL'),
    ('3ab2750c', 'TECNOLOGO ELECTROMECANICO'),
    ('60d88687', 'TECNOLOGO'),
    ('c9bbd0db', 'ELECTROMECANICA INDUSTRIAL'),
    ('a1d361d2', 'TECNICO'),
    ('46e533ee', 'POSGRADO'),
    ('f52c43dd', 'POSGRADO GERENCIA TRIBUTARIA'),
    ('f74bea41', 'PROGRAMACION SOFTWARE'),
    ('8112f1a9', 'QUIMICO'),
    ('c42b26c1', 'MICROBIOLOGIA DE ALIMENTOS'),
    ('3e28cb99', 'PRODUCCION INDUSTRIAL'),
    ('c284f27b', 'MECANICO DE MAQUINARIA INDUSTRIAL'),
    ('0f451a7d', 'INGENIERIA FINANCIERA'),
    ('fed51d79', 'IMPLEMENTACION DE INFRAESTRUCTURA TIC'),
    ('90f07dfc', 'MECATRONICA'),
    ('03fed764', 'ELECTRICIDAD INDUSTRIAL'),
    ('a58ad91b', 'FISIOTERAPEUTA ESP SST'),
    ('b8c16fe9', 'MANEJO DE RECURSOS AMBIENTALES'),
    ('13e3e2a2', 'PUBLICIDAD Y MERCADEO'),
    ('cb6dc57c', 'INGENIERA QUIMICA'),
    ('af9a4b65', 'TRABAJO SOCIAL'),
    ('5c29808c', 'AUTOMATISMOS INDUSTRIALES'),
    ('39e009da', 'INGENIERO INDUSTRIAL'),
    ('0df71f02', 'DISEÑO GRAFICO'),
    ('5af4f04c', 'INGENIERO MECANICO'),
    ('4c2d2811', 'INSTRUMENTACION INDUSTRIAL'),
    ('59962633', 'GESTION DOCUMENTAL'),
    ('95827308', 'GESTION AGROINDUSTRIAL'),
    ('57317497', 'INGENIERO FINANCIERO'),
    ('95f75c67', 'ECONOMIA'),
    ('fe4adbec', 'ADMINISTRACION EN SALUD'),
    ('d2fa8908', 'PSICOLOGO'),
    ('2f44b392', 'GESTION AGROEMPRESARIAL'),
    ('5ecf81da', 'INGENIERO DE SISTEMAS'),
    ('3af0395f', 'TECNOLOGO EN GESTION EMPRESARIAL');

-- Perfiles Ocupacionales
INSERT INTO perfil_ocupacional (id_perfil, area_id, perfil_ocupacional, presupuestados) VALUES
    ('1', (SELECT id FROM area WHERE nombre='GERENCIA'), 'ASISTENTE DE GERENCIA', 1),
    ('2', (SELECT id FROM area WHERE nombre='GERENCIA'), 'GERENTE GENERAL', 1),
    ('3', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CALIDAD DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR DE CALIDAD', NULL),
    ('4', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CALIDAD DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE CALIDAD LINEA BENEFICIO', NULL),
    ('5', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='L&D DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR DE LIMPIEZA Y DESINFECCION DESPOSTE', NULL),
    ('6', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LAVANDERIA DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR DE LAVANDERIA', 1),
    ('7', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LINEA DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR DE DESPOSTE', NULL),
    ('8', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR DE LOGISTICA', 8),
    ('9', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE LOGISTICA', 1),
    ('10', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PORCIONADO' AND d.nombre='DESPOSTE'), 'AUXILIAR DE PORCIONADO', 5),
    ('11', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PRODUCCION DESPOSTE' AND d.nombre='DESPOSTE'), 'COORDINADOR DE DESPOSTE', 1),
    ('12', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PRODUCCION DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE DESPOSTE', 1),
    ('13', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PRODUCCION DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE INFORMACION', 1),
    ('14', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PRODUCCION DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE PORCIONADO', 1),
    ('15', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='ADMINISTRACION' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'COORDINADOR ADMINISTRATIVO', NULL),
    ('16', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'AUXILIAR DE ALMACEN', NULL),
    ('17', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR DE COMPRAS', NULL),
    ('18', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTABILIDAD' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'APRENDIZ SENA CONTABILIDAD', NULL),
    ('19', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTABILIDAD' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'AUXILIAR DE CONTABILIDAD', NULL),
    ('20', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTABILIDAD' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'COORDINADOR CONTABLE', NULL),
    ('21', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTABILIDAD' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR CONTABLE', NULL),
    ('22', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTABILIDAD' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR NIIF', NULL),
    ('23', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION ADMON Y FINANCIERA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GERENTE ADMINISTRATIVO Y FINANCIERO', NULL),
    ('24', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'AUXILIAR DE CAJA', NULL),
    ('25', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'AUXILIAR DE FACTURACION, PLANILLAJE Y CARTERA', NULL),
    ('26', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'COORDINADOR DE TESORERIA Y CARTERA', NULL),
    ('27', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR DE CARTERA', NULL),
    ('28', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR DE FACTURACION Y PLANILLAJE', NULL),
    ('29', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='AMBIENTAL' AND d.nombre='DPTO CALIDAD'), 'COORDINADOR AMBIENTAL', NULL),
    ('30', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='AMBIENTAL' AND d.nombre='DPTO CALIDAD'), 'GESTOR AMBIENTAL', NULL),
    ('31', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'APRENDIZ SENA CALIDAD', NULL),
    ('32', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'COORDINADOR DE CALIDAD', NULL),
    ('33', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'GERENTE DE CALIDAD', NULL),
    ('34', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'PASANTE UNIVERSITARIO MVZ', NULL),
    ('35', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LIMPIEZA Y DESINFECCION' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE LIMPIEZA Y DESINFECCION', NULL),
    ('36', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LIMPIEZA Y DESINFECCION' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE LIMPIEZA Y DESINFECCION DE BENEFICIO', NULL),
    ('37', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LIMPIEZA Y DESINFECCION' AND d.nombre='DPTO CALIDAD'), 'COORDINADOR DE LIMPIEZA Y DESINFECCION', NULL),
    ('38', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PTAP' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE PTAP', NULL),
    ('39', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PTAR' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE JARDINERIA', NULL),
    ('40', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PTAR' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR PTAR', NULL),
    ('41', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'DIRECTOR COMERCIAL', NULL),
    ('42', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='FOMENTO GANADERO' AND d.nombre='DPTO COMERCIAL'), 'COORDINADOR DE FOMENTO GANADERO', NULL),
    ('43', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MERCADEO' AND d.nombre='DPTO COMERCIAL'), 'AUXILIAR COMERCIAL', 1),
    ('44', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MERCADEO' AND d.nombre='DPTO COMERCIAL'), 'COORDINADOR DE MERCADEO', NULL),
    ('45', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MERCADEO' AND d.nombre='DPTO COMERCIAL'), 'GESTOR DE CARNES COLBEEF', NULL),
    ('46', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MERCADEO' AND d.nombre='DPTO COMERCIAL'), 'GESTOR REGIONAL', NULL),
    ('47', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION PRODUCCION' AND d.nombre='DPTO DE OPERACIONES'), 'APRENDIZ SENA ADMINISTRATIVO', NULL),
    ('48', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION PRODUCCION' AND d.nombre='DPTO DE OPERACIONES'), 'DIRECTOR DE OPERACIONES', 1),
    ('49', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LINEA DE SACRIFICIO' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE LINEA', NULL),
    ('50', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LINEA DE SACRIFICIO' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR LINEA DE BENEFICIO', NULL),
    ('51', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE LOGISTICA', 26),
    ('53', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA' AND d.nombre='DPTO DE OPERACIONES'), 'COORDINADOR DE LOGISTICA', 1),
    ('54', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MANTENIMIENTO' AND d.nombre='DPTO DE OPERACIONES'), 'APRENDIZ SENA MANTENIMIENTO', 4),
    ('55', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MANTENIMIENTO' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE MANTENIMIENTO', NULL),
    ('56', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MANTENIMIENTO' AND d.nombre='DPTO DE OPERACIONES'), 'COORDINADOR DE MANTENIMIENTO', 1),
    ('57', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MANTENIMIENTO' AND d.nombre='DPTO DE OPERACIONES'), 'GESTOR DE MANTENIMIENTO', NULL),
    ('58', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='RECEPCION Y PESAJE' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE BASCULA', NULL),
    ('59', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='RECEPCION Y PESAJE' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE CORRALES', NULL),
    ('60', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='RECEPCION Y PESAJE' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE INSPECCION VETERINARIA', NULL),
    ('61', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='RECEPCION Y PESAJE' AND d.nombre='DPTO DE OPERACIONES'), 'COORDINADOR DE CORRALES', NULL),
    ('62', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='SUBPRODUCTOS COMESTIBLES' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE PRODUCTOS CARNICOS COMESTIBLES', NULL),
    ('63', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='SUBPRODUCTOS COMESTIBLES' AND d.nombre='DPTO DE OPERACIONES'), 'AUXILIAR DE SUBPRODUCTOS', NULL),
    ('64', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='SUBPRODUCTOS COMESTIBLES' AND d.nombre='DPTO DE OPERACIONES'), 'COORDINADOR DE PRODUCTOS CARNICOS COMESTIBLES', NULL),
    ('65', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='ACCIONISTAS' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR DE ACCIONISTAS', NULL),
    ('66', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO JURIDICO Y GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'COORDINADOR JURIDICO', NULL),
    ('67', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO JURIDICO Y GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GERENTE JURIDICA Y DE GESTION HUMANA', NULL),
    ('68', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ SENA - SISO', NULL),
    ('69', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR DE MENSAJERIA', NULL),
    ('70', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR DE SERVICIOS GENERALES', NULL),
    ('71', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR SISO', NULL),
    ('72', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'COORDINADORA DE GESTION HUMANA', NULL),
    ('73', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTOR DE BIENESTAR COMUNICACION Y CAPACITACION', NULL),
    ('74', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTOR DE CONTRATACION', NULL),
    ('75', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTOR DE SEGURIDAD Y SALUD EN EL TRABAJO', NULL),
    ('76', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTOR DE TALENTO HUMANO', NULL),
    ('77', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'SUPERNUMERARIO', NULL),
    ('78', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TECNOLOGIA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ SENA - TIC', NULL),
    ('79', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TECNOLOGIA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR TIC', NULL),
    ('80', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TECNOLOGIA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'COORDINADOR DE TIC', NULL),
    ('81', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PLANEACION' AND d.nombre='PLANEACION Y PROYECTOS'), 'AUXILIAR DE PLANEACION Y PROYECTOS', NULL),
    ('82', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PLANEACION' AND d.nombre='PLANEACION Y PROYECTOS'), 'DIRECTOR DE PLANEACION Y PROYECTOS', NULL),
    ('83', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PLANEACION' AND d.nombre='PLANEACION Y PROYECTOS'), 'GESTOR DE PLANEACION Y PROYECTOS', NULL),
    ('84', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA' AND d.nombre='DPTO DE OPERACIONES'), 'GESTOR DE LOGISTICA', 1),
    ('87', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'PENDIENTE POR ASIGNAR', NULL),
    ('240c11f2', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ SENA GH', 1),
    ('d2012dd2', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='AMBIENTAL' AND d.nombre='DPTO CALIDAD'), 'APRENDIZ SENA AMBIENTAL', 1),
    ('9c6b9261', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO JURIDICO Y GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ SENA JURIDICA', 1),
    ('83f47129', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO JURIDICO Y GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ JURIDICO', 1),
    ('9ecf802b', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GESTION HUMANA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'APRENDIZ GESTIÓN HUMANA', 1),
    ('351fac4d', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LINEA DE SACRIFICIO' AND d.nombre='DPTO DE OPERACIONES'), 'COORDINADOR DE LINEA', 1),
    ('786995f6', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CALIDAD DESPOSTE' AND d.nombre='DESPOSTE'), 'GESTOR DE CALIDAD DESPOSTE', 1),
    ('cbabdae1', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR CALIDAD', 2),
    ('25ed471d', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'GESTOR CALIDAD', 2),
    ('4bdd1f3d', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LAVANDERIA' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE LAVANDERÍA', 2),
    ('8b67fb22', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TECNOLOGIA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'GESTOR TIC', 1),
    ('87ed6334', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION PRODUCCION' AND d.nombre='DPTO DE OPERACIONES'), 'GESTOR DE INFORMACION', 1),
    ('0c9da5ed', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'COORDINADOR DE COMPRAS', 1),
    ('f8986cc6', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='INVIMA' AND d.nombre='DPTO CALIDAD'), 'AUXILIAR DE CALIDAD', 3),
    ('2c34b18e', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='JARDINERIA' AND d.nombre='DPTO CALIDAD'), 'JARDINERO', 1),
    ('e5694694', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='INVIMA' AND d.nombre='DPTO CALIDAD'), 'PASANTE UNIVERSITARIO MVZ', 3),
    ('41670931', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'ANALISTA DE INFORMACION', 1),
    ('3e00f8a5', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CALIDAD DESPOSTE' AND d.nombre='DESPOSTE'), 'PASANTE UNIVERSITARIO MVZ', 1),
    ('68cde94d', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MTTO DESPOSTE' AND d.nombre='DESPOSTE'), 'AUXILIAR MANTENIMIENTO', 1),
    ('41a9bff6', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='MTTO DESPOSTE' AND d.nombre='DESPOSTE'), 'APRENDIZ SENA MANTENIMIENTO', 1),
    ('a083d707', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'EJECUTIVO DE CUENTAS CLAVES', 1),
    ('e1d2d4d3', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'VENDEDOR', 1),
    ('d7c1b17a', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'ANALISTA DE MERCADEO Y COMUNICACIONES', 1),
    ('00da28eb', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TECNOLOGIA' AND d.nombre='DPTO JURIDICO Y GESTION HUMANA'), 'AUXILIAR DE GESTION DOCUMENTAL', 1),
    ('50234612', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION PRODUCCION' AND d.nombre='DPTO DE OPERACIONES'), 'PRACTICANTE DE MTTO', 1),
    ('be2fa828', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA' AND d.nombre='DPTO DE OPERACIONES'), 'DIRECTOR DE LOGISTICA Y ABASTECIMIENTO', 1),
    ('ccca8d3e', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='RECEPCION Y PESAJE' AND d.nombre='DPTO DE OPERACIONES'), 'PRACTICANTE MVZ', 1),
    ('92b28c0b', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'GESTOR ADMINISTRATIVO', 1),
    ('94d07290', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO CALIDAD' AND d.nombre='DPTO CALIDAD'), 'ANALISTA DE SIG', 1),
    ('478dbeb1', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'APRENDIZ', 1),
    ('278a55f1', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='PRODUCCION DESPOSTE' AND d.nombre='DESPOSTE'), 'APRENDIZ', 1),
    ('de5dcdf3', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'ANALISTA PQRS', 1),
    ('c3261768', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION DPTO COMERCIAL' AND d.nombre='DPTO COMERCIAL'), 'EJECUTIVO COMERCIAL BENEFICIO', 1),
    ('c246e08e', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='LOGISTICA' AND d.nombre='DPTO DE OPERACIONES'), 'APRENDIZ SENA', 1),
    ('452351d8', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='TESORERIA' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'APRENDIZ SENA', 1),
    ('d3e61e7c', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='CONTROL INTERNO' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'PROFESIONAL CONTROL INTERNO', 1),
    ('702a408b', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='DIRECCION PRODUCCION' AND d.nombre='DPTO DE OPERACIONES'), 'LIDER DE PROYECTOS', 1),
    ('808d40f3', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='COMPRAS' AND d.nombre='DPTO ADMON Y FINANCIERO'), 'AUXILIAR DE MENSAJERIA', 1),
    ('25d60732', (SELECT a.id FROM area a JOIN departamento d ON a.departamento_id=d.id WHERE a.nombre='GERENCIA'), 'DIRECTOR DE SURTIDORES Y COMPRA DE GANADO', 1);

-- ============================================================
-- ÍNDICES ADICIONALES
-- ============================================================

CREATE INDEX idx_empleado_departamento ON empleado(departamento);
CREATE INDEX idx_empleado_area ON empleado(area);
CREATE INDEX idx_empleado_estado ON empleado(estado);
CREATE INDEX idx_empleado_nombre ON empleado(apellidos_nombre);
CREATE INDEX idx_retirado_tipo ON retirado(tipo_retiro);
CREATE INDEX idx_retirado_fecha ON retirado(fecha_retiro);
