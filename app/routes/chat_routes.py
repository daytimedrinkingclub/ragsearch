from flask import Blueprint, request, jsonify, render_template
from app.services.data_service import DataService
from app.services.anthropic_chat import AnthropicChat
import json

chat_bp = Blueprint('chat', __name__)

def message_to_dict(message):
    """Convert a Message object to a dictionary."""
    content = message.content if isinstance(message.content, str) else json.loads(message.content)
    
    return {
        "content": content,
        "role": message.role,
        "tool_name": message.tool_name,
        "tool_use_id": message.tool_use_id,
        "tool_input": message.tool_input,
        "tool_result": message.tool_result,
        "created_at": message.created_at.isoformat()
    }

@chat_bp.route('/create_chat', methods=['POST'])
def create_chat():
    chat_id = DataService.create_chat()
    return jsonify({"chat_id": chat_id}), 201

@chat_bp.route('/send_message', methods=['POST'])
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

@chat_bp.route('/get_chats', methods=['GET'])
def get_chats():
    chats = DataService.get_all_chats()
    serialized_chats = [chat_to_dict(chat) for chat in chats]
    return jsonify(serialized_chats), 200

def chat_to_dict(chat):
    """Convert a Chat object to a dictionary."""
    return {
        "id": str(chat.id),
        "created_at": chat.created_at.isoformat(),
        "messages": [message_to_dict(message) for message in chat.messages]
    }

@chat_bp.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify({"error": "Missing chat_id"}), 400

    try:
        chat = DataService.get_chat_by_id(chat_id)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        messages = chat.messages
        messages_list = [message_to_dict(message) for message in messages]
        return jsonify(messages_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/')
def index():
    return render_template('chat.html', active_tab='Chat')

@chat_bp.route('/<chat_id>')
def chat_page(chat_id):
    return render_template('chat_page.html', chat_id=chat_id, active_tab='Chat')

