from flask import Blueprint, request, jsonify
from app.services.data_service import DataService
from app.services.anthropic_chat import AnthropicChat

chat_bp = Blueprint('chat', __name__)

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
    return jsonify(chats), 200

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

