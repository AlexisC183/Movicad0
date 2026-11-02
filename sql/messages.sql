begin;
insert into private_messages values
(default, 'Aquí tienes el QR para solicitar', '2026-10-10T15:43:22.019', ''::bytea, 'image/png', 1, 1, false),
(default, 'muchas gracias', '2026-10-10T16:00:01.099', ''::bytea, 'image/gif', 26, 1, false),
(default, 'disculpe, existe un limite de cupo?', '2026-10-11T07:22:01.610', ''::bytea, 'image/gif', 28, 4, false),
(default, 'Hola', '2026-10-04T22:30:00.001', ''::bytea, 'image/gif', 31, 7, false);
commit;

begin;
insert into forum_messages values
(default, 'Soy nuevo!!', '2026-10-13T06:00:30.812', ''::bytea, 'image/gif', 27, 1, false);
commit;
