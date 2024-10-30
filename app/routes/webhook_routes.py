from flask import Blueprint, request, jsonify
from app.services.anthropic_chat import AnthropicChat
from app.models.chat_model import Chat
from app import db
from app.vendors import Chatwoot
import requests
from flask import current_app

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/', methods=['POST'])
def webhook():
    data = request.json
    if data['event'] == 'message_created' and data['message_type'] == 'incoming':
        user_message = data['content']
        conversation_id = data['conversation']['id']
        
        current_app.logger.debug(f"Chatwoot API request message: {user_message}, conversation_id: {conversation_id}")
        auth_token = data['sender']['custom_attributes'].get('auth_token')
        conversation_category = data['conversation']['custom_attributes'].get('category', "general")
        # Handle the chat
        response = AnthropicChat.handle_chat(None, user_message, category=conversation_category, external_id=conversation_id, auth_token=auth_token)
        
        # Extract the content from the response
        if isinstance(response.content, list) and len(response.content) > 0 and hasattr(response.content[0], 'text'):
            content = response.content[0].text
        else:
            content = str(response.content)
        
        # Send response back to Chatwoot
        response = Chatwoot.add_message(conversation_id, content)
        current_app.logger.debug(f"Chatwoot API response: {response}")
    
    return '', 200