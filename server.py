import sys
sys.path.append('./Identification')
sys.path.append('./audioRecorder')
sys.path.append('./templates')
# Modules
import sys
import datetime
# Importing Flask
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymongo
#Socket IO
from flask_socketio import SocketIO
#Import Mongo
from pymongo import MongoClient
# Importing Local Py Files
from recordVoice import *
from CreateProfile import CreateProfile
from EnrollProfile import enroll_profile
from EnrollmentResponse import EnrollmentResponse
from IdentificationServiceHttpClientHelper import IdentificationServiceHttpClientHelper

filePath = "/Users/txt-19/Desktop/duckV2/audioRecorder/"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Connecting to DB
connection = pymongo.MongoClient('ds119223.mlab.com', 19223)
db = connection["cube-traffic"]
db.authenticate("admin", "admin")
# Defined the DB's Collection for User's
users = db.users

#Azure Parameters that need to be filled with automatic goodness :)
subscriptionKey = "b51342b216294701b97755a73f959ba4"
locale = "en-us"

#Global Vars
global numberOfTimesEnrolled
numberOfTimesEnrolled = 6
global recordingAudio
recordingAudio = False

profileId = None
# Initializes Create Profile class
CreateProfile = CreateProfile(profileId)

# Essentially the Home Page of Enrollment
@app.route('/', methods=['POST', 'GET'])
def index():
	if 'beginEnrollment' in request.form:
		CreateProfile.create_profile(subscriptionKey, locale)
		global numberOfTimesEnrolled
		numberOfTimesEnrolled = 6
		return redirect(url_for('enrollVoice'))

	else:
		return render_template('index.html')

# The Enrollment Page, where Audio gets recorded and processed
@app.route('/enrollVoice', methods=['POST', 'GET'])
def enrollVoice():

	# The path where the audio file is stored, the specific .wav file used to record this is added to the var filePath
	filePath = "/Users/txt-19/Desktop/duckV2/"
	sendForm = False
	error = None
	global numberOfTimesEnrolled
	global recordingAudio
	recordingAudio = False
	# Converts the Boolean that will be sent to the JS file into a string, this makes it easier for us to use the value easily in JS
	if recordingAudio == False:
		recordingAudio = "false"
	else:
		recordingAudio = "true"

	data = {'recordingAudio': recordingAudio}

	if numberOfTimesEnrolled == 3:
		print("went through 1st query")
	elif numberOfTimesEnrolled == 2:
		print("went through 2nd query")
	elif numberOfTimesEnrolled == 1:
		print("went through 3rd query")
		
			

	# Begins recording someone's voice
	if 'enrollVoice' in request.form: 

		print("Recording...")

		recordingAudio = True

		if recordingAudio == False:
			recordingAudio = "false"
		else:
			recordingAudio = "true"

		# Whether or not someones voice is being recording atm is stored to be sent to a JS file for further use
		data = {'recordingAudio': recordingAudio}

		# return render_template('recordVoice.html', data=data, numberOfTimesEnrolled = "You have to enroll this amount of time: " + str(numberOfTimesEnrolled) + " times!", recordingUserAudio = "Recording User Audio = " + str(recordingAudio))
		
		recordVoice()
		print("audio is saved to... " + str(recordVoice.FULL_FILE_NAME))
		newAudioSavedLocation = recordVoice.FULL_FILE_NAME
		recordingAudio = False
		print("Done Recording!")

		# Path were the new audio file is saved
		enrollmentFilePath = filePath + newAudioSavedLocation
		print("enrollmentFilePath = " + enrollmentFilePath)

		#Enrolls Audio to Newly Created User
		enroll_profile(subscriptionKey, CreateProfile.profileId, enrollmentFilePath, "false")
		if numberOfTimesEnrolled == 1:
			numberOfTimesEnrolled = 6
			return redirect(url_for('enrollUserInfo'))
		numberOfTimesEnrolled -= 1
		print("numberOfTimesEnrolled = " + str(numberOfTimesEnrolled))
		
		# if sendForm:
		# 	userData = {
		# 		"fullName":fullName,
		# 		"profileId":CreateProfile.profileId
		# 	}
		# 	db.users.insert(userData)
		# 	return str(userData)

		return render_template('recordVoice.html', data=data, numberOfTimesEnrolled = "You have to enroll this amount of time: " + str(numberOfTimesEnrolled) + " times", recordingUserAudio = "Recording User Audio = " + str(recordingAudio))
		
	else:
		#return jsonify(numberOfTimesEnrolled=numberOfTimesEnrolled)
		return render_template('recordVoice.html', data=data, numberOfTimesEnrolled = "You have to enroll this amount of time: " + str(numberOfTimesEnrolled) + " times", recordingUserAudio = "Recording User Audio = " + str(recordingAudio))

# This is the page were we get the user's Name
@app.route('/enrollUserInfo', methods=['POST', 'GET'])
def enrollUserInfo():
	now = datetime.datetime.now()
	date =  str(now.month) + "/" + str(now.day) + "/" + str(now.year)

	sendForm = False
	if 'enrollUserInfo' in request.form:
		firstName = request.form['first-name']
		lastName = request.form['last-name']
		parentPhoneNumber = request.form['phone-number']
		emailAddress = request.form['email-address']

		fullName = firstName + " " + lastName
		sendForm = True

	if sendForm:
		# Creates an Object that can be used to store data in our DB
		userData = {
			"fullName":fullName,
			"profileId":CreateProfile.profileId,
			"emailAddress": emailAddress,
			"parentPhoneNumber":parentPhoneNumber,
			"dateCreated": date
		}
		db.users.insert(userData)
		return redirect(url_for('index'))
	else:
		return render_template('enrollUserInfo.html')


"""
@app.route('/signup', methods=['POST', 'GET'])

def signup():
	filePath = "/Users/txt-19/Desktop/duckAi-py/RECORDING.wav"
	sendForm = False
	error = None
	
	if 'recordVoice' in request.form:
		recordVoice()

	if 'createUserId' in request.form:
		firstName = request.form['first-name']
		lastName = request.form['last-name']
		# Full Name
		global fullName
		fullName = firstName + " " + lastName
		CreateProfile.create_profile(subscriptionKey, locale)
		return redirect(url_for('index'))


	if 'enrollAudio' in request.form:
		sendForm = True
		enroll_profile(subscriptionKey, CreateProfile.profileId, filePath, "false")
		
	if sendForm:
		userData = {
			"fullName":fullName,
			"profileId":CreateProfile.profileId
		}
		db.users.insert(userData)
		return str(userData)


	# the code below is executed if the request method
	# was GET or the credentials were invalid
	else:
		return render_template('signup.html', error=error)
"""

if __name__ == "__main__":
	app.run(debug=True)


