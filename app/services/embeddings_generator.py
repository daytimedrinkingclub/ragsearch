from openai import OpenAI
from flask import current_app

def create_embedding(text):
    """Create an embedding for the given text using OpenAI's API."""
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    return response.data[0].embedding