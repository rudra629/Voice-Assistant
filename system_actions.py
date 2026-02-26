# system_actions.py
import winshell
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from voice_engine import speak, listen, set_hotword, get_hotword
import pyautogui
import time
import os
import datetime
import webbrowser
import subprocess

def empty_recycle_bin():
    winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
    speak("Recycle bin emptied.")

def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level / 100, None)
    speak(f"Volume set to {level} percent.")

def check_battery():
    battery = psutil.sensors_battery()
    percent = battery.percent
    plugged = battery.power_plugged
    status = "plugged in" if plugged else "not charging"
    speak(f"Battery is at {percent}% and is currently {status}.")

def get_current_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def check_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    speak(f"The current CPU usage is {cpu_percent} percent.")

def open_file(file_path):
    try:
        os.startfile(file_path)
        speak(f"Opening {file_path}")
    except FileNotFoundError:
        speak(f"Sorry, I could not find the file {file_path}.")
    except Exception as e:
        speak(f"An error occurred while trying to open the file: {e}")

def create_folder(folder_name):
    try:
        os.makedirs(folder_name)
        speak(f"Created folder named {folder_name}.")
    except FileExistsError:
        speak(f"The folder {folder_name} already exists.")
    except Exception as e:
        speak(f"An error occurred while creating the folder: {e}")

def delete_file(file_path):
    speak(f"Are you sure you want to delete {file_path}?")
    confirmation = listen()
    if "yes" in confirmation.lower():
        try:
            os.remove(file_path)
            speak(f"Deleted the file {file_path}.")
        except FileNotFoundError:
            speak(f"Sorry, I could not find the file {file_path}.")
        except Exception as e:
            speak(f"An error occurred while trying to delete the file: {e}")
    else:
        speak("File deletion canceled.")

def open_application(app_name):
    app_mapping = {
        "notepad": "notepad.exe",
        "chrome": "chrome.exe",
        "calculator": "calc.exe",
        "spotify": "spotify.exe",
        "word": "winword.exe",
        "excel": "excel.exe"
    }

    app_exe = app_mapping.get(app_name.lower())
    
    if app_exe:
        try:
            subprocess.Popen(app_exe)
            speak(f"Opening {app_name}.")
            return
        except FileNotFoundError:
            pass
    try:
        subprocess.Popen(f'start {app_name}', shell=True)
        speak(f"Opening {app_name}.")
    except Exception as e:
        speak(f"Sorry, I could not find or open the application {app_name}.")
        print(f"Error: {e}")

def close_active_window():
    pyautogui.hotkey('alt', 'f4')
    speak("Closing the active window.")

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Searching Google for {query}.")

def open_website(url):
    webbrowser.open(url)
    speak(f"Opening {url}.")

def play_pause():
    pyautogui.press('playpause')
    speak("Toggling playback.")

def next_track():
    pyautogui.press('nexttrack')
    speak("Skipping to the next track.")

def previous_track():
    pyautogui.press('prevtrack')
    speak("Returning to the previous track.")

def maximize_window():
    pyautogui.hotkey('win', 'up')
    speak("Maximizing the active window.")

def minimize_window():
    pyautogui.hotkey('win', 'down')
    speak("Minimizing the active window.")

def change_hotword(new_hotword):
    """Changes the hotword and provides confirmation."""
    set_hotword(new_hotword)
    speak(f"The hotword has been changed to {new_hotword}.")