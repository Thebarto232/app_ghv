-- Vincular cada usuario con su ficha de empleado (id_cedula) para que puedan
-- solicitar permisos y vacaciones "para sí mismos" (el formulario los identifica por id_cedula).
-- Reemplaza cada placeholder por la cédula real (debe existir en la tabla empleado).

USE gestio_humana;

-- US-0003 gestor.contratacion@colbeef.com (GESTOR DE CONTRATACION)
UPDATE usuario SET id_cedula = 'CEDULA_US0003' WHERE id_user = 'US-0003';

-- US-0004 coordinacion.gestionhumana@colbeef.com (COORD. GH)
UPDATE usuario SET id_cedula = 'CEDULA_US0004' WHERE id_user = 'US-0004';

-- US-0005 bienestarsocial@colbeef.com (BIENESTAR SOCIAL)
UPDATE usuario SET id_cedula = 'CEDULA_US0005' WHERE id_user = 'US-0005';

-- US-0006 gestionhumana@colbeef.com (GESTOR DE NOMINA)
UPDATE usuario SET id_cedula = 'CEDULA_US0006' WHERE id_user = 'US-0006';

-- US-0007 Aux.siso@colbeef.com
UPDATE usuario SET id_cedula = 'CEDULA_US0007' WHERE id_user = 'US-0007';

-- US-0008 Siso@colbeef.com
UPDATE usuario SET id_cedula = 'CEDULA_US0008' WHERE id_user = 'US-0008';

-- US-0009 practicante.siso@colbeef.com
UPDATE usuario SET id_cedula = 'CEDULA_US0009' WHERE id_user = 'US-0009';

-- US-0010 tecnologia@colbeef.com (ADMIN)
UPDATE usuario SET id_cedula = 'CEDULA_US0010' WHERE id_user = 'US-0010';

-- Verificación (descomenta y ejecuta después de reemplazar las cédulas):
-- SELECT id_user, nombre, email, rol, id_cedula FROM usuario WHERE id_user IN ('US-0003','US-0004','US-0005','US-0006','US-0007','US-0008','US-0009','US-0010');
