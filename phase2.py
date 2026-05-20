import streamlit as st
import os
import shutil
import requests
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pyttsx3

# =========================================================
# TEXT TO SPEECH ENGINE
# =========================================================

tts = pyttsx3.init()

def speak(text):
    tts.say(text)
    tts.runAndWait()

# =========================================================
# SPEECH TO TEXT
# =========================================================

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio).lower()
    except:
        return ""

# =========================================================
# MODEL
# =========================================================

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# =========================================================
# DATA
# =========================================================

training_data = {
    "browser_issue": [
        "Chrome is not opening",
        "Chrome is very slow",
        "Websites are not loading",
        "Chrome is broken"
    ]
}

all_sentences = []
all_labels = []

for label, sentences in training_data.items():
    for s in sentences:
        all_sentences.append(s)
        all_labels.append(label)

sentence_embeddings = model.encode(all_sentences)

# =========================================================
# AUTOMATION FUNCTIONS
# =========================================================

def close_chrome():
    os.system("taskkill /f /im chrome.exe")

def check_internet():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except:
        return False

def clear_cache():
    path = os.path.expandvars(
        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data\Default\Cache"
    )
    shutil.rmtree(path, ignore_errors=True)

def restart_system():
    os.system("shutdown /r /t 5")

def reset_browser():
    path = os.path.expandvars(
        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data"
    )
    shutil.rmtree(path, ignore_errors=True)

# =========================================================
# STEPS
# =========================================================

steps = [
    "Close Google Chrome",
    "Restart the system",
    "Clear Chrome cache",
    "Check internet connection",
    "Reset browser settings"
]

automation_map = {
    "Close Google Chrome": close_chrome,
    "Restart the system": restart_system,
    "Clear Chrome cache": clear_cache,
    "Check internet connection": check_internet,
    "Reset browser settings": reset_browser
}

# =========================================================
# STREAMLIT UI
# =========================================================

st.set_page_config(page_title="Voice AI Troubleshooting", layout="centered")
st.title("🛠 Voice AI Troubleshooting Assistant")

# =========================================================
# MAIN FLOW
# =========================================================

if st.button("🎙 Start Voice Assistant"):

    # STEP 1: USER SPEECH
    user_text = listen()
    st.write("🗣 You said:", user_text)

    if user_text:

        user_emb = model.encode([user_text])

        sim = cosine_similarity(user_emb, sentence_embeddings)

        best_index = np.argmax(sim)
        score = sim[0][best_index]
        label = all_labels[best_index]

        if score > 0.45:

            st.success("Issue Identified: Browser Issue")

            # STEP 2: SPEAK CONFIRMATION QUESTION
            question = "Can I perform the troubleshooting steps for your issue?"
            st.write("🤖 AI:", question)
            speak(question)

            # STEP 3: LISTEN FOR CONFIRMATION
            response = listen()
            st.write("🗣 User Response:", response)

            if "yes" in response:

                speak("Okay, I will start fixing the issue")

                st.write("## 🛠 Running Troubleshooting Steps")

                for step in steps:

                    st.write("✔", step)

                    if step in automation_map:
                        try:
                            result = automation_map[step]()

                            if step == "Check internet connection":
                                if result:
                                    st.success("Internet OK")
                                else:
                                    st.error("No Internet")

                        except:
                            st.error(f"Failed: {step}")

                speak("All steps completed. Is your issue resolved?")

                # STEP 4: FINAL FEEDBACK (VOICE)
                final_response = listen()
                st.write("🗣 Final Feedback:", final_response)

                if "yes" in final_response:
                    speak("Great! Issue resolved successfully")

                else:
                    speak("Okay, I will escalate this issue for advanced support")

            else:
                speak("Okay, I will not perform any actions")

        else:
            st.error("Issue not recognized")