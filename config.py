import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@db:5432/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    PINECONE_ENV = os.environ.get('PINECONE_ENV')
    PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME')
    PINECONE_HOST = os.environ.get('PINECONE_HOST')
    DELTAEX_API_KEY = os.environ.get('DELTAEX_API_KEY')
    CHATWOOT_BASE_URL = os.environ.get('CHATWOOT_BASE_URL')
    CHATWOOT_ACCESS_TOKEN = os.environ.get('CHATWOOT_ACCESS_TOKEN')
    CHATWOOT_ACCOUNT_ID = os.environ.get('CHATWOOT_ACCOUNT_ID')
    CHATWOOT_WEBSITE_TOKEN = os.environ.get('CHATWOOT_WEBSITE_TOKEN')
