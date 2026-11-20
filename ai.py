from google import genai
from os import getenv

client = genai.Client(api_key=getenv('GOOGLE_AI'))
