from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.services.data_service import DataService
from app.services.embeddings_service import EmbeddingsService
from app.services.embeddings_search import search_articles
from firecrawl import FirecrawlApp
import os
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

article_bp = Blueprint('article', __name__)

# Add this new route to scrape and upload articles
@article_bp.route('/scrape_and_upload_articles', methods=['GET'])
def scrape_and_upload_articles():
    try:
        # Initialize Firecrawl
        firecrawl_api_key = 'fc-4f631143aa7346aea8d79d14a6f1cf3b'
        app = FirecrawlApp(api_key=firecrawl_api_key)

        # Define the URL to scrape
        url = 'https://deltaexchangeindia.freshdesk.com/support/solutions'

        # Validate the URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({"error": "Invalid URL provided"}), 400

        logger.info(f"Starting to scrape URL: {url}")

        # Scrape the Delta Exchange India support page
        scrape_result = app.scrape_url(
            url,
            params={'formats': ['markdown']}
        )

        # Extract the first 10 article links from the scraped content
        article_links = scrape_result['markdown'].split('](')[1:11]
        article_links = [link.split(')')[0] for link in article_links]

        logger.info(f"Found {len(article_links)} article links")

        # Scrape and upload each article
        for index, link in enumerate(article_links, start=1):
            logger.info(f"Processing article {index} of {len(article_links)}: {link}")
            article_result = app.scrape_url(link, params={'formats': ['markdown']})
            article_content = article_result['markdown']
            article_name = article_content.split('\n')[0].strip('# ')  # Assume the first line is the title

            # Upload the article using the existing upload_article function
            result = DataService.create_article(article_name, article_content)
            EmbeddingsService.upsert_article_embedding(result['id'])
            logger.info(f"Uploaded article: {article_name}")

        return jsonify({"message": f"Successfully scraped and uploaded {len(article_links)} articles"}), 200
    except Exception as e:
        logger.error(f"Error in scrape_and_upload_articles: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

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
