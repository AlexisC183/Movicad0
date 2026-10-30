from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request, Response
from app import app
from datetime import date, datetime, time, timezone
from db import dbconn
from functools import partial
from pydantic import BaseModel
from utils import constants
from utils import sql
from utils.res_bodies import err, log_err, ok
from utils.sessions import verify_requester
from utils.validation import vars_fail
from models import CallFor

class CreateData(BaseModel):
    title: str
    description: str
    requirements: str
    destinationCountry: str
    initialDate: date | None
    finalDate: date | None

@app.post('/api/calls-for/create')
def create(
    req: Request,
    res: Response,
    data: CreateData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    trimmed_title = data.title.strip()
    trimmed_description = data.description.strip()
    trimmed_requirements = data.requirements.strip()

    if body := vars_fail(
        (
            trimmed_title,
            lambda t: 1 <= len(t) <= 200,
            partial(err, 'El título debe contener entre 1 y 200 caracteres')
        ),
        (
            data.destinationCountry,
            lambda dest_c: dest_c in ('otro', 'mexico', 'china'),
            partial(err, 'País no válido')
        )
    ):
        res.status_code = 400
        return body

    initial_date_utc = (
        None if data.initialDate is None else
        datetime.combine(
            data.initialDate,
            time.min,
            tzinfo=timezone.utc
        )
    )
    final_date_utc = (
        None if data.finalDate is None else
        datetime.combine(
            data.finalDate,
            time.min,
            tzinfo=timezone.utc
        )
    )

    if (
        initial_date_utc and
        final_date_utc and
        initial_date_utc > final_date_utc
    ):
        res.status_code = 400
        return err('La fecha de apertura no puede ser mayor que la fecha de cierre')

    now = datetime.now(timezone.utc)
    call_for = CallFor(
        0,
        trimmed_title,
        initial_date_utc,
        final_date_utc,
        trimmed_description,
        trimmed_requirements,
        data.destinationCountry,
        now,
        now,
        verif['idRolePair']['id'],
        False
    )
    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'insert into calls_for values (default, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                [call_for.title, call_for.initial_date, call_for.final_date, call_for.description, call_for.requirements, call_for.destination_country, call_for.publish_date, call_for.modification, call_for.administrative_id, call_for.deleted]
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
    

class UpdateData(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    destinationCountry: str
    initialDate: date | None
    finalDate: date | None

@app.patch('/api/calls-for/update')
def update(
    req: Request,
    res: Response,
    data: UpdateData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    trimmed_title = data.title.strip()
    trimmed_description = data.description.strip()
    trimmed_requirements = data.requirements.strip()

    if body := vars_fail(
        (
            trimmed_title,
            lambda t: 1 <= len(t) <= 200,
            partial(err, 'El título debe contener entre 1 y 200 caracteres')
        ),
        (
            data.destinationCountry,
            lambda dest_c: dest_c in ('otro', 'mexico', 'china'),
            partial(err, 'País no válido')
        )
    ):
        res.status_code = 400
        return body

    initial_date_utc = (
        None if data.initialDate is None else
        datetime.combine(
            data.initialDate,
            time.min,
            tzinfo=timezone.utc
        )
    )
    final_date_utc = (
        None if data.finalDate is None else
        datetime.combine(
            data.finalDate,
            time.min,
            tzinfo=timezone.utc
        )
    )

    if (
        initial_date_utc and
        final_date_utc and
        initial_date_utc > final_date_utc
    ):
        res.status_code = 400
        return err('La fecha de apertura no puede ser mayor que la fecha de cierre')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select cf.administrative_id from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s',
                [data.id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La convocatoria no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')
            
            c.execute(
                'update calls_for set title = %s, initial_date = %s, final_date = %s, description = %s, requirements = %s, destination_country = %s, modification = %s where id = %s',
                [
                    trimmed_title,
                    initial_date_utc,
                    final_date_utc,
                    trimmed_description,
                    trimmed_requirements,
                    data.destinationCountry,
                    datetime.now(timezone.utc),
                    data.id
                ]
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

class DeleteData(BaseModel):
    callForId: int
    password: str

@app.delete('/api/calls-for/delete')
def delete(
    req: Request,
    res: Response,
    data: DeleteData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select cf.administrative_id, u.password from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s',
                [data.callForId]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La convocatoria no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            try:
                PasswordHasher().verify(call_for[1], data.password)
            except VerifyMismatchError:
                res.status_code = 401
                return err('Contraseña incorrecta')

            sql.set_deleted(conn, 'calls_for', data.callForId)

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
