import speech_recognition as sr
import pyttsx3
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import time

# -----------------------------
# INITIALIZE
# -----------------------------

recognizer = sr.Recognizer()

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.Client()
collection = client.get_or_create_collection("knowledge_base")

# -----------------------------
# TEXT TO SPEECH (FIXED)
# -----------------------------

def speak(text):

    print("\nAssistant:", text)

    engine = pyttsx3.init(driverName='sapi5')  # IMPORTANT FIX

    engine.setProperty('rate', 170)

    voices = engine.getProperty('voices')

    if voices:
        engine.setProperty('voice', voices[0].id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

# -----------------------------
# SPEECH TO TEXT
# -----------------------------

def listen():

    with sr.Microphone() as source:

        print("\n🎤 Listening...")

        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

    try:

        query = recognizer.recognize_google(audio)

        print("\nYou:", query)

        return query.lower()

    except Exception as e:

        print("Error:", e)

        return ""

# -----------------------------
# VECTOR SEARCH
# -----------------------------

def search_vector_db(query):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "distances"]
    )

    docs = results["documents"][0]
    distances = results["distances"][0]

    filtered = []

    for doc, dist in zip(docs, distances):

        if dist < 1.0:   # similarity filter
            filtered.append(doc)

    if len(filtered) == 0:
        return None

    return "\n".join(filtered)

# -----------------------------
# OLLAMA (RAG)
# -----------------------------

def ask_llm(question, context):

    prompt = f"""
You are a helpful assistant.

Use the context only if relevant.
If context is not useful, ignore it.

Context:
{context}

Question:
{question}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]

# -----------------------------
# DIRECT OLLAMA (FALLBACK)
# -----------------------------

def ask_direct(question):

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": question}]
    )

    return response["message"]["content"]

# -----------------------------
# MAIN LOOP
# -----------------------------

speak("Voice assistant started")

while True:

    query = listen()

    if query == "":
        continue

    # STOP CONDITION
    if "stop" in query or "exit" in query:

        speak("Goodbye")

        break

    # SMALL DELAY (audio stability fix)
    time.sleep(0.3)

    # VECTOR SEARCH
    context = search_vector_db(query)

    # RAG OR FALLBACK
    if context:
        answer = ask_llm(query, context)
    else:
        answer = ask_direct(query)

    # PRINT + SPEAK
    speak(answer)