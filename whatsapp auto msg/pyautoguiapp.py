import webbrowser
import time
import pyautogui

# Phone number with country code
phone_number = input("Enter recipient's phone number with country code (e.g., +919502685672): ")
message = input("Enter your message: ")


# Open WhatsApp app via the URI scheme
webbrowser.open(f"whatsapp://send?phone={phone_number}&text={message}")

# Give some time for the app to open
time.sleep(3)

# Press 'Enter' to send the message (this simulates the 'Enter' key)
pyautogui.press('enter')

print("Message sent successfully!")