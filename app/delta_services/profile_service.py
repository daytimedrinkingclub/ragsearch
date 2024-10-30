from flask import current_app
import requests

class ProfileService:
    @staticmethod
    def get_user_by_auth_token(auth_token):
        url = f"{current_app.config['DELTAEX_BASE_URL']}/v2/profile"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers = headers)
        response.raise_for_status()
        response_json = response.json()
        profile = response_json["result"]
        return profile
        