from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3

# Load Whisper model (you can change to "small" or "medium" for better accuracy)
model = WhisperModel("base", compute_type="int8")

# Load responses from file
def load_responses(file_path):
    responses = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                responses[key.lower().strip()] = value.strip()
    return responses

# Text to speech
engine = pyttsx3.init()

def speak(text):
    print("Bot:", text)
    engine.say(text)
    engine.runAndWait()

# Record audio
def record_audio(filename="audio.wav", duration=5, fs=16000):
    print("🎤 Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(filename, fs, audio)

# Convert speech → text using Whisper
def transcribe(filename="audio.wav"):
    segments, info = model.transcribe(filename)

    text = ""
    for segment in segments:
        text += segment.text

    return text.lower().strip()

# Load your file
responses = load_responses("FUN.txt")

print("🚀 Voice Assistant Started (Whisper Mode)")

while True:
    # Step 1: record voice
    record_audio()

    # Step 2: convert to text
    user_input = transcribe()

    print("You said:", user_input)

    # Step 3: match response
    reply = "Sorry, I don't understand"

    for key in responses:
        if key in user_input:
            reply = responses[key]
            break

    # Step 4: speak response
    speak(reply)