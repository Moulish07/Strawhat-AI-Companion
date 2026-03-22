import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import requests
import os
from google import genai

# Initialize engine variable (will be configured inside the thread)
engine = None

# Initialize Google Gemini AI
try:
    gemini_client = genai.Client(api_key="AIzaSyAAORVSZqh_JR7vDSDLXPpF0aP0nsyYSRo")
except Exception as e:
    print("Warning: Failed to configure Gemini AI.")

# --- LUFFY PHONEBOOK ---
# LUFFY can't securely read your phone, so we teach it numbers directly!
# Add your friends here. Make sure to include the country code (like +1 or +91)
contacts = {
    "papa": "+919434221065",
    "boss": "+0987654321"
}

def speak(audio):
    """Tell LUFFY to speak text aloud and print to the terminal."""
    global engine
    if engine is None:
        # Initialize it exactly when the background thread first speaks!
        engine = pyttsx3.init()
        
    print(f"\nLUFFY: {audio}")
    engine.say(audio)
    engine.runAndWait()

def wish_me():
    """Greet the user based on the time of day."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

def listen():
    """Listen to the microphone and convert speech to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nLUFFY is Listening...")
        # Brief pause to adjust to background noise
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Record the audio
        audio = recognizer.listen(source)

    try:
        print("Processing...")
        command = recognizer.recognize_google(audio, language='en-US')
        print(f"You said: {command}")
        return command.lower()
    except Exception as e:
        # If the microphone didn't hear anything clearly
        return "none"

def process_command(query):
    """Process the user's voice command and take action."""
    # 1. Time Feature
    if 'time' in query:
        # Get the current time in Hour:Minute AM/PM format (e.g. 05:30 PM)
        time_now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {time_now}")
        return True # Return True to keep the conversation loop going
    
    # 1.5 Date Feature
    elif 'date' in query or 'today' in query:
        date_today = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {date_today}")
        return True
    
    # 2. Web Browsing Feature
    elif 'open youtube' in query:
        speak("Opening YouTube...")
        webbrowser.open("https://www.youtube.com")
        return True
    
    elif 'open google' in query:
        speak("Opening Google...")
        webbrowser.open("https://www.google.com")
        return True

    # 3. Wikipedia Feature
    elif 'wikipedia' in query:
        speak("Searching Wikipedia...")
        # Remove the word 'wikipedia' from the query to just search the topic
        query = query.replace("wikipedia", "")
        try:
            # Fetch 2 sentences of summary
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia:")
            speak(results)
        except Exception as e:
            speak("Sorry, I couldn't find a matching Wikipedia page for that.")
        return True

    # 4. Weather Feature
    elif 'weather' in query:
        speak("Checking the weather...")
        try:
            # wttr.in is a free weather service that doesn't need an API key!
            # We use a special format to make it sound like a full sentence.
            res = requests.get('https://wttr.in/?format="%C with a temperature of %t"')
            speak(res.text.replace('"', ''))
        except Exception as e:
            speak("Sorry, I couldn't connect to the weather service.")
        return True

    # 4.5 Conversational Greetings
    elif 'hello' in query or 'hi' in query or 'how are you' in query or 'good morning' in query or 'good afternoon' in query or 'good evening' in query:
        speak("Greetings! I am functioning perfectly and ready to help.")
        return True

    # 4.75 Play Music on YouTube
    elif 'play' in query:
        song = query.replace('play', '').strip()
        speak(f"Playing {song} on YouTube...")
        try:
            import pywhatkit
            # This magically searches YouTube and auto-plays the first video!
            pywhatkit.playonyt(song)
        except Exception:
            speak("Sorry, I couldn't play that song right now.")
        return True

    # 4.8 WhatsApp Messaging Skill
    elif 'whatsapp' in query or 'message' in query:
        speak("Who would you like to message?")
        name = listen()
        if name in contacts:
            speak(f"What is your message for {name}?")
            msg = listen()
            if msg != "none":
                speak(f"Sending your message to {name} via WhatsApp...")
                try:
                    import pywhatkit
                    # Opens WhatsApp Web and literally takes over your keyboard to press Send!
                    pywhatkit.sendwhatmsg_instantly(contacts[name], msg, wait_time=15, tab_close=True, close_time=3)
                except Exception:
                    speak("Sorry, I failed to send the WhatsApp message.")
            else:
                speak("I didn't catch the message. Canceling.")
        elif name != "none":
            speak(f"I am sorry, but {name} is not saved in my contacts.")
        return True

    # 5. Local System Control
    elif 'open notepad' in query:
        speak("Opening Notepad...")
        try:
            os.startfile('notepad.exe')
        except Exception:
            speak("I could not locate Notepad on your system.")
        return True
        
    elif 'open calculator' in query:
        speak("Opening Calculator...")
        try:
            os.startfile('calc.exe')
        except Exception:
            speak("I could not locate the Calculator.")
        return True

    # 6. Exit/Quit Feature
    elif 'exit' in query or 'quit' in query or 'stop' in query:
        speak("Goodbye! Have a great day.")
        return False # Return False to break the loop and close the program
    
    # 6. Ultimate Brain: Google Gemini AI
    elif query != "none" and query != "":
        speak("Consulting my AI networks...")
        try:
            prompt = f"You are Luffy, a highly intelligent and helpful AI assistant. The user says: '{query}'. Provide a very concise, conversational response (1 to 2 sentences max)."
            
            # Use the brand new modern Google GenAI protocol!
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            clean_text = response.text.replace('*', '').replace('#', '')
            speak(clean_text)
        except Exception as e:
            # Print the actual text error to the GUI logic box so we can see it if it fails!
            print(f"\n[DEBUG] Gemini Network Error: {e}")
            speak("I'm sorry, my neural networks are currently unreachable.")
        return True
    
    return True # Keep listening if query was "none"

def run_assistant():
    """Start the JARVIS assistant loop."""
    # IMPORTANT: Fix for Windows Voice Threading
    # This prevents the GUI background thread from silencing the pyttsx3 engine!
    import pythoncom
    pythoncom.CoInitialize()
    
    wish_me()
    speak("I am ready. I will only respond if you say my name first.")
    
    active = True
    while active:
        user_command = listen()
        
        if "luffy" in user_command:
            action = user_command.replace("luffy", "").strip()
            
            if action == "":
                speak("Yes?")
                follow_up = listen()
                if follow_up != "none":
                    active = process_command(follow_up)
            else:
                active = process_command(action)
                
        elif 'exit' in user_command or 'stop' in user_command:
            active = process_command(user_command)

if __name__ == "__main__":
    run_assistant()
