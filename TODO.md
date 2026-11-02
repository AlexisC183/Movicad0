# TODO


# TEST
/api/administratives/read

/api/applications/create
/api/applications/delete

/api/calls-for/read <- OK
/api/calls-for/read/{id}
/api/calls-for/read-by-student
/api/calls-for/create
/api/calls-for/update
/api/calls-for/delete

# Walking the relational hierarchy bottom to top
```sql
select cf.administrative_id
from calls_for cf
join users u on cf.administrative_id = u.id
where not cf.deleted and not u.deleted and cf.id = ?;
```