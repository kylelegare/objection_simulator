import openai
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer
from threading import Thread
import time
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

# Get OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get Azure Key
speech_key, speech_region = os.getenv("SPEECH_KEY"), os.getenv("SPEECH_REGION")

# Define a function to handle objections
def handle_objection():
    # Generate a common sales objection using OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI that only communicates in sales objections."},
            {"role": "user", "content": "Give me a sales objection."},
        ],
    )
    sales_objection = response.choices[0].message['content']

    # Analyze the sales objection using OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a sales manager reviewing a section of a conversion. You're looking to identify sales objections and then present helpful ways for your sales rep to respond to them"},
            {"role": "user", "content": f"This is a brief section of a sales call'{sales_objection}'"},
            {"role": "user", "content": "Review the transcript and identify and sales objections"},
            {"role": "user", "content": "After identifying use Chris Voss's labeling technique for the objection"},
            {"role": "user", "content": "When you reply the format should be  List the sales objection and Label the sales objection using Chris Voss's labeling technique"},
        ],
    )
    objection_analysis = response.choices[0].message['content']
    

    # Print the analysis to the app
    print("Objection Analysis:", objection_analysis)

    # Speak the sales objection out loud using Azure Cognitive Services Text-to-Speech
    speech_config = SpeechConfig(subscription=speech_key, region=speech_region)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    

    def speak_text(text):
        result = synthesizer.speak_text_async(text).get()

    # Create a new thread to speak the sales objection
    t = Thread(target=speak_text, args=(sales_objection,))
    t.start()

    # Wait for the thread to finish before continuing
    t.join()

    # Initialize speech recognizer
    audio_config = AudioConfig(use_default_microphone=True)
    speech_recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Recognize speech input from the user
    print("Speak your response to the objection...")
    result = speech_recognizer.recognize_once()

    # Combine the user's response with the objection and analyze the result using OpenAI
    response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=[
            {"role": "system", "content": "You are Chris Voss using your techniques to determine how well someone handled an objection."},
            {"role": "user", "content": f"AI Objection: {sales_objection}"},
            {"role": "user", "content": f"Salesperson's response: {response}"},
        ],
    )
    
    analysis = response.choices[0].message['content']

    # Print the analysis to the app
    print("Evaluation of your response:",analysis)

    # Ask the user if they want to handle another objection
    response = input("Do you want to handle another objection? (y/n)")
    if response.lower() == "y":
        handle_objection()

# Ask the user if they want to start
response = input("Do you want to start? (y/n)")
if response.lower() != "y":
    # Exit the app if the user doesn't want to start
    exit()

# Call the handle_objection() function to handle the first objection
handle_objection()
