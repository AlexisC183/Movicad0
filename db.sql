create collation case_accent_insensitive (
    provider = icu,
    locale = 'und-u-ks-level1',
    deterministic = false
);

create table users (
    id bigserial primary key,
    key varchar(50) not null collate case_accent_insensitive
        unique
        check (length(key) > 0),
    role text not null collate case_accent_insensitive
        check (role in ('estudiante', 'administrativo')),
    password char(97) not null,
    creation timestamp with time zone not null,
    deleted boolean not null
);

create table students (
    id bigint not null
        references users(id),
    name varchar(100) not null collate case_accent_insensitive,
    icon bytea not null
        check (length(icon) <= 10485760),
    icon_media_type text not null collate case_accent_insensitive
        check (icon_media_type in ('image/gif', 'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml')),
    primary key (id)
);

create table administratives (
    id bigint not null
        references users(id),
    name varchar(200) not null collate case_accent_insensitive,
    acronym varchar(100) not null collate case_accent_insensitive,
    type text not null collate case_accent_insensitive
        check (type in ('publica', 'privada', 'comunitaria')),
    country text not null collate case_accent_insensitive
        check (country in ('otro', 'mexico', 'china')),
    website text not null collate case_accent_insensitive,
    icon bytea not null
        check (length(icon) <= 10485760),
    icon_media_type text not null collate case_accent_insensitive
        check (icon_media_type in ('image/gif', 'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml')),
    primary key (id)
);

create table administrative_messages (
    id bigserial primary key,
    subject varchar(150) not null collate case_accent_insensitive,
    body text not null collate case_accent_insensitive
        check (length(body) > 0),
    creation timestamp with time zone not null,
    sender_id bigint not null
        references administratives(id),
    recipient_id bigint not null
        references administratives(id),
    deleted boolean not null
);

create table administrative_message_files (
    id bigserial primary key,
    name text not null collate case_accent_insensitive,
    media_type text not null collate case_accent_insensitive,
    content bytea not null
        check (length(content) <= 31457280),
    administrative_message_id bigint not null
        references administrative_messages(id)
);

create table calls_for (
    id bigserial primary key,
    title varchar(200) not null collate case_accent_insensitive
        check (length(title) > 0),
    initial_date timestamp with time zone,
    final_date timestamp with time zone,
    description text not null collate case_accent_insensitive,
    requirements text not null collate case_accent_insensitive,
    destination_country text not null collate case_accent_insensitive
        check (destination_country in ('otro', 'mexico', 'china')),
    publish_date timestamp with time zone not null,
    modification timestamp with time zone not null,
    administrative_id bigint not null
        references administratives(id),
    deleted boolean not null
);

create table frequent_questions (
    id bigserial primary key,
    question varchar(150) not null collate case_accent_insensitive
        check (length(question) > 0),
    answer text not null collate case_accent_insensitive
        check (length(question) > 0),
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null
);

create table links (
    id bigserial primary key,
    title varchar(150) not null collate case_accent_insensitive
        check (length(title) > 0),
    url text not null collate case_accent_insensitive
        check (length(title) > 0),
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null
);

create table forum_files (
    id bigserial primary key,
    title varchar(150) not null collate case_accent_insensitive
        check (length(title) > 0),
    name text not null collate case_accent_insensitive,
    media_type text not null collate case_accent_insensitive,
    content bytea not null
        check (length(content) <= 31457280),
    modification timestamp with time zone not null,
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null
);

create table forum_messages (
    id bigserial primary key,
    content varchar(1000) not null collate case_accent_insensitive
        check (length(content) > 0),
    creation timestamp with time zone not null,
    attached_image bytea not null
        check (length(attached_image) <= 10485760),
    image_media_type text not null collate case_accent_insensitive
        check (image_media_type in ('image/gif', 'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml')),
    user_id bigint not null
        references users(id),
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null
);

create table file_requests (
    id bigserial primary key,
    title varchar(150) not null collate case_accent_insensitive
        check (length(title) > 0),
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null
);

create table applications (
    id bigserial primary key,
    student_id bigint not null
        references students(id),
    call_for_id bigint not null
        references calls_for(id),
    deleted boolean not null,
    unique (student_id, call_for_id)
);

create table student_files (
    application_id bigint not null
        references applications(id),
    file_request_id bigint not null
        references file_requests(id),
    name text not null collate case_accent_insensitive,
    media_type text not null collate case_accent_insensitive,
    content bytea not null
        check (length(content) <= 31457280),
    modification timestamp with time zone not null,
    deleted boolean not null,
    primary key (application_id, file_request_id)
);

create table private_messages (
    id bigserial primary key,
    content varchar(1000) not null collate case_accent_insensitive
        check (length(content) > 0),
    creation timestamp with time zone not null,
    attached_image bytea not null
        check (length(attached_image) <= 10485760),
    image_media_type text not null collate case_accent_insensitive
        check (image_media_type in ('image/gif', 'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml')),
    user_id bigint not null
        references users(id),
    application_id bigint not null
        references applications(id),
    deleted boolean not null
);
