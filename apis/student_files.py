from fastapi import Request, Response, Query
from fastapi.responses import StreamingResponse
from app import app
from datetime import datetime, timezone
from db import dbconn
from pydantic import BaseModel
from utils import constants, sql
from utils.res_bodies import ok, log_err, not_found, forbidden, err
from utils.sessions import verify_requester
from utils.validation import validate_file
from typing import Annotated
from models import StudentFile

@app.get('/api/student-files/read/{application_id},{file_req_id}')
def read(
    req: Request,
    res: Response,
    application_id: int,
    file_req_id: int
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
                    select cf.id from student_files sf
                    join applications ap on sf.application_id = ap.id
                    join users s on ap.student_id = s.id
                    join file_requests fr on sf.file_request_id = fr.id
                    join calls_for cf on fr.call_for_id = cf.id
                    join users a on cf.administrative_id = a.id
                    where
                        not sf.deleted and
                        not ap.deleted and
                        not s.deleted and
                        not fr.deleted and
                        not cf.deleted and
                        not a.deleted and
                        sf.application_id = %s and
                        sf.file_request_id = %s
                )
                """,
                [application_id, file_req_id]
            )

            if not c.fetchone()[0]:
                res.status_code = 404
                return not_found()

            if verif['idRolePair']['role'] == constants.STUDENT:
                is_member_q = """
                select exists (
                    select 1 from applications
                    where id = %s and student_id = %s
                )
                """
            elif verif['idRolePair']['role'] == constants.ADMINISTRATIVE:
                is_member_q = """
                select exists (
                    select 1 from applications ap
                    join calls_for cf on ap.call_for_id = cf.id
                    where ap.id = %s and cf.administrative_id = %s
                )
                """
            param_vals = [application_id, verif['idRolePair']['id']]

            c.execute(is_member_q, param_vals)

            if not c.fetchone()[0]:
                res.status_code = 403
                return forbidden()

            c.execute(
                'select name, media_type, content from student_files where application_id = %s and file_request_id = %s',
                [application_id, file_req_id]
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

@app.get('/api/student-files/read')
def read_by(
    req: Request,
    res: Response,
    student_id: Annotated[int, Query(alias='student-id')],
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
                select ap.id from applications ap
                join users s on ap.student_id = s.id
                join calls_for cf on ap.call_for_id = cf.id
                join users a on cf.administrative_id = a.id
                where
                    not ap.deleted and
                    not s.deleted and
                    not cf.deleted and
                    not a.deleted and
                    ap.student_id = %s and
                    ap.call_for_id = %s
                """,
                [student_id, call_for_id]
            )
            application = c.fetchone()

            if not application:
                res.status_code = 404
                return not_found()

            if verif['idRolePair']['role'] == constants.STUDENT:
                is_member_q = """
                select exists (
                    select 1 from applications
                    where id = %s and student_id = %s
                )
                """
            elif verif['idRolePair']['role'] == constants.ADMINISTRATIVE:
                is_member_q = """
                select exists (
                    select 1 from applications ap
                    join calls_for cf on ap.call_for_id = cf.id
                    where ap.id = %s and cf.administrative_id = %s
                )
                """
            param_vals = [application[0], verif['idRolePair']['id']]

            c.execute(is_member_q, param_vals)

            if not c.fetchone()[0]:
                res.status_code = 403
                return forbidden()

            json_keys = ['fileRequestId', 'title', 'requirements', 'referenceFileId', 'uploadedFile']
            query = """
            select
                fr.id,
                fr.title,
                fr.requirements,
                case
                    when ff.deleted is null or ff.deleted then
                        null else
                        ff.id
                end,
                case
                    when sf.application_id is null then
                        null else
                        jsonb_build_object(
                            'applicationId', sf.application_id,
                            'fileRequestId', sf.file_request_id,
                            'name', sf.name,
                            'size', sf.size,
                            'modification', sf.modification
                        )
                end
            from file_requests fr
            left join (
                select application_id, file_request_id, name, length(content) as size, modification
                from student_files
                where not deleted and application_id = %s
            ) sf on fr.id = sf.file_request_id
            left join forum_files ff on fr.ref_file_id = ff.id
            """
            where = 'where not fr.deleted and fr.call_for_id = %s'
            param_vals = [application[0], call_for_id]

            if cursor_pos_maybe is None:
                cursor_pos = sql.get_init_cursor_pos(
                    conn,
                    f'select fr.id from file_requests fr { where }',
                    'fr.id',
                    [call_for_id]
                )
            else:
                cursor_pos = cursor_pos_maybe

            file_rows = sql.fetch_paginated(
                conn,
                f'{ query } { where }',
                'fr.id',
                param_vals,
                cursor_pos
            )
            files = [dict(zip(json_keys, row)) for row in file_rows]

            if len(files) == constants.PAGE_SIZE:
                new_cursor_pos = files[-1]['fileRequestId']
            else:
                new_cursor_pos = constants.FINAL_CURSOR_POS
        
            res.status_code = 200
            return ok({
                'cursorPosition': new_cursor_pos,
                'fileEntries': files
            }) | { 'idRolePair': verif['idRolePair'] }
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()

class CreateData(BaseModel):
    fileRequestId: int
    name: str
    fileUri: str

@app.post('/api/student-files/create')
def create(
    req: Request,
    res: Response,
    data: CreateData
):
    verif = verify_requester(req, constants.STUDENT)
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

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select cf.id from file_requests fr join calls_for cf on fr.call_for_id = cf.id join users a on cf.administrative_id = a.id where not fr.deleted and not cf.deleted and not a.deleted and fr.id = %s',
                [data.fileRequestId]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La solicitud de archivo (espacio para subir archivo) no existe')

            c.execute(
                'select id from applications where student_id = %s and call_for_id = %s and not deleted',
                [verif['idRolePair']['id'], call_for[0]]
            )
            application = c.fetchone()

            if not application:
                res.status_code = 400
                return err('No es miembro')

            c.execute(
                'select exists (select 1 from student_files where application_id = %s and file_request_id = %s)',
                [application[0], data.fileRequestId]
            )

            file = StudentFile(
                application[0],
                data.fileRequestId,
                data.name,
                uri_validation[1]['media_type'],
                uri_validation[1]['content'],
                datetime.now(timezone.utc),
                False
            )

            if c.fetchone()[0]:
                c.execute(
                    'update student_files set name = %s, media_type = %s, content = %s, modification = %s, deleted = %s where application_id = %s and file_request_id = %s',
                    [file.name, file.media_type, file.content, file.modification, file.deleted, file.application_id, file.file_request_id]
                )
            else:
                c.execute(
                    'insert into student_files values (%s, %s, %s, %s, %s, %s, %s)',
                    [file.application_id, file.file_request_id, file.name, file.media_type, file.content, file.modification, file.deleted]
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
