begin;
insert into file_requests (
    title,
    call_for_id,
    deleted
) values
('Formato de solicitud', 1, false),
('Contrato', 1, true),
('Comprobante de estudios', 1, false),
('Comprobante de visa', 1, false),
('e-firma', 1, false),
('Foto blanco y negro, formal', 1, false),
('Avance 1', 1, false);
commit;
