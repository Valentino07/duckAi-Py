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

# Pygame (Plays Audio File)
import pygame
from pygame import mixer

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

import pywintypes
import pyttsx3
engine = pyttsx3.init()



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

mixer.init()
mixer.music.load('C:/Users/duoma/Desktop/ducky/vgBeep2.wav')

groupQueryInit = False

userGroup = None

# mixer.init()
# mixer.pre_init(frequency=0 ,size=16,channels=2)
# print("mixer initialized")
# mixer.music.load('C:/Users/duoma/Desktop/ducky/vgBeep2.wav')
# print("sound FX loaded")

def listen():
	# Gives function access to outside variables
	global userSpeech 
	global duckQueryInit
	global groupQueryInit
	global userGroup

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

			if groupQueryInit:
				# Places user in a group
				if "1"  in userSpeech:
					print("*User is from Group 1*")
					userGroup = 1
				elif "2"  in userSpeech:
					print("*User is from Group 2*")
					userGroup = 2
				elif "3"  in userSpeech:
					print("*User is from Group 3*")
					userGroup = 3

				engine.say("Say hey duck i'm entering. or say hey duck i'm leaving")
				engine.runAndWait()
				#system("say Say hey duck i'm entering. or say hey duck i'm leaving")
				print("say hey duck i'm entering. or say hey duck i'm leaving")
				print("playing sound FX...")
				mixer.music.play(loops = 0, start = 0.0)
				duckQueryInit = True

			if "Hey Duck" in userSpeech:
				engine.say("Hello, what group are you from?")
				engine.runAndWait()				
				#system("say Hello, what group are you from?")
				print("Hello, what group are you from?")
				
				mixer.music.play(loops = 0, start = 0.0)
				groupQueryInit = True

			elif "hey duck" in userSpeech:
				engine.say("Hello, what group are you from?")
				engine.runAndWait()
				print("Hello, what group are you from?")		
				duckQueryInit = True

			elif "Hey Doug" in userSpeech:
				engine.say("Hello, what group are you from?")
				engine.runAndWait()
				print("Hello, what group are you from?")		
				duckQueryInit = True

			elif "hey doug" in userSpeech:
				engine.say("Hello, what group are you from?")
				engine.runAndWait()
				print("Hello, what group are you from?")		
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
					if len(allUserIds) == 10:
						allUserIds.pop[0:11] = GroupOne
						print (GroupOne)
					print(allUserIds)

			identifiedSpeaker = ""
			# Handles cases when the user says they're entering	
			if "I'm entering" in str(audioTranscripter.speechRecognized):
				engine.say("Processing your input, please wait.")
				engine.runAndWait()
				print("Processing your input, please wait.")
				print("userGroup =" + str(userGroup))
				
				if userGroup == 1: 
					if len(allUserIds[0:10]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[0:10])
					else:
						engine.say("There has not been any users enrolled in yet. Please enroll before trying to using the duck.")
						engine.runAndWait()
						duckQueryInit = False	
						break
				
				if userGroup == 2: 
					if len(allUserIds[10:20]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[10:20])
					else:
						engine.say("Group 2 does not exist. If you forgot your group number, please ask an administrator for it.")
						engine.runAndWait()
						duckQueryInit = False
						break	
				
				if userGroup == 3 :
					if len(allUserIds[20:30]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[20:30])
					else:
						engine.say("Group 3 does not exist. If you forgot your group number, please ask an administrator for it.")
						engine.runAndWait()	
						duckQueryInit = False	
						break		


				if identify_file.identifiedSpeakerId == '00000000-0000-0000-0000-000000000000':
					engine.say("Sorry it seems like something has gone wrong, Please Restart the Duck.")
					engine.runAndWait()
					print("Sorry it seems like something has gone wrong, Please Restart the Duck.")
					
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
					engine.say("Welcome" + identifiedSpeaker)
					sendTrafficTextNotification(identifiedSpeaker + " came into the cube " + logSmsTime, parentPhoneNumber)

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

				engine.say("Processing your input, please wait.")
				engine.runAndWait()
				print("Processing your input, please wait.")
				
				if userGroup == 1: 
					if len(allUserIds[0:10]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[0:10])
					else:
						engine.say("There has not been any users enrolled in yet. Please enroll before trying to using the duck.")
						engine.runAndWait()
						duckQueryInit = False	
						break
				
				if userGroup == 2: 
					if len(allUserIds[10:20]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[10:20])
					else:
						engine.say("Group 2 does not exist. If you forgot your group number, please ask an administrator for it.")
						engine.runAndWait()
						duckQueryInit = False
						break	
				
				if userGroup == 3 :
					if len(allUserIds[20:30]) > 1:
						identify_file(subscriptionKey, newFilePath, True, allUserIds[20:30])
					else:
						engine.say("Group 3 does not exist. If you forgot your group number, please ask an administrator for it.")
						engine.runAndWait()	
						duckQueryInit = False	
						break

				if identify_file.identifiedSpeakerId == '00000000-0000-0000-0000-000000000000':
					engine.say("Sorry it seems like something has gone wrong, Please Restart the Duck.")
					engine.runAndWait()
					print("Sorry it seems like something has gone wrong, Please Restart the Duck.")
				else:
					# Based on the ID returned it assigns that ID to a specific person
					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}):
						identifiedSpeaker = user['fullName']
						print("Identified Speaker = " + identifiedSpeaker)


					for user in userProfiles.find({'profileId':identify_file.identifiedSpeakerId}):
						parentPhoneNumber = user['parentPhoneNumber']
						print("parentPhoneNumber = " + parentPhoneNumber)

					print("Goodbye " + identifiedSpeaker)
					# Says good bye to the Identified Speaker
					engine.say("Goodbye "+ identifiedSpeaker)
					duckQueryInit = False
					sendTrafficTextNotification(identifiedSpeaker + " came into the cube " + logSmsTime, parentPhoneNumber)

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
				engine.say("Say Hey Duck I'm Entering or Hey Duck I'm Leaving")

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