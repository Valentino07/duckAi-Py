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
import pygame
from pygame import mixer
import speech_recognition as sr
# Audiofile to Text
from audioTranscriber import *
# SMS Lib
from send_sms import sendTrafficTextNotification
# Audio Recorder module
from recordVoice import *
# Azure Module
from IdentificationServiceHttpClientHelper import *
from IdentifyFile import *
import pymongo
# import pywintypes <---- For WINDOWS 'say'
import pyttsx3
engine = pyttsx3.init()


# MongoDB
connection = pymongo.MongoClient('ds119223.mlab.com', 19223)
db = connection["cube-traffic"]
db.authenticate("admin", "admin")
# Defined the DB's Collection for Traffic
traffic = db.traffic
userProfiles = db.users
# Azure Subscription Key
subscriptionKey = 'b51342b216294701b97755a73f959ba4'
# Pygame Mixer
mixer.init()
# Duck Global Vars
duckQueryInit = False
userSpeech = ""
newFilePath = ""
groupQueryInit = False
userGroup = None
allUserIds = []
users = []
# Input Device Vars
CHUNK_SIZE = 64700
FORMAT = pyaudio.paInt16
RATE = 211600

# Finds out what group the user is in
def duckQuery():
    global groupQueryInit
    engine.say("Hello, what group are you from?")
    engine.runAndWait()
    print("Hello, what group are you from?")
    mixer.music.load('../vgBeep2.wav')
    mixer.music.play(loops = 0, start = 0.0)
    groupQueryInit = True
# Identifies the user and logs them in the DB
def identifyUser(trafficType):
	global userGroup
	global duckQueryInit
	global userProfiles
	global allUserIds
	global newFilePath
	global date
	global logSmsTime
	global clockTime
	
	print("userGroup =" + str(userGroup))
	if userGroup == 1: 
			if len(allUserIds[0:10]) > 1:
					identify_file(subscriptionKey, newFilePath, True, allUserIds[0:10])
			else:
					engine.say("There has not been any users enrolled in yet. Please enroll before trying to using the duck.")
					engine.runAndWait()
					print("There have not been any users enrolled in yet. Please enroll before trying to using the duck.")
					duckQueryInit = False	
	elif userGroup == 2: 
			if len(allUserIds[10:20]) > 1:
					identify_file(subscriptionKey, newFilePath, True, allUserIds[10:20])
			else:
					engine.say("Group 2 does not exist. If you forgot your group number, please ask an administrator for it.")
					engine.runAndWait()
					print("Group 2 does not exist")
					duckQueryInit = False	
	elif userGroup == 3 :
			if len(allUserIds[20:30]) > 1:
					identify_file(subscriptionKey, newFilePath, True, allUserIds[20:30])
			else:
					engine.say("Group 3 does not exist. If you forgot your group number, please ask an administrator for it.")
					engine.runAndWait()
					print("Group 3 Does not Exist")	
					duckQueryInit = False	
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
			if trafficType == "entering":
					print("Welcome " + identifiedSpeaker)
					engine.say("Welcome" + identifiedSpeaker)
					engine.runAndWait()
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
			else:
					print("Goodbye " + identifiedSpeaker)
					# Says good bye to the Identified Speaker
					engine.say("Goodbye "+ identifiedSpeaker)
					engine.runAndWait()
					duckQueryInit = False
					sendTrafficTextNotification(identifiedSpeaker + " left the cube " + logSmsTime, parentPhoneNumber)

					userData = {
							"fullName":identifiedSpeaker,
							"profileId":identify_file.identifiedSpeakerId,
							"trafficQuery":"Left",
							"date": date,
							"time": clockTime
					}
					db.traffic.insert(userData)
					allUserIds = []	
					duckQueryInit = False	

# Listens for what the User says
def listen():
	global userSpeech 
	global duckQueryInit
	global groupQueryInit
	global userGroup

	conversationInit = False

	r = sr.Recognizer()
	r.energy_threshold = 4000
	if not duckQueryInit:
		with sr.Microphone() as source:
			print("Listening...")
			audio = r.listen(source)
	try:
		if not duckQueryInit:
			print("You said: " + r.recognize_google(audio))
			userSpeech = r.recognize_google(audio)

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
				mixer.music.load('../vgBeep2.wav')
				mixer.music.play(loops = 0, start = 0.0)
				print("say hey duck i'm entering. or say hey duck i'm leaving")
				print("playing sound FX...")
				duckQueryInit = True

			if "Hey Duck" in userSpeech:	
				duckQuery()
			elif "hey duck" in userSpeech:
				duckQuery()
			elif "Hey Doug" in userSpeech:
				duckQuery()		
			elif "hey doug" in userSpeech:
				duckQuery()

		# Look for a audio file to text converter, you send the audio file to a funciton and it outputs text
		while duckQueryInit:
			global allUserIds
			global newFilePath
			global date
			global logSmsTime
			global clockTime
			
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

			# Records Audio
			print("Recording Audio...")
			groupQueryInit = False
			recordVoice()
			print("Done Recording!")
			# Allows user to know that their conversation is being processed
			engine.say("Processing your input, please wait.")
			engine.runAndWait()
			print("Processing your input, please wait.")

			# Creates a file path that can be send to Azure
			newFilePath = '/Users/duoma/Desktop/ducky/duckRecognition/'+str(recordVoice.FULL_FILE_NAME)
			print("newFilePath = "+ newFilePath)
			# Translate audio file into text
			audioTranscripter(newFilePath)
			
			logSmsTime = "on " + date + " at " + clockTime
			
			# Adds azure profileIds to an Array
			for user in userProfiles.find():
				userIds = user['profileId']
				if userIds not in allUserIds:
					allUserIds.append(userIds)
					print(allUserIds)

			identifiedSpeaker = ""
			# Handles cases when the user says they're entering	
			if "I'm entering" in str(audioTranscripter.speechRecognized):
				identifyUser("entering")
			# Handles cases when the user says they're leaving	
			elif "I'm leaving" in str(audioTranscripter.speechRecognized):
				identifyUser("leaving")
			else:
				# engine.say("Say Hey Duck I'm Entering or Hey Duck I'm Leaving")
				print("Say Hey Duck I'm Entering or Hey Duck I'm Leaving")

	except sr.UnknownValueError:
		print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

starttime = time.time()

# Loop that runs the duck
while True:
	listen()
	print("duckQueryInit = " + str(duckQueryInit))
	time.sleep(1.0 - ((time.time() - starttime) % 1.0))                                                                 
