#first install pywhatkit 

import pywhatkit as kit

# Phone number with country code, message, and time (24hr format)
phone_number = "+918688389382"  # Replace with recipient's number
message = "Hello! This is an automated message from my Python script."
hour = 23  # 3 PM
minute = 11  # 3:30 PM

# Send the message
#kit.sendwhatmsg(phone_number, message, hour, minute)
#or
kit.sendwhatmsg_instantly(phone_number, message)
print("Message scheduled successfully!")
