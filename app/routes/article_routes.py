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
    
@article_bp.route('/get_articles', methods=['GET'])
def get_articles():
    articles = DataService.get_all_articles()
    return jsonify(articles), 200

@article_bp.route('/delete_article', methods=['DELETE'])
def delete_article():
    article_id = request.args.get('article_id')
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400

    try:
        result = DataService.delete_article(article_id)
        return jsonify({"message": "Article deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500