--SOLO EJECUTAR UNA VEZ O PUEDE CAUSAR DUPLUICIDAD DE DATOS
ALTER TABLE usuario DROP CONSTRAINT IF EXISTS usuario_username_key;

--START TRIGGER
CREATE OR REPLACE FUNCTION crear_perfil_si_cuenta_activa()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo actuar si el estado cambia a '2'
    IF NEW.estadocuenta = '2' THEN

        -- Verificar si ya existe un perfil asociado
        IF NOT EXISTS (
            SELECT 1 FROM perfil WHERE usuario_id = NEW.usuario_id
        ) THEN
            INSERT INTO perfil (usuario_id, programa_academico_id, fecharegistro)
            VALUES (NEW.usuario_id, NULL, NOW());
        END IF;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_crear_perfil ON usuario;

CREATE TRIGGER trigger_crear_perfil
AFTER UPDATE OF estadocuenta
ON usuario
FOR EACH ROW
EXECUTE FUNCTION crear_perfil_si_cuenta_activa();
--END TRIGGER

ALTER TABLE genero
ALTER COLUMN fecha_creacion SET DEFAULT NOW();

ALTER TABLE programa
ALTER COLUMN fecha_creacion SET DEFAULT NOW();

ALTER TABLE ubicacion
ALTER COLUMN fecha_creacion SET DEFAULT NOW();

INSERT INTO genero(descripcion)
VALUES
('Masculino'),
('Femenino'),
('Otro');

INSERT INTO programa (descripcion) VALUES
('Artes Visuales'),
('Comunicación Social'),
('Derecho'),
('Filosofía'),
('Música'),
('Licenciatura en Educación Artística'),
('Medicina Veterinaria'),
('Zootecnia'),
('Ingeniería Agronómica'),
('Biología'),
('Matemática Aplicada'),
('Física'),
('Geología'),
('Microbiología'),
('Química'),
('Administración de Empresas'),
('Contaduría Pública'),
('Economía'),
('Licenciatura en Ciencias Sociales'),
('Licenciatura en Educación Física, Recreación y Deportes'),
('Licenciatura en Humanidades y Lengua Castellana'),
('Licenciatura en Educación Infantil'),
('Licenciatura en Lenguas Extranjeras Inglés–Francés'),
('Arquitectura'),
('Diseño Industrial'),
('Ingeniería Ambiental'),
('Ingeniería Civil'),
('Ingeniería de Alimentos'),
('Ingeniería de Sistemas'),
('Ingeniería Eléctrica'),
('Ingeniería Electrónica'),
('Ingeniería en Telecomunicaciones'),
('Ingeniería Industrial'),
('Ingeniería Mecánica'),
('Ingeniería Mecatrónica'),
('Ingeniería Química'),
('Bacteriología y Laboratorio Clínico'),
('Enfermería'),
('Fisioterapia'),
('Fonoaudiología'),
('Medicina'),
('Nutrición y Dietética'),
('Psicología'),
('Terapia Ocupacional'),
-- Registros adicionales solicitados
('Posgrado'),
('Egresado'),
('Otro');

insert into ubicacion(descripcion)
values
('Pamplona'),
('Cucuta'),
('Otro');


