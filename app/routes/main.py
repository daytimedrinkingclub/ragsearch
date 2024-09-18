from flask import Blueprint, request, jsonify
from app.services.embeddings_upsert import upsert_article
from app.services.embeddings_search import search_articles

main_bp = Blueprint('main', __name__)

@main_bp.route('/upload_article', methods=['POST'])
def upload_article():
    data = request.json
    article_name = data.get('article_name')
    article_content = data.get('article_content')

    if not article_name or not article_content:
        return jsonify({"error": "Missing article_name or article_content"}), 400

    try:
        result = upsert_article(article_name, article_content)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        results = search_articles(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500