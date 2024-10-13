from flask import Blueprint, request, jsonify
from app.services.anthropic_chat import AnthropicChat
from app.models.chat_model import Chat
from app import db
import requests
from flask import current_app

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/', methods=['POST'])
def webhook():
    data = request.json
    if data['event'] == 'message_created' and data['message_type'] == 'incoming':
        user_message = data['content']
        conversation_id = data['conversation']['id']
        
        # Handle the chat
        response = AnthropicChat.handle_chat(None, user_message, external_id=conversation_id)
        
        # Extract the content from the response
        if isinstance(response.content, list) and len(response.content) > 0 and hasattr(response.content[0], 'text'):
            content = response.content[0].text
        else:
            content = str(response.content)
        
        # Send response back to Chatwoot
        chatwoot_response = {
            'content': content,
            'message_type': 'outgoing',
            'private': False
        }
        
        chatwoot_url = f"{current_app.config['CHATWOOT_BASE_URL']}/api/v1/accounts/{current_app.config['CHATWOOT_ACCOUNT_ID']}/conversations/{conversation_id}/messages"
        headers = {
            'Content-Type': 'application/json',
            'api_access_token': current_app.config['CHATWOOT_ACCESS_TOKEN']
        }
        
        response = requests.post(chatwoot_url, json=chatwoot_response, headers=headers)
        current_app.logger.info(f"Chatwoot API response: {response.status_code} - {response.text}")
    
    return '', 200