import speech_recognition as sr
import os
import webbrowser
import pyautogui
import time
from datetime import datetime

def voice_control():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a command...")
        audio = r.listen(source)
        
    try:
        command = r.recognize_google(audio).lower()
        print(f"Command recognized: {command}")

        # Lock Computer
        if "lock computer" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return f"Executed: {command}"

        # Open Spotify
        elif "open spotify" in command:
            spotify_path = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "Spotify", "Spotify.exe")
            if os.path.exists(spotify_path):
                os.startfile(spotify_path)
                return f"Executed: {command}"
            else:
                return "Spotify is not installed or path is incorrect."

        # Open Chrome
        elif "open chrome" in command:
            os.startfile(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            return f"Executed: {command}"

        # Open Notepad
        elif "open notepad" in command:
            os.startfile(r"C:\Windows\system32\notepad.exe")
            return f"Executed: {command}"

        # Search on Google
        elif "search google for" in command:
            query = command.replace("search google for", "")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Executed: Searching Google for {query}"

        # Search on Wikipedia
        elif "search wikipedia for" in command:
            query = command.replace("search wikipedia for", "")
            webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
            return f"Executed: Searching Wikipedia for {query}"

        # Tell the time
        elif "what time is it" in command:
            current_time = datetime.now().strftime("%H:%M:%S")
            return f"The time is {current_time}"

        # Volume Control
        elif "increase volume" in command:
            pyautogui.press('volumeup')
            return f"Executed: {command}"

        elif "decrease volume" in command:
            pyautogui.press('volumedown')
            return f"Executed: {command}"

        # Screenshot
        elif "take a screenshot" in command:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            return "Screenshot saved."

        # Shutdown the system
        elif "shutdown computer" in command:
            os.system("shutdown /s /t 1")
            return f"Executed: {command}"

        else:
            return "Command not recognized. Please try again."
        
    except sr.UnknownValueError:
        return "Could not understand the command. Please speak clearly."
    except sr.RequestError:
        return "Error with the speech recognition service. Please try again later."

# Example usage:
if __name__ == "__main__":
    response = voice_control()
    print(response)
