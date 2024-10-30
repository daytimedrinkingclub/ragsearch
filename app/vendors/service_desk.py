from flask import current_app
import requests
import json

class ServiceDesk:
    @staticmethod
    def create_ticket_on_freshdesk(payload):
        url = f"{current_app.config['FRESHDESK_API_BASE_URL']}/api/v2/tickets"
        api_key = current_app.config['FRESHDESK_API_KEY']
        payload = json.dumps({
            'subject': payload['subject'],
            'description': payload['description'],
            'email': payload['email'],
            'custom_fields': {
                'cf_user_id': int(payload['user_id'])
            },
            'status': 2,
            'priority': 1
        })
        headers = { 'Content-Type': 'application/json' }
        response = requests.post(url, auth=(api_key, 'X'), headers = headers, data = payload)
        response.raise_for_status()
        return response.json()