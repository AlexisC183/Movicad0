begin;
insert into applications (
	student_id,
	call_for_id,
	deleted
) values
(26, 1, false),
(26, 2, false), 
(27, 1, false),
(28, 6, false),
(29, 1, false),
(30, 1, true),
(31, 1, false);
commit;
