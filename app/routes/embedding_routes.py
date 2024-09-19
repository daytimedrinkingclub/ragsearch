from flask import Blueprint, request, jsonify
from app.services.embeddings_service import upsert_article_embedding

embedding_bp = Blueprint('embedding', __name__)

@embedding_bp.route('/upsert_article', methods=['POST'])
def upsert_article():
    article_id = request.args.get('article_id')
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400

    try:
        result = upsert_article_embedding(article_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


