from fastapi import Request, Response, Query
from fastapi.responses import StreamingResponse
from app import app
from datetime import datetime, timezone
from db import dbconn
from pydantic import BaseModel
from typing import Annotated
from utils import constants
from utils import sql
from utils.res_bodies import log_err, not_found, forbidden, ok, err
from utils.sessions import verify_requester
from utils.validation import validate_file
from models import ForumFile

@app.get('/api/forum-files/read/{id}')
def read(
    req: Request,
    res: Response,
    id: int
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select cf.id from forum_files ff join calls_for cf on ff.call_for_id = cf.id join users a on cf.administrative_id = a.id where not ff.deleted and not cf.deleted and not a.deleted and ff.id = %s',
                [id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 404
                return not_found()

            if verif['idRolePair']['role'] == constants.STUDENT:
                is_member_q = """
                select exists (
                    select 1 from calls_for cf
                    join applications ap on cf.id = ap.call_for_id
                    where not ap.deleted and cf.id = %s and ap.student_id = %s
                )
                """
            elif verif['idRolePair']['role'] == constants.ADMINISTRATIVE:
                is_member_q = """
                select exists (
                    select 1 from calls_for
                    where id = %s and administrative_id = %s
                )
                """
            param_vals = [call_for[0], verif['idRolePair']['id']]

            c.execute(is_member_q, param_vals)

            if not c.fetchone()[0]:
                res.status_code = 403
                return forbidden()

            c.execute(
                'select name, media_type, content from forum_files where id = %s',
                [id]
            )
            [name, media_type, content] = c.fetchone()

            res.status_code = 200
            return StreamingResponse(
                content=(content.tobytes() for _ in range(1)),
                media_type=media_type,
                headers={
                    'Content-Disposition': f'attachment; filename={ name }'
                }
            )
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

@app.get('/api/forum-files/read')
def read_by(
    req: Request,
    res: Response,
    call_for_id: Annotated[int, Query(alias='call-for-id')],
    cursor_pos_maybe: Annotated[int | None, Query(alias='cursor-pos')] = None
):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                """
                select exists (
                    select 1 from calls_for cf
                    join users a on cf.administrative_id = a.id
                    where not cf.deleted and not a.deleted and cf.id = %s
                )
                """,
                [call_for_id]
            )

            if not c.fetchone()[0]:
                res.status_code = 404
                return not_found()

            if verif['idRolePair']['role'] == constants.STUDENT:
                is_member_q = """
                select exists (
                    select 1 from calls_for cf
                    join applications ap on cf.id = ap.call_for_id
                    where not ap.deleted and cf.id = %s and ap.student_id = %s
                )
                """
            elif verif['idRolePair']['role'] == constants.ADMINISTRATIVE:
                is_member_q = """
                select exists (
                    select 1 from calls_for
                    where id = %s and administrative_id = %s
                )
                """
            param_vals = [call_for_id, verif['idRolePair']['id']]

            c.execute(is_member_q, param_vals)

            if not c.fetchone()[0]:
                res.status_code = 403
                return forbidden()

            json_keys = ['id', 'title', 'name', 'size', 'modification']
            query = 'select id, title, name, length(content), modification from forum_files'
            where = 'where not deleted and call_for_id = %s'
            param_vals = [call_for_id]

            if cursor_pos_maybe is None:
                cursor_pos = sql.get_init_cursor_pos(
                    conn,
                    f'select id from forum_files { where }',
                    'id',
                    param_vals
                )
            else:
                cursor_pos = cursor_pos_maybe

            file_rows = sql.fetch_paginated(
                conn,
                f'{ query } { where }',
                'id',
                param_vals,
                cursor_pos
            )
            files = [dict(zip(json_keys, row)) for row in file_rows]

            if len(files) == constants.PAGE_SIZE:
                new_cursor_pos = files[-1]['id']
            else:
                new_cursor_pos = constants.FINAL_CURSOR_POS
        
            res.status_code = 200
            return ok({
                'cursorPosition': new_cursor_pos,
                'files': files
            }) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

class CreateData(BaseModel):
    title: str
    name: str
    fileUri: str
    callForId: int

@app.post('/api/forum-files/create')
def create(
    req: Request,
    res: Response,
    data: CreateData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    uri_validation = validate_file(
        data.fileUri,
        30 * constants.MEGABYTE,
    )

    if uri_validation[0] == False:
        res.status_code = 400
        return err(uri_validation[1])

    trimmed_title = data.title.strip()

    if not 1 <= len(trimmed_title) <= 150:
        res.status_code = 400
        return err('El título debe contener entre 1 y 150 caracteres')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select cf.administrative_id from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s',
                [data.callForId]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La convocatoria no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            file = ForumFile(
                0,
                trimmed_title,
                data.name,
                uri_validation[1]['media_type'],
                uri_validation[1]['content'],
                datetime.now(timezone.utc),
                data.callForId,
                False
            )

            c.execute(
                'insert into forum_files values (default, %s, %s, %s, %s, %s, %s, %s)',
                [file.title, file.name, file.media_type, file.content, file.modification, file.call_for_id, file.deleted]
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
    name: str
    fileUri: str

@app.patch('/api/forum-files/update')
def update(
    req: Request,
    res: Response,
    data: UpdateData
):
    verif = verify_requester(req, constants.ADMINISTRATIVE)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    uri_validation = validate_file(
        data.fileUri,
        30 * constants.MEGABYTE,
    )

    if uri_validation[0] == False:
        res.status_code = 400
        return err(uri_validation[1])

    trimmed_title = data.title.strip()

    if not 1 <= len(trimmed_title) <= 150:
        res.status_code = 400
        return err('El título debe contener entre 1 y 150 caracteres')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                """
                select cf.administrative_id from forum_files ff
                join calls_for cf on ff.call_for_id = cf.id
                join users a on cf.administrative_id = a.id
                where not ff.deleted and not cf.deleted and not a.deleted and ff.id = %s
                """,
                [data.id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('El archivo a modificar no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            c.execute(
                'update forum_files set title = %s, name = %s, media_type = %s, content = %s, modification = %s where id = %s',
                [
                    trimmed_title,
                    data.name,
                    uri_validation[1]['media_type'],
                    uri_validation[1]['content'],
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
    id: int

@app.delete('/api/forum-files/delete')
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
                """
                select cf.administrative_id from forum_files ff
                join calls_for cf on ff.call_for_id = cf.id
                join users a on cf.administrative_id = a.id
                where not ff.deleted and not cf.deleted and not a.deleted and ff.id = %s
                """,
                [data.id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('El archivo no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            sql.set_deleted(conn, 'forum_files', data.id)

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
