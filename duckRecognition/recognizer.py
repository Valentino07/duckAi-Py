#!/usr/bin/env python3
# Requires PyAudio and PySpeech.

# Miscellaneous
import sys
sys.path.append('../Identification')
sys.path.append('../audioRecorder')
import os
from os import system
import time
from datetime import datetime
userSpeech = ""

# Azure
from IdentificationServiceHttpClientHelper import *
from IdentifyFile import *

# Audio Recorder
from recordVoice import *

# Speech to Text
import speech_recognition as sr

# Text to Speech
import pyttsx3

# Audiofile to Text
from audioTranscriber import *

# SMS
from send_sms import sendTrafficTextNotification

# Traffic DB
import pymongo
connection = pymongo.MongoClient('ds119223.mlab.com', 19223)
db = connection["cube-traffic"]
db.authenticate("admin", "admin")

# Defined the DB's Collection for Traffic
traffic = db.traffic
userProfiles = db.users

# Good for getting names but not good for getting profileIds
allUserIds = []
users = []

# Azure Subscription Key
subscriptionKey = 'b51342b216294701b97755a73f959ba4'

duckQueryInit = False

# Sets input device
CHUNK_SIZE = 64700
FORMAT = pyaudio.paInt16
RATE = 211600

#p = pyaudio.PyAudio()
os.system("start ../vgBeep.wav")
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')
# for i in range(0, numdevices):
#         if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#             print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
# devinfo = p.get_device_info_by_index(1)
# print(devinfo)
def listen():
	# Gives function access to outside variables
	global userSpeech 
	global duckQueryInit

	conversationInit = False
	# Record Audio
	r = sr.Recognizer()
	r.energy_threshold = 4000
	if not duckQueryInit:
		with sr.Microphone() as source:
			print("Listening...")
			audio = r.listen(source)

	# Speech recognition using Google Speech Recognition
	try:
		# for testing purposes, we're just using the default API key
		# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
		# instead of `r.recognize_google(audio)`
		if not duckQueryInit:
			print("You said: " + r.recognize_google(audio))
			userSpeech = r.recognize_google(audio)

			if "Goodbye Duck" in userSpeech:
				system('say Goodybye human')
			elif "Bye Duck" in userSpeech:
				system('say Goodybye human')
			elif "Shut up duck" in userSpeech:
				system("Well that's rude")

			if "Hey Duck" in userSpeech:
				print("Hello, say hey duck i'm entering. or say hey duck i'm leaving")
				system("say Hello, say hey duck i'm entering. or say hey duck i'm leaving")
				duckQueryInit = True

			elif "hey duck" in userSpeech:
				system('say Hello, are you entering or leaving')
				print("Hello, say hey duck i'm entering. or say hey duck i'm leaving")
				duckQueryInit = True

			elif "Hey Doug" in userSpeech:
				system('say Hello, are you entering or leaving')
				print("Hello, say hey duck i'm entering. or say hey duck i'm leaving")
				duckQueryInit = True

			elif "hey doug" in userSpeech:
				system('say Hello, are you entering or leaving')
				print("Hello, say hey duck i'm entering. or say hey duck i'm leaving")
				duckQueryInit = True

		# Look for a audio file to text converter, you send the audio file to a funciton and it outputs text
		
		while duckQueryInit:
			global allUserIds
			now = datetime.now()

			# Converts standard time, so that it's not in military time and defines whether it's AM or PM
			if now.hour >= 13:
				hour = str(now.hour - 12)
				meridiem = "PM"
			elif now.hour == 0:
				hour = str(12)
				meridiem = "AM"
			else:
				hour = str(now.hour)
				meridiem = "AM"

			date = str(datetime.now().strftime('%m-%d-%Y'))

			minute = now.minute

			if minute < 10:
				minute = str("0" + str(minute))
			else:
				minute = str(minute)



			clockTime = hour + ":" + minute + " " + meridiem

			print("Recording Audio...")
			recordVoice()
			print("Done Recording!")
			newFilePath = '/Users/duoma/Desktop/ducky/duckRecognition/'+str(recordVoice.FULL_FILE_NAME)
			print("newFilePath = "+ newFilePath)
			audioTranscripter(newFilePath)
			
			logSmsTime = "on " + date + " at " + clockTime
			

			for user in userProfiles.find():
				userIds = user['profileId']
				if userIds not in allUserIds:
					allUserIds.append(userIds)
					print(allUserIds)


			identifiedSpeaker = ""
			# Handles cases when the user says they're entering	
			if "I'm entering" in str(audioTranscripter.speechRecognized):
				print("Processing your input...")
				system('say Processing your input...')
				identify_file(subscriptionKey, newFilePath, True, allUserIds)

				if identify_file.identifiedSpeakerId == '00000000-0000-0000-0000-000000000000':
					system("say Sorry but it seems like you haven't enrolled. Can you do that please before logging in?")
					print("Sorry but it seems like you haven't enrolled. Can you do that please before logging in?")
				else:
					# Based on the ID returned it assigns that ID to a specific person
					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}): 
						identifiedSpeaker = user['fullName']
						print("Identified Speaker = " + identifiedSpeaker)

					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}):
						parentPhoneNumber = user['parentPhoneNumber']
						print("parentPhoneNumber = " + parentPhoneNumber)

					# Says welcome to the Identified Speaker
					print("Welcome " + identifiedSpeaker)
					system("say Welcome" + identifiedSpeaker)
					#sendTrafficTextNotification(identifiedSpeaker + " came into the cube " + logSmsTime, parentPhoneNumber)

					userData = {
						"fullName":identifiedSpeaker,
						"profileId":identify_file.identifiedSpeakerId,
						"trafficQuery":"Entered",
						"date": date,
						"time": clockTime
					}

					db.traffic.insert(userData)
					allUserIds = []
					duckQueryInit = False

			# Handles cases when the user says they're leaving	
			elif "I'm leaving" in str(audioTranscripter.speechRecognized):

				print("Processing your input...")
				system('say currently processing your input please wait...')
				
				identify_file(subscriptionKey, newFilePath, True, allUserIds)

				if identify_file.identifiedSpeakerId == '00000000-0000-0000-0000-000000000000':
					system("say Sorry but it seems like you haven't enrolled. Can you do that please before logging in?")
					print("Sorry but it seems like you haven't enrolled. Can you do that please before logging in?")
				else:
					# Based on the ID returned it assigns that ID to a specific person
					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}):
						identifiedSpeaker = user['fullName']
						print("Identified Speaker = " + identifiedSpeaker)


					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}):
						parentPhoneNumber = user['parentPhoneNumber']
						print("parentPhoneNumber = " + parentPhoneNumber)

					print("Welcome " + identifiedSpeaker)
					# Says good bye to the Identified Speaker
					system("say Goodbye "+ identifiedSpeaker)
					duckQueryInit = False
					#sendTrafficTextNotification(identifiedSpeaker + " came into the cube " + logSmsTime, parentPhoneNumber)

					userData = {
						"fullName":identifiedSpeaker,
						"profileId":identify_file.identifiedSpeakerId,
						"trafficQuery":"Left",
						"date": date,
						"time": clockTime
					}
					db.traffic.insert(userData)
					allUserIds = []
			else:
				system("say Say Hey Duck I'm Entering or Hey Duck I'm Leaving")

	except sr.UnknownValueError:
		print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

starttime=time.time()

# Allows the duck to continuously run
while True:
	listen()
	print("duckQueryInit = " + str(duckQueryInit))
	print ("tick")
	time.sleep(1.0 - ((time.time() - starttime) % 1.0))                                                                 