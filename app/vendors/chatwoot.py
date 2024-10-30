from flask import current_app
import requests

class Chatwoot:

    @staticmethod
    def add_message(conversation_id, content) :
        url = f"{current_app.config['CHATWOOT_BASE_URL']}/api/v1/accounts/{current_app.config['CHATWOOT_ACCOUNT_ID']}/conversations/{conversation_id}/messages"
        headers = {
            'Content-Type': 'application/json',
            'api_access_token': current_app.config['CHATWOOT_ACCESS_TOKEN']
        }
        payload = {
            'content': content,
            'message_type': 'outgoing',
            'private': False
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def edit_labels(conversation_id, labels = ["manual"]):
        url = f"{current_app.config['CHATWOOT_BASE_URL']}/api/v1/accounts/{current_app.config['CHATWOOT_ACCOUNT_ID']}/conversations/{conversation_id}/labels"
        headers = {
            'Content-Type': 'application/json',
            'api_access_token': current_app.config['CHATWOOT_ACCESS_TOKEN']
        }
        payload = {
            'labels': labels
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()