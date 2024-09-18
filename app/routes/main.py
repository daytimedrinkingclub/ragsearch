from flask import Blueprint, request, jsonify
from app.services.embeddings_upsert import upsert_article
from app.services.embeddings_search import search_articles
from app.services.data_service import DataService
from app.services.anthropic_chat import AnthropicChat

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
    
@main_bp.route('/create_chat', methods=['POST'])
def create_chat():
    chat_id = DataService.create_chat()
    return jsonify({"chat_id": chat_id}), 201

def message_to_dict(message):
    """Convert a Message object to a dictionary."""
    content = ""
    if isinstance(message.content, list):
        for block in message.content:
            if hasattr(block, 'text'):
                content += block.text
    else:
        content = str(message.content)
    
    return {
        "content": content,
        "role": message.role,
        "model": message.model,
        "stop_reason": message.stop_reason,
        "type": message.type,
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens
        }
    }

@main_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')

    if not chat_id or not message:
        return jsonify({"error": "Missing chat_id or message"}), 400

    try:
        response = AnthropicChat.handle_chat(chat_id, message)
        response_dict = message_to_dict(response)
        return jsonify(response_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

