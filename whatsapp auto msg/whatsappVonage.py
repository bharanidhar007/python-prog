#pip install vonage

import vonage

def send_whatsapp_message(sender_number, receiver_number, message, api_key, api_secret):
    """
    Sends a WhatsApp message using Vonage API.
    """
    client = vonage.Client(key=api_key, secret=api_secret)
    whatsapp = vonage.Messaging(client)

    try:
        response = whatsapp.send_message({
            "channel": "whatsapp",
            "message_type": "text",
            "to": receiver_number,
            "from": sender_number,
            "text": message
        })

        if "message_uuid" in response:
            print(f" Message sent successfully from {sender_number} to {receiver_number}")
        else:
            print(f" Failed to send message: {response}")

    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    api_key = input(" *Enter your Vonage API Key: ")
    api_secret = input("* Enter your Vonage API Secret: ")
    sender = input(" Enter sender's WhatsApp number (with country code, e.g., +91234567890): ")
    receiver = input(" Enter receiver's WhatsApp number (with country code, e.g., +91234567890): ")
    message = input(" Enter your message: ")

    send_whatsapp_message(sender, receiver, message, api_key, api_secret)
