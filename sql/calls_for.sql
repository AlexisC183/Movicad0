BEGIN;

INSERT INTO calls_for (
    title,
    initial_date,
    final_date,
    description,
    requirements,
    destination_country,
    publish_date,
    modification,
    administrative_id,
    deleted
) VALUES
(
    'Becas de movilidad académica 2026',
    '2026-01-15 00:00:00-08',
    '2026-03-15 23:59:59-07',
    'Convocatoria para estudiantes interesados en realizar una estancia académica internacional.',
    'Ser estudiante activo, tener promedio mínimo de 8.5 y presentar constancia de idioma.',
    'mexico',
    '2025-12-10 09:00:00-08',
    '2025-12-10 09:00:00-08',
    1,
    false
),
(
    'Intercambio estudiantil de primavera',
    '2026-02-01 00:00:00-08',
    '2026-04-10 23:59:59-07',
    'Programa de intercambio semestral con instituciones universitarias asociadas.',
    'Haber aprobado al menos el 50 por ciento de los créditos y contar con pasaporte vigente.',
    'mexico',
    '2026-01-05 10:30:00-08',
    '2026-01-12 11:00:00-08',
    2,
    false
),
(
    'Apoyo para investigación en el extranjero',
    '2026-03-01 00:00:00-08',
    '2026-05-30 23:59:59-07',
    'Apoyo económico para desarrollar proyectos de investigación en centros internacionales.',
    'Presentar protocolo de investigación, carta de aceptación y recomendación académica.',
    'otro',
    '2026-02-12 08:00:00-08',
    '2026-02-12 08:00:00-08',
    3,
    false
),
(
    'Estancias cortas de verano',
    '2026-04-01 00:00:00-07',
    '2026-05-20 23:59:59-07',
    'Convocatoria para cursos, talleres y estancias académicas durante el verano.',
    'Tener disponibilidad en verano y entregar carta de motivos.',
    'mexico',
    '2026-03-01 09:15:00-08',
    '2026-03-04 14:20:00-08',
    4,
    false
),
(
    'Prácticas profesionales internacionales',
    '2026-05-01 00:00:00-07',
    '2026-07-15 23:59:59-07',
    'Programa para realizar prácticas profesionales en organizaciones extranjeras.',
    'Contar con el 70 por ciento de los créditos, seguro médico y nivel intermedio de inglés.',
    'china',
    '2026-04-03 08:45:00-07',
    '2026-04-03 08:45:00-07',
    5,
    false
),
(
    'Movilidad virtual colaborativa',
    NULL,
    NULL,
    'Experiencia de colaboración virtual con estudiantes y docentes de otros países.',
    'Estar inscrito durante el periodo de la actividad y disponer de conexión a internet.',
    'mexico',
    '2026-01-20 12:00:00-08',
    '2026-01-20 12:00:00-08',
    6,
    false
),
(
    'Diplomado internacional en innovación educativa',
    '2026-02-10 00:00:00-08',
    '2026-03-31 23:59:59-07',
    'Diplomado dirigido a personal académico y administrativo interesado en innovación educativa.',
    'Presentar currículum, carta de exposición de motivos y autorización de la institución.',
    'mexico',
    '2026-01-25 09:30:00-08',
    '2026-02-02 16:10:00-08',
    7,
    false
),
(
    'Programa de doble titulación',
    '2026-01-05 00:00:00-08',
    '2026-02-28 23:59:59-08',
    'Proceso de selección para estudiantes que desean cursar un programa de doble titulación.',
    'Promedio mínimo de 9.0, nivel avanzado de idioma y entrevista de selección.',
    'mexico',
    '2025-11-18 10:00:00-08',
    '2025-12-02 10:00:00-08',
    8,
    false
),
(
    'Curso intensivo de lengua portuguesa',
    '2026-03-10 00:00:00-07',
    '2026-04-25 23:59:59-07',
    'Curso presencial de lengua portuguesa previo a una experiencia de movilidad.',
    'Tener disponibilidad de horario y completar el registro institucional.',
    'mexico',
    '2026-02-20 11:00:00-08',
    '2026-02-20 11:00:00-08',
    9,
    false
),
(
    'Red de proyectos comunitarios internacionales',
    '2026-06-01 00:00:00-07',
    '2026-08-01 23:59:59-07',
    'Apoyo para participar en proyectos de impacto social junto con comunidades internacionales.',
    'Presentar propuesta de proyecto, presupuesto preliminar y carta de compromiso.',
    'mexico',
    '2026-05-01 08:30:00-07',
    '2026-05-01 08:30:00-07',
    10,
    false
),
(
    'Seminario global de ciencias de datos',
    NULL,
    '2026-09-30 23:59:59-07',
    'Seminario híbrido sobre herramientas y tendencias actuales en ciencias de datos.',
    'Ser estudiante o personal académico y realizar el registro antes de la fecha límite.',
    'china',
    '2026-06-15 09:00:00-07',
    '2026-07-01 13:30:00-07',
    11,
    false
),
(
    'Beca para formación docente',
    '2026-04-15 00:00:00-07',
    '2026-06-15 23:59:59-07',
    'Beca destinada a docentes que realizarán formación especializada en el extranjero.',
    'Contar con nombramiento vigente, currículum actualizado y plan de transferencia de conocimientos.',
    'mexico',
    '2026-03-20 10:15:00-07',
    '2026-03-20 10:15:00-07',
    12,
    false
),
(
    'Encuentro juvenil de liderazgo',
    '2026-07-01 00:00:00-07',
    '2026-08-10 23:59:59-07',
    'Convocatoria para estudiantes que participarán en un encuentro internacional de liderazgo.',
    'Tener entre 18 y 28 años, promedio mínimo de 8.0 y presentar video de postulación.',
    'mexico',
    '2026-05-18 09:45:00-07',
    '2026-05-18 09:45:00-07',
    13,
    false
),
(
    'Certificación internacional de competencias',
    '2026-02-20 00:00:00-08',
    '2026-04-05 23:59:59-07',
    'Apoyo para obtener certificaciones internacionales relacionadas con el área de estudio.',
    'Tener promedio mínimo de 8.0 y entregar comprobante de inscripción al examen.',
    'otro',
    '2026-01-30 08:20:00-08',
    '2026-02-01 09:00:00-08',
    14,
    false
),
(
    'Misiones académicas de tecnología',
    '2026-08-01 00:00:00-07',
    '2026-09-20 23:59:59-07',
    'Estancias de una semana en empresas e instituciones tecnológicas internacionales.',
    'Ser estudiante de área tecnológica, contar con pasaporte y carta de recomendación.',
    'china',
    '2026-06-25 10:00:00-07',
    '2026-06-25 10:00:00-07',
    15,
    false
),
(
    'Voluntariado académico intercultural',
    NULL,
    NULL,
    'Participación en actividades de voluntariado con enfoque académico e intercultural.',
    'Completar la capacitación inicial y presentar carta de compromiso.',
    'mexico',
    '2026-02-05 12:30:00-08',
    '2026-02-05 12:30:00-08',
    16,
    false
),
(
    'Intercambio de investigadores visitantes',
    '2026-05-10 00:00:00-07',
    '2026-07-31 23:59:59-07',
    'Convocatoria para investigadores que recibirán una estancia en universidades asociadas.',
    'Contar con grado de maestría o doctorado y proyecto de investigación definido.',
    'otro',
    '2026-04-10 09:10:00-07',
    '2026-04-10 09:10:00-07',
    17,
    false
),
(
    'Taller internacional de emprendimiento',
    '2026-03-05 00:00:00-08',
    '2026-04-18 23:59:59-07',
    'Taller práctico para desarrollar proyectos de emprendimiento con alcance internacional.',
    'Presentar una idea de negocio y asistir a todas las sesiones programadas.',
    'mexico',
    '2026-02-10 11:20:00-08',
    '2026-02-10 11:20:00-08',
    18,
    false
),
(
    'Programa de arte y patrimonio cultural',
    '2026-09-01 00:00:00-07',
    '2026-10-15 23:59:59-07',
    'Movilidad para estudiantes de artes, diseño y patrimonio cultural.',
    'Presentar portafolio, carta de motivos y constancia de estudios.',
    'china',
    '2026-07-15 08:40:00-07',
    '2026-07-15 08:40:00-07',
    19,
    false
),
(
    'Foro internacional de sostenibilidad',
    '2026-04-20 00:00:00-07',
    '2026-06-01 23:59:59-07',
    'Apoyo para asistir al foro internacional sobre sostenibilidad y cambio climático.',
    'Tener participación comprobable en proyectos ambientales y presentar carta de motivos.',
    'mexico',
    '2026-03-15 09:00:00-07',
    '2026-03-15 09:00:00-07',
    20,
    false
);

update calls_for set administrative_id = 1 where id = 3;
COMMIT;

-- For AI
/*create table calls_for (
    call_for_id bigserial primary key,

    -- key is a random hexadecimal number string of length 32
    key char(32) not null collate case_accent_insensitive
        unique,

    title varchar(200) not null collate case_accent_insensitive
        check (length(title) > 0),
    
    -- initial_date must be less than final_date;
    -- any or both dates can be null
    initial_date timestamp with time zone,
    final_date timestamp with time zone,

    description text not null collate case_accent_insensitive,
    requirements text not null collate case_accent_insensitive,
    publish_date timestamp with time zone not null,
    modification timestamp with time zone not null,

    -- valid ids: between 1 and 25
    administrative_id bigint not null
        references administratives(user_id),

    deleted boolean not null
);

-- repeated call_for_ids are ok (one call_for having multiple destination_countries)
create table destination_countries (
    call_for_id bigint not null
        references calls_for(call_for_id),

    -- valid ids: between 1 and 226
    country_id bigint not null
        references countries(country_id),

    deleted boolean not null,
    primary key (call_for_id, country_id)
);*/

