# TODO

# TEST
/api/student-files/read
/api/student-files/read/{application_id},{file_req_id}
/api/student-files/create

/api/file-requests/create
/api/file-requests/update
/api/file-requests/delete

# Walking the relational hierarchy bottom to top
```sql
select cf.administrative_id
from calls_for cf
join users u on cf.administrative_id = u.id
where not cf.deleted and not u.deleted and cf.id = ?;
```