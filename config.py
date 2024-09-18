import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    PINECONE_ENV = os.environ.get('PINECONE_ENV')
    PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME')
    PINECONE_HOST = os.environ.get('PINECONE_HOST')