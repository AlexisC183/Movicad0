from fastapi import Request, Response, Query
from app import app
from db import dbconn
from pydantic import BaseModel
from typing import Annotated
from utils import constants
from utils import sql
from utils.converters import memoryview_to_b64
from utils.res_bodies import err, log_err, ok, not_found, forbidden
from utils.sessions import verify_requester
from utils.validation import validate_file

@app.get('/api/students/me')
def read(req: Request, res: Response):
    verif = verify_requester(req, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    json_keys = ['name', 'icon', 'iconMediaType']
    query = 'select name, icon, icon_media_type from students where id = %s'
    conn = None

    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(query, [verif['idRolePair']['id']])
            student = dict(zip(json_keys, c.fetchone()))

            student['icon'] = memoryview_to_b64(student['icon'])

            res.status_code = 200
            return ok(student) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

@app.get('/api/students/read')
def read_by(
    req: Request,
    res: Response,
    call_for_id: Annotated[int, Query(alias='call-for-id')],
    cursor_pos_maybe: Annotated[int | None, Query(alias='cursor-pos')] = None
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
                'select cf.administrative_id from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s',
                [call_for_id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 404
                return not_found()

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 403
                return forbidden()

            json_keys = ['id', 'name', 'icon', 'iconMediaType']
            query = 'select u.id, s.name, s.icon, s.icon_media_type from applications ap join students s on ap.student_id = s.id join users u on s.id = u.id'
            where = 'where not ap.deleted and not u.deleted and ap.call_for_id = %s'
            param_vals = [call_for_id]

            if cursor_pos_maybe is None:
                cursor_pos = sql.get_init_cursor_pos(
                    conn,
                    f'select u.id from applications ap join users u on ap.student_id = u.id { where }',
                    'u.id',
                    param_vals
                )
            else:
                cursor_pos = cursor_pos_maybe

            student_rows = sql.fetch_paginated(
                conn,
                f'{ query } { where }',
                'u.id',
                param_vals,
                cursor_pos
            )
            students = [dict(zip(json_keys, row)) for row in student_rows]

            for student in students:
                student['icon'] = memoryview_to_b64(student['icon'])

            if len(students) == constants.PAGE_SIZE:
                new_cursor_pos = students[-1]['id']
            else:
                new_cursor_pos = constants.FINAL_CURSOR_POS
        
            res.status_code = 200
            return ok({
                'cursorPosition': new_cursor_pos,
                'students': students
            }) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

class UpdateProfileData(BaseModel):
    name: str
    iconUri: str

@app.patch('/api/students/update-profile')
def update_profile(
    req: Request,
    res: Response,
    data: UpdateProfileData
):
    verif = verify_requester(req, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    uri_validation = None

    if len(data.iconUri) > 0:
        uri_validation = validate_file(
            data.iconUri,
            10 * constants.MEGABYTE,
            'image/(gif|jpeg|png|webp|svg\\+xml)'
        )
    
    if uri_validation and uri_validation[0] == False:
        res.status_code = 400
        return err(uri_validation[1])

    if uri_validation:
        parsed_img_uri = uri_validation[1]
    else:
        parsed_img_uri = {
            'media_type': 'image/gif',
            'content': memoryview(b'')
        }
    
    trimmed_name = data.name.strip()

    if len(trimmed_name) > 100:
        res.status_code = 400
        return err('Su nombre es muy largo')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:            
            c.execute(
                'update students set name = %s, icon = %s, icon_media_type = %s where id = %s',
                [
                    trimmed_name,
                    parsed_img_uri['content'],
                    parsed_img_uri['media_type'],
                    verif['idRolePair']['id']
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
            