from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request, Response
from pydantic import BaseModel
from app import app
from db import dbconn
from utils.res_bodies import ok, log_err, err
from utils.sessions import verify_requester, create_session, set_auth_cookie, delete_session, delete_auth_cookie
from utils import constants

class LogInData(BaseModel):
    id: str
    password: str

@app.post('/api/sessions/log-in')
def log_in(res: Response, data: LogInData):
    key = data.id.strip()
    conn = None

    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select id, password from users where not deleted and key = %s',
                [key]
            )
            user = c.fetchone()

            if not user:
                res.status_code = 401
                return err('El identificador o contraseña es incorrecto')
            try:
                PasswordHasher().verify(user[1], data.password)
            except VerifyMismatchError:
                res.status_code = 401
                return err('El identificador o contraseña es incorrecto')

            token = create_session(conn, user[0])
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

@app.get('/api/sessions/log-out')
def log_out(req: Request, res: Response):
    token = req.cookies.get('session')

    if token:
        conn = None
        try:
            conn = dbconn()
            delete_session(conn, token)
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()

    delete_auth_cookie(res)
    res.status_code = 200
    return ok()

@app.get('/api/sessions/verify-session')
def verify_session(req: Request, res: Response):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)

    res.status_code = 200
    if verif['fail']:
        return ok({ 'idRolePair': None })
    return ok({ 'idRolePair': verif['idRolePair'] })
