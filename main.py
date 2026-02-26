# main.py
import os
import time
import json
from matcher import CommandMatcher
from code_executor import execute_code
from voice_engine import listen_for_hotword, listen, speak, play_sound, set_hotword, get_hotword


def main():
    assistant = CommandMatcher()
    
    if assistant.offline_mode:
        print("Assistant is running in offline mode. Semantic matching is disabled.")
        speak("Assistant is running in offline mode. Some features may not work.")

    while True:
        user_choice = input("Type or say a command? (t for type / v for voice / q to quit): ").strip().lower()

        if user_choice == 'q':
            speak("Goodbye!")
            break

        # --- Handle text input ---
        elif user_choice == 't':
            command = input("Type your command: ")

        # --- Handle voice input ---
        elif user_choice == 'v':
            hotword = get_hotword()
            speak(f"Waiting for you to say the hotword: {hotword}")
            if not listen_for_hotword(hotword=hotword):
                continue
            
            speak("I'm listening for your command.")
            command = listen()
            if "Sorry" in command:  # listen() failed
                speak("I didn't catch that. Please try again.")
                continue
            
            play_sound('hotword')
            speak(f"You said: {command}")

        else:
            print("Invalid input.")
            continue

        # --- Process the command ---
        print("[Assistant]: Processing your request...")
        code = assistant.match_command(command)

        if code:
            if "search_google" in code:
                print("\n--- FALLBACK SEARCH ---")
                speak("Searching the web for that now.")
            else:
                print("\n--- GENERATED CODE ---")
            
            try:
                execute_code(code)
            except Exception as e:
                print(f"[Error] {e}")
                speak(f"An error occurred while running your command.")
            finally:
                # ✅ Always confirm completion
                speak("Done.")
                play_sound('complete')

        else:
            speak("Sorry, I couldn't understand the command.")


if __name__ == "__main__":
    main()
