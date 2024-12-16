from flask import Flask, render_template, request, jsonify
import pyttsx3
import speech_recognition as sr
import requests
import json
import time

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyAOu3RGa1zBMzl8qdHpCjOM_wy2V9Wui5M"  # Replace with your actual API key


# Function to process speech and convert it to text using Google's speech recognition
def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

        try:
            print("Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError:
            print("Network error occurred")
            return None


# Function to generate speech (text-to-speech)
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred: {e}")


def query_ai(prompt):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}

    try:
        print(f"Sending request to: {url}")  # Log URL being called
        print(f"Payload: {json.dumps(payload)}")  # Log the payload

        response = requests.post(url, json=payload, headers=headers)
        print(f"Response Status Code: {response.status_code}")  # Log status code
        print(f"Response Content: {response.text}")  # Log the response content

        if response.status_code == 200:
            parsed_response = response.json()
            if 'candidates' in parsed_response:
                return parsed_response["candidates"][0]["content"]["parts"][0]["text"]
            return "Sorry, I couldn't get a response."
        else:
            return "Error: Unable to connect to the AI service."

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while querying the AI: {e}")
        return "An error occurred while processing your request."


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('user_input')

    if user_input:
        response_text = query_ai(user_input)
        speak(response_text)  # Convert response to speech
        return jsonify({"response": response_text})
    return jsonify({"response": "Sorry, I didn't catch that."})


if __name__ == "__main__":
    app.run(debug=True)
