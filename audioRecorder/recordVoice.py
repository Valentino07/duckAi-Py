import pyaudio
import wave
import pickle
from array import array

global audioFileName

def recordVoice():
    pickle_in = open("./file_number.pickle","rb")
    file_number = pickle.load(pickle_in)
    updated_file_number = pickle.load(pickle_in)

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    FILE_NAME = "RECORDING"
    ENCODING = pyaudio
    audio = pyaudio.PyAudio()  # instantiate the pyaudio

    # recording prerequisites
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    # starting recording
    frames = []
    print("recording")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):

        data = stream.read(CHUNK)
        data_chunk = array('h', data)
        vol = max(data_chunk)
        if (vol >= 0):
            frames.append(data)

        else:
            print("nothing")
            print("\n")



    file_number = []
    x = updated_file_number
    x += 1
    if x >= 3:
        x = 0
    file_number.append(x)
    last_file_number = len(file_number) - 1
    updated_file_number = file_number[last_file_number]

    pickle_out = open("file_number.pickle","wb")
    pickle.dump(file_number,pickle_out)
    pickle.dump(updated_file_number,pickle_out)
    recordVoice.FULL_FILE_NAME = FILE_NAME + str(updated_file_number) + ".wav"
    print(recordVoice.FULL_FILE_NAME)
    pickle_out.close()

    # end of recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # writing to file
    wavfile = wave.open(recordVoice.FULL_FILE_NAME, 'wb')
    wavfile.setnchannels(CHANNELS)
    wavfile.setsampwidth(audio.get_sample_size(FORMAT))
    wavfile.setframerate(RATE)
    wavfile.writeframes(b''.join(frames))  # append frames recorded to file
    wavfile.close()
    return recordVoice.FULL_FILE_NAME
