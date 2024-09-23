from flask import Blueprint, request, jsonify, render_template
from app.services.data_service import DataService
from app.services.anthropic_chat import AnthropicChat
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# Route Definitions
@chat_bp.route('/')
def index():
    """Render the main chat page."""
    return render_template('chat.html', active_tab='Chat')

@chat_bp.route('/<chat_id>')
def chat_page(chat_id):
    """Render a specific chat page."""
    return render_template('chat_page.html', chat_id=chat_id, active_tab='Chat')

@chat_bp.route('/get_chats', methods=['GET'])
def get_chats():
    """Get all chats."""
    try:
        chats = DataService.get_all_chats()
        serialized_chats = [chat_to_dict(chat) for chat in chats]
        return jsonify(serialized_chats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/create_chat', methods=['POST'])
def create_chat():
    """Create a new chat."""
    try:
        chat_id = DataService.create_chat()
        return jsonify({"chat_id": chat_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to a chat."""
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')

    if not chat_id or not message:
        return jsonify({"error": "Missing chat_id or message"}), 400

    try:
        response = AnthropicChat.handle_chat(chat_id, message)
        print('Response: ', response)
        
        # Extract the text from the first TextBlock object in the response content
        if isinstance(response.content, list) and len(response.content) > 0 and hasattr(response.content[0], 'text'):
            content = response.content[0].text
        else:
            content = str(response.content)
        
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    """Get the chat history for a specific chat."""
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

# Helper Functions
def chat_to_dict(chat):
    """Convert a Chat object to a dictionary."""
    return {
        "id": str(chat.id),
        "messages": [message_to_dict(message) for message in chat.messages]
    }

def message_to_dict(message):
    """Convert a Message object to a dictionary."""
    content = message.content
    if isinstance(content, list):
        content = [block_to_dict(block) for block in content]
    elif not isinstance(content, str):
        content = str(content)
    
    return {
        "content": content,
        "role": message.role
    }

def block_to_dict(block):
    """Convert a TextBlock object to a dictionary."""
    if hasattr(block, 'text'):
        return {"text": block.text}
    return str(block)