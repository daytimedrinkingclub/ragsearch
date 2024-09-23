from pinecone import Pinecone
from flask import current_app
from .embeddings_generator import create_embedding
from .data_service import DataService

class EmbeddingsService:
    @staticmethod
    def upsert_article_embedding(article_id):
        try:
            print(f"Embedding service called to upsert the article with id: {article_id}")
            # Retrieve the article from the database
            article = DataService.get_article_by_id(article_id)
            if not article:
                raise ValueError("Article not found")

            # Generate embedding for the article content
            embedding = create_embedding(article.article_content)
            print(f"Embedding created for the article with id: {article_id}")

            # connect to pinecone and upsert the embeddings with metadata
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
            raise e
    
    @staticmethod
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
        
    @staticmethod
    def update_article_embedding(article_id, new_article_content):
        try:
            # Update the article in the database
            updated_article = DataService.update_article(article_id, new_article_content)
            if not updated_article:
                raise ValueError("Article not found")

            # Delete the old embedding
            pc = Pinecone(api_key=current_app.config['PINECONE_API_KEY'])
            index = pc.Index(current_app.config['PINECONE_INDEX_NAME'])
            index.delete(ids=[article_id])

            # Generate new embedding
            embedding = create_embedding(new_article_content)

            # Upsert the new embedding
            vector = {
                "id": article_id,
                "values": embedding,
                "metadata": {"article_name": updated_article["article_name"]}
            }
            index.upsert(vectors=[vector])

            return {"id": article_id, "article_name": updated_article["article_name"], "embedding_updated": True}
        except Exception as e:
            raise e