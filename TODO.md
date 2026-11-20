# TODO


# TEST
AI endpoint against "Foto" file request



# Walking the relational hierarchy bottom to top
```sql
select cf.administrative_id
from calls_for cf
join users u on cf.administrative_id = u.id
where not cf.deleted and not u.deleted and cf.id = ?;
```

# Other
2 h + 11 min, at 11-19T20:58 (power outage)
