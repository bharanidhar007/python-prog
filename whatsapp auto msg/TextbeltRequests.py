import requests

def send_sms(sender_number, receiver_number, message, api_key):
    """
    Sends an SMS using the Textbelt API.
    """
    url = "https://textbelt.com/text"
    data = {
        "phone": receiver_number,
        "message": message,
        "key": api_key  # Use "textbelt" for a free trial (1 message/day)
    }

    try:
        response = requests.post(url, data=data)
        result = response.json()

        if result.get("success"):
            print(f"Message sent successfully from {sender_number} to {receiver_number}")
        else:
            print(f" Failed to send message: {result.get('error', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sender = input("Enter sender's phone number (for reference only): ")
    receiver = input("Enter receiver's phone number (with country code, e.g., +91234567890): ")
    message = input(" Enter your message: ")
    api_key = input("Enter your Textbelt API Key (or use 'textbelt' for free trial): ")

    send_sms(sender, receiver, message, api_key)
