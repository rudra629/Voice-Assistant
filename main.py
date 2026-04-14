# main.py
import os
import sys
from agent_brain import AgenticAssistant
from voice_engine import listen_for_hotword, listen, speak, play_sound, get_hotword

def main():
    # --- IMPORTANT: SET YOUR API KEY ---
    # Either set it in your system environment variables, or uncomment the line below and paste it here:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB-05dDrGtfWLGvrPIfk1dekANCe_PC1Uo"
    
    if "GOOGLE_API_KEY" not in os.environ:
        print("ERROR: GOOGLE_API_KEY environment variable not found.")
        print("Please set it in your terminal or hardcode it in main.py")
        sys.exit(1)

    print("Booting up Agentic OS Control...")
    assistant = AgenticAssistant()

    while True:
        user_choice = input("Type or say a command? (t for type / v for voice / q to quit): ").strip().lower()

        if user_choice == 'q':
            speak("Shutting down.")
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
            
            speak("I'm listening.")
            command = listen()
            
            if "Sorry" in command:  
                speak("I didn't catch that. Please try again.")
                continue
            
            play_sound('hotword')
            speak(f"You said: {command}")

        else:
            print("Invalid input.")
            continue

        # --- Process the command via the Agent ---
        print("[Assistant]: Thinking...")
        
        # The agent dynamically selects a tool or writes code
        final_answer = assistant.execute_command(command)
        
        print(f"\n[Agent Answer]: {final_answer}")
        
        # We speak the LLM's summarized answer back
        speak(final_answer)
        play_sound('complete')

if __name__ == "__main__":
    main()