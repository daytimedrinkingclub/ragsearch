from pinecone import Pinecone
from app.models import Article
from .embeddings_generator import create_embedding
from flask import current_app

def search_articles(query, top_k=3):
    query_embedding = create_embedding(query)
    pc = Pinecone(api_key=current_app.config['PINECONE_API_KEY'])
    index = pc.Index(current_app.config['PINECONE_INDEX_NAME'])
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    formatted_results = []
    for match in results['matches']:
        article = Article.query.get(match['id'])
        if article:
            formatted_results.append({
                "id": match['id'],
                "article_name": match['metadata']['article_name'],
                "score": match['score'],
                "content_preview": article.article_content
            })

    return formatted_results