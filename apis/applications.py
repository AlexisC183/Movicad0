from app import app
from db import dbconn
from fastapi import Request, Response
from utils import constants
from utils.res_bodies import err, log_err, ok
from utils.sessions import verify_requester
from pydantic import BaseModel
from models import Application

class CreateData(BaseModel):
    id: int

@app.post('/api/applications/create')
def create(
    req: Request,
    res: Response,
    data: CreateData
):
    verif = verify_requester(req, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select exists (select 1 from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s)',
                [data.id]
            )
            if not c.fetchone()[0]:
                res.status_code = 400
                return err('La convocatoria no existe')

            c.execute(
                'select id from applications where student_id = %s and call_for_id = %s',
                [verif['idRolePair']['id'], data.id]
            )
            past_application = c.fetchone()

            if past_application:
                c.execute(
                    'update applications set deleted = false where id = %s',
                    [past_application[0]]
                )
            else:
                application = Application(
                    0,
                    verif['idRolePair']['id'],
                    data.id,
                    False
                )
                c.execute(
                    'insert into applications values (default, %s, %s, %s)',
                    [application.student_id, application.call_for_id, application.deleted]
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
    call_for_id: int

@app.delete('/api/applications/delete')
def delete(
    req: Request,
    res: Response,
    data: DeleteData
):
    verif = verify_requester(req, constants.STUDENT)
    if verif['fail']:
        res.status_code = verif['sc']
        return verif['body']

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select exists (select 1 from calls_for cf join users u on cf.administrative_id = u.id where not cf.deleted and not u.deleted and cf.id = %s)',
                [data.call_for_id]
            )
            if not c.fetchone()[0]:
                res.status_code = 400
                return err('La convocatoria no existe')

            c.execute(
                'select id from applications where student_id = %s and call_for_id = %s',
                [verif['idRolePair']['id'], data.call_for_id]
            )
            application = c.fetchone()

            if not application:
                res.status_code = 400
                return err('Nunca se ha postulado a la convocatoria')

            c.execute(
                'update applications set deleted = true where id = %s',
                [application[0]]
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
