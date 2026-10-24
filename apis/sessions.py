from fastapi import Request, Response
from app import app
from utils.res_bodies import ok
from utils.sessions import verify_requester
from utils import constants

@app.get('/api/sessions/verify-session')
def verify_session(req: Request, res: Response):
    verif = verify_requester(req, constants.ADMINISTRATIVE, constants.STUDENT)

    res.status_code = 200
    if verif['fail']:
        return ok({ 'idRolePair': None })
    return ok({ 'idRolePair': verif['idRolePair'] })
