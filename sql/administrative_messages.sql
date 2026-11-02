BEGIN;

INSERT INTO administrative_messages (
    subject,
    body,
    creation,
    sender_id,
    recipient_id,
    deleted
) VALUES
(
    'Reunión de coordinación semestral',
    'Buenos días. Se convoca a reunión de coordinación para revisar las actividades del próximo semestre.',
    '2026-01-08 09:00:00-08',
    1,
    2,
    false
),
(
    'Solicitud de actualización de datos',
    'Por favor, actualiza los datos de contacto de tu área antes del viernes.',
    '2026-01-10 11:15:00-08',
    2,
    5,
    false
),
(
    'Confirmación de presupuesto',
    'Se confirma la disponibilidad presupuestal para las actividades de movilidad académica.',
    '2026-01-13 08:40:00-08',
    3,
    1,
    false
),
(
    'Recordatorio de entrega de informes',
    'Les recordamos que el informe mensual debe entregarse a más tardar el día 25.',
    '2026-01-15 14:20:00-08',
    4,
    7,
    false
),
(
    'Invitación a capacitación',
    'Se adjunta la invitación a la capacitación sobre procesos de internacionalización.',
    '2026-01-18 10:00:00-08',
    5,
    9,
    false
),
(
    'Validación de convocatoria',
    'La convocatoria fue revisada y puede continuar con el proceso de publicación.',
    '2026-01-20 16:30:00-08',
    6,
    3,
    false
),
(
    'Cambio de fecha para la sesión',
    'La sesión programada para mañana se moverá al jueves a las 10:00 horas.',
    '2026-01-22 13:10:00-08',
    7,
    12,
    false
),
(
    'Consulta sobre convenio internacional',
    '¿Podrían compartir el estado actual del convenio con la institución asociada?',
    '2026-01-25 09:35:00-08',
    8,
    4,
    false
),
(
    'Aprobación de propuesta de movilidad',
    'La propuesta presentada ha sido aprobada. Favor de iniciar los trámites correspondientes.',
    '2026-01-28 15:45:00-08',
    9,
    15,
    false
),
(
    'Documentación pendiente',
    'Falta recibir la carta de aceptación y la constancia de seguro médico.',
    '2026-02-01 08:25:00-08',
    10,
    6,
    false
),
(
    'Seguimiento a solicitud de beca',
    'Se informa que la solicitud de beca se encuentra en etapa de revisión documental.',
    '2026-02-03 12:00:00-08',
    11,
    18,
    false
),
(
    'Actualización de calendario académico',
    'Se comparte el calendario académico actualizado para el periodo agosto-diciembre.',
    '2026-02-06 10:50:00-08',
    12,
    8,
    false
),
(
    'Solicitud de difusión',
    'Solicitamos apoyo para difundir la convocatoria entre estudiantes y docentes.',
    '2026-02-10 09:10:00-08',
    13,
    20,
    false
),
(
    'Confirmación de participación',
    'Confirmamos la participación de nuestra institución en el encuentro internacional.',
    '2026-02-12 17:05:00-08',
    14,
    11,
    false
),
(
    'Revisión de expediente',
    'El expediente fue recibido y será revisado por el comité durante esta semana.',
    '2026-02-15 11:30:00-08',
    15,
    22,
    false
),
(
    'Solicitud de reporte de actividades',
    'Favor de enviar el reporte de actividades realizadas durante el primer trimestre.',
    '2026-02-18 08:55:00-08',
    16,
    13,
    false
),
(
    'Aviso de mantenimiento del sistema',
    'El sistema estará en mantenimiento el sábado de 08:00 a 12:00 horas.',
    '2026-02-20 14:40:00-08',
    17,
    21,
    false
),
(
    'Resultado de evaluación de proyecto',
    'El proyecto fue evaluado favorablemente y se autoriza la siguiente etapa.',
    '2026-02-23 16:15:00-08',
    18,
    16,
    false
),
(
    'Coordinación de visita institucional',
    'Se solicita confirmar la agenda propuesta para la visita institucional de marzo.',
    '2026-02-25 10:20:00-08',
    19,
    24,
    false
),
(
    'Cierre de convocatoria',
    'La convocatoria cerró correctamente y se iniciará la evaluación de postulaciones.',
    '2026-02-28 18:00:00-08',
    20,
    17,
    false
);

INSERT INTO administrative_message_files (
    name,
    media_type,
    content,
    administrative_message_id
)
    VALUES
    (
        'agenda_reunion_semestral.pdf',
        'application/pdf',
        '\x255044462d312e34'::bytea,
        1
    ),
    (
        'lista_asistentes.xlsx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ''::bytea,
        1
    ),
    (
        'formato_actualizacion_datos.docx',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ''::bytea,
        2
    ),
    (
        'presupuesto_movilidad_2026.pdf',
        'application/pdf',
        '\x255044462d312e37'::bytea,
        3
    ),
    (
        'plantilla_informe_mensual.xlsx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ''::bytea,
        4
    ),
    (
        'invitacion_capacitacion.pdf',
        'application/pdf',
        '\x255044462d312e35'::bytea,
        5
    ),
    (
        'programa_capacitacion.png',
        'image/png',
        '\x89504e470d0a1a0a'::bytea,
        5
    ),
    (
        'convocatoria_validada.pdf',
        'application/pdf',
        ''::bytea,
        6
    ),
    (
        'calendario_sesion.ics',
        'text/calendar',
        ''::bytea,
        7
    ),
    (
        'estado_convenio.docx',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ''::bytea,
        8
    ),
    (
        'propuesta_movilidad.pdf',
        'application/pdf',
        '\x255044462d312e36'::bytea,
        9
    ),
    (
        'lista_documentos_pendientes.pdf',
        'application/pdf',
        ''::bytea,
        10
    ),
    (
        'calendario_academico_2026.pdf',
        'application/pdf',
        '\x255044462d312e34'::bytea,
        11
    ),
    (
        'material_difusion.zip',
        'application/zip',
        ''::bytea,
        12
    ),
    (
        'agenda_visita_institucional.pdf',
        'application/pdf',
        ''::bytea,
        13
    );

COMMIT;

-- For AI
/*
create table administrative_messages (
    administrative_message_id bigserial primary key,

    -- Random hex number string of length 32
    key char(32) not null collate case_accent_insensitive
        unique,

    subject varchar(150) not null collate case_accent_insensitive,
    body text not null collate case_accent_insensitive
        check (length(body) > 0),
    creation timestamp with time zone not null,

    -- Valid IDs between 1 and 25
    sender_id bigint not null
        references administratives(user_id),
    recipient_id bigint not null
        references administratives(user_id),

    deleted boolean not null
);

create table administrative_message_files (
    administrative_message_file_id bigserial primary key,

    -- Random hex number string of length 32
    key char(32) not null collate case_accent_insensitive
        unique,

    -- File name + extension
    name text not null collate case_accent_insensitive,

    media_type text not null collate case_accent_insensitive,

    -- Random bytea literal or ''::bytea
    content bytea not null
        check (length(content) <= 31457280),

    administrative_message_id bigint not null
        references administrative_messages(administrative_message_id)
);*/
