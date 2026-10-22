from app import app
from fastapi import Response
from pydantic import BaseModel
from functools import partial
from utils import constants
from utils.validation import assertion_fail
from utils.res_bodies import err
import re


# @app.get('/')
# def home():
#     return { 'message': 'Hello, World!' }
# https://pytutorial.com/fastapi-tutorial-build-your-first-python-rest-api/

class CreateReq(BaseModel):
    id: str
    password: str
    password1: str
    role: str

@app.post('/api/users/create')
def create(req: CreateReq, res: Response):
    if req.password != req.password1:
        res.status_code = 400
        return err('Las contraseñas no coinciden')
    if body := assertion_fail(req, {
        'id': (
            lambda id: 1 <= len(id) <= 50 and bool(re.match('\\w+', id, re.ASCII)),
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

    return { 'message': 'Everything seems fine' }
        