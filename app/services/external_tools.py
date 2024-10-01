import requests
from flask import current_app

def check_deposit_status(transfer_unique_number):
    """
    Checks the deposit status using the provided transfer unique number.
    
    Args:
    transfer_unique_number (str): The unique number of the transfer to check.
    
    Returns:
    dict: The response from the API containing the deposit status.
    """
    url = "https://cdn-ind.testnet.deltaex.org/v2/deposit/claim"
    headers = {
        "Authorization": current_app.config['DELTAEX_API_KEY'],
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
        success_message = "Deposit is completed successfully"
        current_app.logger.info(success_message)
        return {"success": success_message, "data": response_data}
    except requests.RequestException as e:
        # Log the error and return a user-friendly message
        current_app.logger.error(f"Error checking deposit status: {str(e)}")
        return {"status": "Unable to check deposit status at this time. Please try again later.", "data": e.response.text}