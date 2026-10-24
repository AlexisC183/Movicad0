"""Session-related utilities for the application."""

from fastapi import Request, Response
from datetime import datetime, timezone, timedelta
from models import Session
from res_bodies import err
from db import dbconn
from utils import constants
import secrets
import hashlib

def _gen_session_token():
    return secrets.token_urlsafe(32)

def _hash_session_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(conn, user_id: int):
    """
    Inserts a session in the database.
    The transaction is not committed.
    Returns a new session token.
    """
    token = _gen_session_token()
    now = datetime.now(timezone.utc)
    session = Session(
        0,
        _hash_session_token(token),
        user_id,
        now,
        now + timedelta(seconds=constants.SESSION_AGE_SECONDS)
    )

    with conn.cursor() as c:
        c.execute(
            'insert into sessions values (default, %s, %s, %s, %s)',
            [session.token_hash, session.user_id, session.creation, session.expiration]
        )
    
    return token

def set_auth_cookie(res: Response, token: str):
    """Sets a session cookie."""
    res.set_cookie(
        key='session',
        value=token,
        httponly=True,
        #secure=True
        samesite='lax',
        max_age=constants.SESSION_AGE_SECONDS,
        path='/'
    )

def verify_requester(req: Request, *allowed_roles: str):
    """
    Verifies the authentication token from the session cookie and then from the database.
    If the session exists, verifies that the requester's role is in `allowed_roles`.
    Returns `{ 'fail': False, 'idRolePair': { 'id': int, 'role': str } }` or `{ 'fail': True, 'sc': int, 'body': dict }`.
    """
    token = req.cookies.get('session')

    if not token:
        print('No token found from cookie')
        return {
            'fail': True,
            'sc': 401,
            'body': { 'status': 'logout' }
        }

    conn = None
    try:
        conn = dbconn()
        with conn.cursor() as c:
            c.execute(
                'select u.id, u.role from sessions s join users u on u.id = s.user_id where s.token_hash = %s and s.expiration > now() and u.deleted = false',
                [_hash_session_token(token)]
            )
            user = c.fetchone()

            if user is None:
                print('No user found from database')
                return {
                    'fail': True,
                    'sc': 401,
                    'body': { 'status': 'logout' }
                }

            role = user[1]

            if not role in allowed_roles:
                print('Permission denied')
                return {
                    'fail': True,
                    'sc': 403,
                    'body': { 'status': 'forbidden' }
                }

            return {
                'fail': False,
                'idRolePair': {
                    'id': user[0],
                    'role': role
                }
            }
    except Exception as e:
        print(e)
        return {
            'fail': True,
            'sc': 500,
            'body': err('No se pudo verificar su identidad')
        }
    finally:
        if conn is not None:
            conn.close()
