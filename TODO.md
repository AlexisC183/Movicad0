# TODO
calls_for.read


# TEST
/api/calls-for/read <- OK
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