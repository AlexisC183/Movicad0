from app import app

@app.get('/')
def home():
    return { 'message': 'Hello, World!' }
