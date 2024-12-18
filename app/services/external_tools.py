import requests
from flask import current_app
from app.vendors import Chatwoot, ServiceDesk
from app.delta_services import ProfileService

def check_deposit_status(transfer_unique_number, auth_token):
    """
    Checks the deposit status using the provided transfer unique number.
    
    Args:
    transfer_unique_number (str): The unique number of the transfer to check.
    
    Returns:
    dict: The response from the API containing the deposit status.
    """
    url = f"{current_app.config['DELTAEX_BASE_URL']}/v2/deposit/claim"
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    payload = {
        "transfer_unique_no": transfer_unique_number,
        "tx_partner_name": "de_internal"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        response_data = response.json()
        current_app.logger.info(f"Deposit status response: {response_data}")
        success_message = "deposit status fetched successfully"
        current_app.logger.info(success_message)
        return {"success": success_message, "data": response_data}
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            current_app.logger.error(f"Bad request error: {e.response.text}")
            success_message = "deposit status fetched successfully"
            return {"status": success_message, "data": e.response.text}
        else:
            current_app.logger.error(f"HTTP error: {str(e)} body: {e.response.text}")
            return {"status": "Unable to check deposit status. Please try again later.", "data": e.response.text}
    except requests.RequestException as e:
        # Log the error and return a user-friendly message
        current_app.logger.error(f"Error checking deposit status: {str(e)} body: {e.response.text}")
        return {"status": "Unable to check deposit status at this time. Please try again later.", "data": e.response.text}

def get_wallet_details(auth_token):
    """
    get the wallet details for a user.
    
    Returns:
    dict: The response from the API containing wallet details.
    """
    url = f"{current_app.config['DELTAEX_BASE_URL']}/v2/wallet/balances"
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        response_data = response.json()
        return {"success": "wallet details fetched successfully", "data": response_data }
    except requests.RequestException as e:
        # Log the error and return a user-friendly message
        current_app.logger.error(f"Error getting wallet details: {str(e)} body: {e.response.text}")
        return {"status": "Unable to get wallet details at this time. Please try again later.", "data": e.response.text}

def get_order_details(order_id, auth_token):
    """
    get the order details for a user.
    
    Returns:
    dict: The response from the API containing order details.
    """
    url = f"{current_app.config['DELTAEX_BASE_URL']}/v2/orders/{order_id}"
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        response_data = response.json()
        return {"success": "orders details fetched successfully", "data": response_data }
    except requests.RequestException as e:
        # Log the error and return a user-friendly message
        current_app.logger.error(f"Error getting orders details: {str(e)} body: {e.response.text}")
        return {"status": "Unable to get order details", "data": e.response.text}
    
def create_support_ticket(ticket_payload, auth_token):
    try:
        user = ProfileService.get_user_by_auth_token(auth_token)
        ticket_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "subject": ticket_payload["subject"],
            "description": ticket_payload["description"]
        }
        current_app.logger.debug(f"Support ticket payload: {ticket_payload}")
        results = ServiceDesk.create_ticket_on_freshdesk(ticket_payload)
        ticket_url = f"{current_app.config['FRESHDESK_API_BASE_URL']}/a/tickets/{results['id']}"
        return {"success": "Ticket created successfully", "data": ticket_url}
    except Exception as exception:
        current_app.logger.error(f"Error creating support ticket: {str(exception)}")
        return {"status": "Unable to create ticket", "data": exception.response.text}

def engage_human_agent(chat_id):
    try: 
        response = Chatwoot.edit_labels(chat_id)
        return {"success": "Sent the message successfully", "data": response }
    except Exception as exception:
        current_app.logger.error(f"Error engaging human agent: {str(exception)}")
        return {"status": "Unable to connect with delta agent", "data": exception.response.text}