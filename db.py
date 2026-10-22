from os import getenv
import psycopg2

CONFIG = {
    'host': 'localhost',
    'database': 'movicad',
    'user': 'final',
    'password': getenv('FINAL_PASS'),
    'port': 5432
}

def dbconn():
    return psycopg2.connect(**CONFIG)
