import os
from twilio.rest import Client


account_sid = "AC6968990a7bd22a70f6289fc047c77210"
auth_token = "73f8113314effe357c59c451a699e13f"
client = Client(account_sid, auth_token)

def sendTrafficTextNotification(identifiedSpeaker, parentPhoneNumber):
	client.messages.create(
		to= parentPhoneNumber,
		from_="+1 610-915-8882",
		body=identifiedSpeaker
	)
