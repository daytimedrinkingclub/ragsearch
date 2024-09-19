from pinecone import Pinecone
from flask import current_app
from .embeddings_generator import create_embedding
from .data_service import DataService


def upsert_article_embedding(article_id):
    try:
        # Retrieve the article from the database
        article = DataService.get_article_by_id(article_id)
        if not article:
            raise ValueError("Article not found")

        # Generate embedding
        embedding = create_embedding(article.article_content)


        # Upsert to Pinecone
        pc = Pinecone(api_key=current_app.config['PINECONE_API_KEY'])
        index = pc.Index(current_app.config['PINECONE_INDEX_NAME'])
        vector = {
            "id": article_id,
            "values": embedding,
            "metadata": {"article_name": article.article_name}
        }
        index.upsert(vectors=[vector])

        return {"id": article_id, "article_name": article.article_name, "embedding_created": True}
    except Exception as e:
        # If there's an error with Pinecone, we might want to handle it differently
        # For now, we'll just re-raise the exception
        raise e
    
def delete_article_embedding(article_id):
    try:
        # Delete from database
        if DataService.delete_article(article_id):
            # Delete from Pinecone
            pc = Pinecone(api_key=current_app.config['PINECONE_API_KEY'])
            index = pc.Index(current_app.config['PINECONE_INDEX_NAME'])
            index.delete(ids=[article_id])
            return True
        return False
    except Exception as e:
        raise e