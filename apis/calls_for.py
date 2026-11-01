from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request, Response, Query
from app import app
from datetime import date, datetime, time, timezone
from db import dbconn
from functools import partial
from pydantic import BaseModel
from utils import constants
from utils import sql
from utils.converters import try_int
from utils.res_bodies import err, log_err, ok, not_found
from utils.sessions import verify_requester
from utils.validation import vars_fail
from models import CallFor
from typing import Annotated
import base64

@app.get('/api/calls-for/read')
def read_all(
    req: Request,
    res: Response,
    cursor_pos_maybe: Annotated[int | None, Query(alias='cursor-pos')] = None,
    search_term: Annotated[str, Query(alias='search-term')] = '',
    country: str = '',
    admin_id: Annotated[int | None, Query(alias='admin-id')] = None,
    open_only: Annotated[bool, Query(alias='open-only')] = False
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    trimmed_search_term = search_term.strip()

    json_keys = ['icon', 'iconMediaType', 'id', 'title', 'publishDate', 'country']
    query = 'select a.icon, a.icon_media_type, cf.id, cf.title, cf.publish_date, cf.destination_country from calls_for cf join administratives a on cf.administrative_id = a.id join users u on a.id = u.id'
    where = 'where not cf.deleted and not u.deleted'

    if open_only:
        where += " and now() between coalesce(cf.initial_date, '-infinity') and coalesce(cf.final_date, 'infinity')"

    param_vals = []
    if trimmed_search_term:
        where += ' and (cf.title like %s or cf.id = %s)'
        param_vals = [
            f'%{ trimmed_search_term }%',
            try_int(trimmed_search_term)
        ]
    elif country:
        where += ' and cf.destination_country = %s'
        param_vals = [country]
    elif admin_id is not None:
        where += ' and cf.administrative_id = %s'
        param_vals = [admin_id]

    conn = None
    try:
        conn = dbconn()
        if cursor_pos_maybe is None:
            cursor_pos = sql.get_init_cursor_pos(
                conn,
                f'select cf.id from calls_for cf join users u on cf.administrative_id = u.id { where }',
                'cf.id',
                param_vals
            )
        else:
            cursor_pos = cursor_pos_maybe

        calls_for_rows = sql.fetch_paginated(
            conn,
            f'{ query } { where }',
            'cf.id',
            param_vals,
            cursor_pos
        )
        calls_for = [dict(zip(json_keys, row)) for row in calls_for_rows]

        for cf in calls_for:
            cf['icon'] = base64.b64encode(cf['icon'].tobytes())

        if len(calls_for) == constants.PAGE_SIZE:
            new_cursor_pos = calls_for[-1]['id']
        else:
            new_cursor_pos = constants.FINAL_CURSOR_POS
      
        res.status_code = 200
        return ok({
            'cursorPosition': new_cursor_pos,
            'callsFor': calls_for
        }) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
    

@app.get('/api/calls-for/read/{id}')
def read(
    req: Request,
    res: Response,
    id: int
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    json_keys = [
        'title',
        'description',
        'requirements',
        'initialDate',
        'finalDate',
        'modification',
        'country',
        'adminId',
        'acronym',
    ]
    query = 'select cf.title, cf.description, cf.requirements, cf.initial_date, cf.final_date, cf.modification, cf.destination_country, a.id, a.acronym from calls_for cf join administratives a on cf.administrative_id = a.id where not cf.deleted and not u.deleted and cf.id = %s'
    conn = None

    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(query, [id])
            call_for_row = c.fetchone()

            if not call_for_row:
                res.status_code = 404
                return not_found()

            call_for = dict(zip(json_keys, call_for_row))

            res.status_code = 200
            return ok(call_for) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

@app.get('/api/calls-for/read-by-student')
def read_by_student(
    req: Request,
    res: Response,
    cursor_pos_maybe: Annotated[int | None, Query(alias='cursor-pos')] = None
):
    verif = verify_requester(req, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    json_keys = ['icon', 'iconMediaType', 'id', 'title', 'publishDate', 'country']
    query = 'select a.icon, a.icon_media_type, cf.id, cf.title, cf.publish_date, cf.destination_country from applications ap join calls_for cf on ap.call_for_id = cf.id join administratives a on cf.administrative_id = a.id join users u on a.id = u.id where not ap.deleted and not cf.deleted and not u.deleted'

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
