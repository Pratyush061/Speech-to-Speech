import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import google.generativeai as genai
import os
import gtts
import io
from streamlit_lottie import st_lottie
import requests

# Configure API key
api_key = "AIzaSyA3IpZChb68jheLSM6M6uyIQPrB4a00TwQ"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust speaking rate

# Thread-safe text-to-speech queue
tts_queue = []


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Custom CSS for Styling
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: "Arial", sans-serif;
    }
    .stApp {
        background-color: #f4f4f4;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .main-title {
        color: #4CAF50;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .subheader {
        color: #555555;
        font-size: 1.2em;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    .user-input, .response {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #dddddd;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 1em;
        border-radius: 5px;
        cursor: pointer;
        margin-bottom: 20px;
    }
    button:hover {
        background-color: #45a049;
    }
    .audio-player {
        margin-top: 20px;
    }
    .footer {
        color: #777777;
        text-align: center;
        margin-top: 50px;
        font-size: 0.9em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# UI Initialization
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "response" not in st.session_state:
    st.session_state.response = ""

# App Title and Subtitle
st.markdown("<div class='main-title'>Speech-to-Speech LLM Bot</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Ask questions and hear answers instantly!</div>", unsafe_allow_html=True)

# Helper Functions
def process_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        try:
            audio_data = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {e}"

def text_to_speech_worker():
    while True:
        if tts_queue:
            text = tts_queue.pop(0)
            tts_engine.say(text)
            tts_engine.runAndWait()

def add_to_tts_queue(text):
    tts_queue.append(text)

def text_to_speech(text):
    speech = gtts.gTTS(text=text, lang='en')
    audiofile = io.BytesIO()
    speech.write_to_fp(audiofile)
    audiofile.seek(0)
    return audiofile

def generate_response(input_text):
    prompt = (
        """You are Pratyush AI bot. Help users by answering their questions based on this persona:
        You are Pratyush AI bot. You help people answer questions about your self (i.e Pratyush)
    Answer as if you are responding . don't answer in second or third person.
    If you don't know they answer you simply say "That's a secret"


    Pratyush Jain is a dedicated and enthusiastic B.Tech student specializing in Information Technology at Shri G.S. Institute Of Technology And Science, Indore, Madhya Pradesh. With a passion for technology and innovation, he has developed strong skills in programming, data structures, algorithms, and several key areas of computer science. He is proficient in languages such as C, C++, and Python, and well-versed in libraries and frameworks like Pandas, NumPy, NLTK, Sklearn, OpenCV, MediaPipe, and Matplotlib.
    
    Pratyush has undertaken several impactful projects. He developed a Movie Recommender System using Python and NLP techniques, achieving effective content-based recommendations. His work on Plant Disease Classification involved a robust CNN model, reaching a 97.7% accuracy on test data. Additionally, he built an OpenCV AI Virtual Keyboard, incorporating real-time hand tracking and gesture recognition.
    He Developed YuwaWork, an AI-based freelancing platform featuring profile autofill, real-time freelancer matching using RAG architecture, and automated review summaries using advanced NLP models.

    Pose Detection Model
    He is Collaborating with a client to create a pose detection model using React, Next.js, and TensorFlow.js for accurate and real-time pose analysis.

    Recognized for his problem-solving abilities, Pratyush is a 4-star coder on HackerRank and has received bronze medals on Kaggle for his contributions to notebooks and discussions. His commitment to continuous learning and excellence in the field of computer science is evident in his academic and extracurricular achievements.

    Pratyush also loves to read books he has read 50+ books.Some of his favourites include:
    Atomic Habits
    Ikigai
    Linchpin
    Rich Dad Poor Dad
    Eat That Frog
    Mindset
    Zero to One-A note on startups
    The Defining Decade: Why Your Twenties Matter

    Pratyush is based in Ujjain, Madhya Pradesh, and can be contacted via email at pratyushjj02@gmail.com. You can find more about his professional journey on LinkedIn, GitHub, and Kaggle. He is eager to connect with like-minded professionals and contribute to innovative projects.

    Contact Information:

    Phone: +91-7987517018
    Email: pratyushjj02@gmail.com
    LinkedIn: LinkedIn Profile
    GitHub: GitHub Profile
    Kaggle: Kaggle Profile
        """
        f"User Question: {input_text}"
    )
    response = model.generate_content(prompt)
    return response.text

# Start the TTS Worker Thread
if "tts_thread" not in st.session_state:
    tts_thread = threading.Thread(target=text_to_speech_worker, daemon=True)
    tts_thread.start()
    st.session_state.tts_thread = tts_thread

lottie_gif = load_lottieurl("https://lottie.host/54a91536-4fd5-4d10-8041-827cbce8060f/RPTxx1bRNf.json")


st_lottie(lottie_gif, height=250, key="data")

# Interaction Flow
st.markdown("<div class='user-input'>Click the button to start recording your question:</div>", unsafe_allow_html=True)

if st.button("Record and Ask"):
    user_input = process_audio()
    st.session_state.user_input = user_input
    st.markdown(f"<div class='user-input'><b>User Input:</b> {user_input}</div>", unsafe_allow_html=True)

if st.session_state.user_input:
    st.session_state.response = generate_response(st.session_state.user_input)
    response = st.session_state.response.replace('*', ' ')  # To avoid the speaker saying 'asterisk'
    st.markdown(f"<div class='response'><b>Response:</b> {response}</div>", unsafe_allow_html=True)
    add_to_tts_queue(st.session_state.response)

    # Play the audio response
    audio_file = text_to_speech(response)
    st.audio(audio_file, format="audio/mp3", start_time=0)

# Footer
st.markdown("<div class='footer'>Powered by Generative AI and Streamlit</div>", unsafe_allow_html=True)

# streamlit run main.py
