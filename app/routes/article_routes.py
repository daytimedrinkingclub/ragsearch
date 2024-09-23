from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.services.data_service import DataService
from app.services.embeddings_service import EmbeddingsService
from app.services.embeddings_search import search_articles

article_bp = Blueprint('article', __name__)

# this route adds the article to the database and upserts the embeddings to pinecone
@article_bp.route('/upload_article', methods=['POST'])
def upload_article():
    data = request.form
    article_name = data.get('article_name')
    article_content = data.get('article_content')

    if not article_name or not article_content:
        return jsonify({"error": "Missing article_name or article_content"}), 400

    try:
        result = DataService.create_article(article_name, article_content)
        EmbeddingsService.upsert_article_embedding(result['id'])
        return redirect(url_for('article.index'))
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
    data = request.form
    article_id = data.get('article_id')
    if not article_id:
        return jsonify({"error": "Missing article_id in request body"}), 400

    try:
        EmbeddingsService.delete_article_embedding(article_id)
        DataService.delete_article(article_id)
        return redirect(url_for('article.index'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_bp.route('/update_article', methods=['POST'])
def update_article():
    data = request.form
    article_id = data.get('article_id')
    new_article_content = data.get('new_article_content')

    if not article_id or not new_article_content:
        return jsonify({"error": "Missing article_id or new_article_content"}), 400

    try:
        result = EmbeddingsService.update_article_embedding(article_id, new_article_content)
        if result:
            return redirect(url_for('article.index'))
        else:
            return jsonify({"error": "Article not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_bp.route('/')
def index():
    articles = DataService.get_all_articles_list()
    return render_template('index.html', articles=articles, active_tab='Articles')

@article_bp.route('/add_article', methods=['GET'])
def add_article():
    return render_template('add_article.html')

@article_bp.route('/edit_article/<article_id>', methods=['GET'])
def edit_article(article_id):
    article = DataService.get_article_by_id(article_id)
    if article is None:
        return jsonify({"error": "Article not found"}), 404
    return render_template('edit_article.html', article=article)

@article_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    try:
        results = search_articles(query)
        return results
    except Exception as e:
        return jsonify({"error": str(e)}), 500