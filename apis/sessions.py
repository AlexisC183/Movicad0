from fastapi import Request, Response
from app import app
from db import dbconn
from utils.res_bodies import ok, log_err

@app.get('/api/sessions/verify-session')
