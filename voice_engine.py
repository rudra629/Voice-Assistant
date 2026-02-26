# voice_engine.py
import speech_recognition as sr
import pyttsx3
import winsound
import os
import json
import time

def get_hotword():
    """Retrieves the hotword from the configuration file."""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config.get("hotword", "echo")
    except (FileNotFoundError, json.JSONDecodeError):
        set_hotword("echo")
        return "echo"

def set_hotword(new_hotword):
    """Saves a new hotword to the configuration file."""
    with open("config.json", "w") as f:
        json.dump({"hotword": new_hotword.lower()}, f, indent=2)
    return new_hotword

def speak(text):
    """
    Speaks the provided text aloud by initializing a new TTS engine for each command.
    This guarantees reliability and prevents hangs.
    """
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in TTS engine: {e}")
    finally:
        engine.stop()

def play_sound(sound_type):
    """
    Plays a system sound using winsound.
    """
    try:
        if sound_type == 'hotword':
            winsound.Beep(440, 200)
        elif sound_type == 'complete':
            winsound.Beep(660, 200)
    except Exception as e:
        print(f"Error playing sound: {e}")

def listen():
    """
    Listens for a command from the microphone and returns it as text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        return "Sorry, could not understand."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def listen_for_hotword(hotword):
    """
    Listens for the hotword and returns True if it is detected.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Waiting for '{hotword}'...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        if hotword in command:
            return True
        return False
    except sr.UnknownValueError:
        return False
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False