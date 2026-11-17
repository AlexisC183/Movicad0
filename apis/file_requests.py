from fastapi import Request, Response
from app import app
from db import dbconn
from pydantic import BaseModel
from utils import constants
from utils import sql
from utils.res_bodies import log_err, ok, err
from utils.sessions import verify_requester
from models import FileRequest

class CreateData(BaseModel):
    title: str
    callForId: int

@app.post('/api/file-requests/create')
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

            file_req = FileRequest(
                0,
                trimmed_title,
                data.callForId,
                False
            )

            c.execute(
                'insert into file_requests values (default, %s, %s, %s)',
                [file_req.title, file_req.call_for_id, file_req.deleted]
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

@app.patch('/api/file-requests/update')
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

    if not 1 <= len(trimmed_title) <= 150:
        res.status_code = 400
        return err('El título debe contener entre 1 y 150 caracteres')

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                """
                select cf.administrative_id from file_requests fr
                join calls_for cf on fr.call_for_id = cf.id
                join users a on cf.administrative_id = a.id
                where not fr.deleted and not cf.deleted and not a.deleted and fr.id = %s
                """,
                [data.id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La solicitud de archivo (espacio para subir archivo) no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            c.execute(
                'update file_requests set title = %s where id = %s',
                [trimmed_title, data.id]
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

@app.delete('/api/file-requests/delete')
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
                select cf.administrative_id from file_requests fr
                join calls_for cf on fr.call_for_id = cf.id
                join users a on cf.administrative_id = a.id
                where not fr.deleted and not cf.deleted and not a.deleted and fr.id = %s
                """,
                [data.id]
            )
            call_for = c.fetchone()

            if not call_for:
                res.status_code = 400
                return err('La solicitud de archivo (espacio para subir archivo) no existe')

            if verif['idRolePair']['id'] != call_for[0]:
                res.status_code = 400
                return err('No es miembro')

            sql.set_deleted(conn, 'file_requests', data.id)

            res.status_code = 200
            return ok()
    except Exception as e:
        res.status_code = 500
        return log_err(e)
    finally:
        if conn is not None:
            conn.close()
