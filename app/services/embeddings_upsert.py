import uuid
from extensions import db
from app.models import Article
from .embeddings_generator import create_embedding
from pinecone import Pinecone
from flask import current_app

def upsert_article(article_name, article_content):
    try:
        # Generate embedding
        embedding = create_embedding(article_content)

        # Generate a unique ID
        unique_id = str(uuid.uuid4())

        # Store in database
        new_article = Article(id=unique_id, article_name=article_name, article_content=article_content)
        db.session.add(new_article)
        db.session.commit()

        # Upsert to Pinecone
        pc = Pinecone(api_key=current_app.config['PINECONE_API_KEY'])
        index = pc.Index(current_app.config['PINECONE_INDEX_NAME'])
        vector = {
            "id": unique_id,
            "values": embedding,
            "metadata": {"article_name": article_name}
        }
        index.upsert(vectors=[vector])

        return {"id": unique_id, "article_name": article_name}
    except Exception as e:
        db.session.rollback()
        raise e