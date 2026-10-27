from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app import app
from db import dbconn
from datetime import datetime, timezone
from fastapi import Request, Response
from pydantic import BaseModel
from functools import partial
from models import User, Student, Administrative
from utils import constants
from utils.sessions import create_session, set_auth_cookie, verify_requester
from utils.validation import class_fail
from utils.res_bodies import err, log_err, ok, no_account
import re

class CreateData(BaseModel):
    id: str
    password: str
    password1: str
    role: str

@app.post('/api/users/create')
def create(res: Response, data: CreateData):
    if data.password != data.password1:
        res.status_code = 400
        return err('Las contraseñas no coinciden')

    if body := class_fail(data, {
        'id': (
            lambda id: 1 <= len(id) <= 50 and bool(re.fullmatch('\\w+', id, re.ASCII)),
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
        data.id.lower(),
        data.role,
        PasswordHasher().hash(data.password),
        datetime.now(timezone.utc),
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
            user.id = c.fetchone()[0]

            if data.role == constants.STUDENT:
                student = Student(
                    user.id,
                    '',
                    memoryview(b''),
                    'image/gif'
                )
                c.execute(
                    'insert into students values (%s, %s, %s, %s)',
                    [student.id, student.name, student.icon, student.icon_media_type]
                )

            if data.role == constants.ADMINISTRATIVE:
                admin = Administrative(
                    user.id,
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
            token = create_session(conn, user.id)

            conn.commit()

            set_auth_cookie(res, token)

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

class UpdatePasswordData(BaseModel):
    oldPassword: str
    newPassword: str
    newPassword1: str
            
@app.patch('/api/users/update-password')
def update_password(req: Request, res: Response, data: UpdatePasswordData):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    if data.newPassword != data.newPassword1:
        res.status_code = 400
        return err('Las contraseñas no coinciden')

    if body := class_fail(data, {
        'newPassword': (
            lambda pwd: (
                8 <= len(pwd) <= 50 and
                any([not ch.isalnum() for ch in pwd]) and
                not all([ch == pwd[0] for ch in pwd])
            ),
            partial(err, 'La contraseña debe tener longitud [8, 50], un carácter especial y caracteres diferentes')
        )
    }):
        res.status_code = 400
        return body

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select password from users where not deleted and id = %s',
                [verif['idRolePair']['id']]
            )
            user = c.fetchone()
            if not user:
                res.status_code = 401
                return no_account()

            pwd_hasher = PasswordHasher()

            try:
                pwd_hasher.verify(user[0], data.oldPassword)
            except VerifyMismatchError:
                res.status_code = 401
                return err('Contraseña actual incorrecta')

            c.execute(
                'update users set password = %s where id = %s',
                [pwd_hasher.hash(data.newPassword), verif['idRolePair']['id']]
            )
            conn.commit()

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
