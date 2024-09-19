from flask import Blueprint, request, jsonify
from app.services.data_service import DataService

article_bp = Blueprint('article', __name__)

@article_bp.route('/upload_article', methods=['POST'])
def upload_article():
    data = request.json
    article_name = data.get('article_name')
    article_content = data.get('article_content')

    if not article_name or not article_content:
        return jsonify({"error": "Missing article_name or article_content"}), 400

    try:
        # Save the article to the database
        result = DataService.create_article(article_name, article_content)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@article_bp.route('/get_articles_list', methods=['GET'])
def get_articles_list():
    articles = DataService.get_all_articles_list()
    return jsonify(articles), 200

@article_bp.route('/get_article_content', methods=['GET'])
def get_article_content():
    article_id = request.args.get('article_id')
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400

    try:
        article = DataService.get_article_by_id(article_id)
        if article is None:
            return jsonify({"error": "Article not found"}), 404
        
        article_data = {
            "id": article.id,
            "article_name": article.article_name,
            "article_content": article.article_content
        }
        return jsonify(article_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_bp.route('/delete_article', methods=['POST'])
def delete_article():
    data = request.json
    article_id = data.get('article_id')
    if not article_id:
        return jsonify({"error": "Missing article_id in request body"}), 400

    try:
        result = DataService.delete_article(article_id)
        return jsonify({"message": "Article deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500