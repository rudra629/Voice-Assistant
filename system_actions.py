# system_actions.py
import winshell
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from voice_engine import speak, listen, set_hotword, get_hotword
import pyautogui
import os
import datetime
import webbrowser
import subprocess
from langchain.tools import tool

@tool
def empty_recycle_bin() -> str:
    """Empties the Windows recycle bin."""
    winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
    speak("Recycle bin emptied.")
    return "Recycle bin emptied successfully."

@tool
def set_volume(level: int) -> str:
    """Sets the system volume. Input should be an integer between 0 and 100."""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level / 100, None)
    speak(f"Volume set to {level} percent.")
    return f"Volume successfully set to {level}%."

@tool
def check_battery() -> str:
    """Checks the current battery percentage and charging status of the PC."""
    battery = psutil.sensors_battery()
    percent = battery.percent
    plugged = battery.power_plugged
    status = "plugged in" if plugged else "not charging"
    response = f"Battery is at {percent}% and is currently {status}."
    speak(response)
    return response

@tool
def get_current_time() -> str:
    """Gets the current local time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")
    return f"The time is {now}."

@tool
def check_cpu_usage() -> str:
    """Checks the current CPU usage percentage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    speak(f"The current CPU usage is {cpu_percent} percent.")
    return f"CPU usage is at {cpu_percent}%."

@tool
def open_file(file_path: str) -> str:
    """Opens a file at the specified absolute file path."""
    try:
        os.startfile(file_path)
        speak(f"Opening file.")
        return f"Successfully opened {file_path}."
    except Exception as e:
        return f"Error opening file: {e}"

@tool
def create_folder(folder_name: str) -> str:
    """Creates a new directory/folder with the given name or path."""
    try:
        os.makedirs(folder_name)
        speak(f"Created folder {folder_name}.")
        return f"Folder {folder_name} created."
    except Exception as e:
        return f"Error creating folder: {e}"

@tool
def delete_file(file_path: str) -> str:
    """Deletes a file at the specified path. ONLY use if the user explicitly asks to delete."""
    try:
        os.remove(file_path)
        speak("File deleted.")
        return f"Deleted {file_path}."
    except Exception as e:
        return f"Error deleting file: {e}"

@tool
def open_application(app_name: str) -> str:
    """Opens a common application on the PC by name (e.g., 'notepad', 'chrome', 'spotify', 'word', 'excel')."""
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
            return f"Opened {app_name}."
        except FileNotFoundError:
            pass
    try:
        subprocess.Popen(f'start {app_name}', shell=True)
        speak(f"Opening {app_name}.")
        return f"Opened {app_name}."
    except Exception as e:
        return f"Failed to open {app_name}. Error: {e}"

@tool
def close_active_window() -> str:
    """Closes the currently active window on the screen."""
    pyautogui.hotkey('alt', 'f4')
    speak("Closing active window.")
    return "Active window closed."

@tool
def search_google(query: str) -> str:
    """Searches Google in the default web browser for the provided query."""
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Searching for {query}.")
    return f"Opened Google search for {query}."

@tool
def open_website(url: str) -> str:
    """Opens a specific URL in the default web browser."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    speak("Opening website.")
    return f"Opened {url}."

@tool
def play_pause() -> str:
    """Toggles media playback (Play/Pause) for active media players like Spotify."""
    pyautogui.press('playpause')
    speak("Toggled playback.")
    return "Media play/pause toggled."

@tool
def next_track() -> str:
    """Skips to the next media track."""
    pyautogui.press('nexttrack')
    speak("Next track.")
    return "Skipped to next track."

@tool
def previous_track() -> str:
    """Returns to the previous media track."""
    pyautogui.press('prevtrack')
    speak("Previous track.")
    return "Returned to previous track."

@tool
def maximize_window() -> str:
    """Maximizes the currently active window."""
    pyautogui.hotkey('win', 'up')
    speak("Window maximized.")
    return "Window maximized."

@tool
def minimize_window() -> str:
    """Minimizes the currently active window."""
    pyautogui.hotkey('win', 'down')
    speak("Window minimized.")
    return "Window minimized."

@tool
def change_hotword(new_hotword: str) -> str:
    """Changes the assistant's wake word/hotword."""
    set_hotword(new_hotword)
    speak(f"Hotword changed to {new_hotword}.")
    return f"Hotword updated to {new_hotword}."