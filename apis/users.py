from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app import app
from db import dbconn
from datetime import datetime, timezone, timedelta
from fastapi import Response
from pydantic import BaseModel
from functools import partial
from models import User, Student, Administrative
from utils import constants
from utils.validation import assertion_fail
from utils.res_bodies import err, log_err, ok
import re


class CreateReq(BaseModel):
    id: str
    password: str
    password1: str
    role: str

@app.post('/api/users/create')
def create(req: CreateReq, res: Response):
    if req.password != req.password1:
        res.status_code = 400
        return err('Las contraseñas no coinciden')

    if body := assertion_fail(req, {
        'id': (
            lambda id: 1 <= len(id) <= 50 and bool(re.match('\\w+', id, re.ASCII)),
            partial(err, 'El identificador debe tener longitud [1, 50] y solo permite los caracteres [a-zA-Z0-9_]')
        ),
        'password': (
            lambda pwd: (
                8 <= len(pwd) <= 50 and
                any([not ch.isalnum() for ch in pwd]) and
                not all([ch == pwd[0] for ch in pwd])
            ),
            partial(err, 'La contraseña debe tener longitud [8, 50], un carácter especial y caracteres diferentes')
        ),
        'role': (
            lambda r: r in (constants.STUDENT, constants.ADMINISTRATIVE),
            partial(err, 'Rol no válido')
        )
    }):
        res.status_code = 400
        return body

    user = User(
        0,
        req.id.lower(),
        req.role,
        PasswordHasher().hash(req.password),
        datetime.now(timezone(timedelta())),
        False
    )
    conn = None

    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute('select exists (select 1 from users where key = %s)', [user.key])

            if c.fetchone()[0]:
                res.status_code = 409
                return err('Intentar un identificador único diferente')
            
            c.execute(
                'insert into users values (default, %s, %s, %s, %s, %s) returning users.id',
                [user.key, user.role, user.password, user.creation, user.deleted]
            )
            [auto_id] = c.fetchone()

            if req.role == constants.STUDENT:
                student = Student(
                    auto_id,
                    '',
                    memoryview(b''),
                    'image/gif'
                )
                c.execute(
                    'insert into students values (%s, %s, %s, %s)',
                    [student.auto_id, student.name, student.icon, student.icon_media_type]
                )

            if req.role == constants.ADMINISTRATIVE:
                admin = Administrative(
                    auto_id,
                    '',
                    '',
                    'publica',
                    'otro',
                    '',
                    memoryview(b''),
                    'image/gif'
                )
                c.execute(
                    'insert into administratives values (%s, %s, %s, %s, %s, %s, %s, %s)',
                    [admin.id, admin.name, admin.acronym, admin.type, admin.country, admin.website, admin.icon, admin.icon_media_type]
                )

            conn.commit()

            # Authentication goes here...
            # Storing user's ID and role somewhere, if possible...

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()