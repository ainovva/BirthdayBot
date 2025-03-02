import datetime
import speech_recognition as sr
import pyttsx3
import time
import pyaudio
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json

# Initialize Text-to-Speech
engine = pyttsx3.init()
vosk_model = Model("./model/model")
recognizer = KaldiRecognizer(vosk_model, 16000)

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

def speak(text, wait_time=2):
    """Convert text to speech and play it, then pause before proceeding."""
    engine.say(text)
    engine.runAndWait()
    time.sleep(wait_time)  # Pause to give the user time to process

# def listen(device_index=None):
#     """Capture user's voice input and convert it to text."""
#     recognizer = sr.Recognizer()
#     recognizer.pause_threshold = 2  # Allow longer pause before processing speech
#     with sr.Microphone(device_index=device_index) as source:
#         print("Listening... Please say your birthday (e.g., March 14)")
#         speak("Please say the month and day of your birthday, for example, March 19th.")
#         recognizer.adjust_for_ambient_noise(source)
#         try:
#             audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)  # Extended listening time
#             text = recognizer.recognize_google(audio)
#             print(f"You said: {text}")
#             speak(f"You said: {text}")
#             return text
#         except sr.UnknownValueError:
#             print("Sorry, I couldn't understand. Please try again.")
#             speak("Sorry, I couldn't understand. Please try again.", wait_time=2)
#             return None
#         except sr.RequestError:
#             print("Error with the speech recognition service.")
#             return None
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             return None


def listen():
    """Capture user's voice input and convert it to text using Vosk (offline)."""
    speak("Please say your birthday, for example, March 14", wait_time=2)
    print("🎤 Listening... Speak now.")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=None):
        audio_data = sd.rec(int(16000 * 5), samplerate=16000, channels=1, dtype="int16")
        sd.wait()  # Wait until recording is done

    if recognizer.AcceptWaveform(audio_data.tobytes()):
        result = json.loads(recognizer.Result())
        text = result["text"]
        print(f"You said: {text}")
        speak(f"You said: {text}", wait_time=2)
        return text
    else:
        print("Sorry, I couldn't understand. Please try again.")
        speak("Sorry, I couldn't understand. Please try again.", wait_time=2)
        return None

def parse_birthday(input_text):
    """Convert spoken month and day into a MM-DD format."""
    speak("Let me do some math")
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }

    days = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
            "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth",
            "eighteenth", "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third",
            "twenty-fourth", "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth",
            "thirtieth", "thirty-first"]
    month = None
    day = None

    for word in input_text.lower().split():
        if word in months:
            month = months[word]
        elif word in days:
            day = days.index(word) + 1

    if month and day:
        return f"{month:02d}-{day:02d}"  # Format MM-DD
    else:
        speak("Sorry, that didn't work, please try again")
        return None

def days_until_birthday(birthday):
    """Calculate days until the next birthday."""
    today = datetime.date.today()
    birth_month, birth_day = map(int, birthday.split("-"))
    this_year_birthday = datetime.date(today.year, birth_month, birth_day)

    if this_year_birthday < today:
        next_year_birthday = datetime.date(today.year + 1, birth_month, birth_day)
        days_remaining = (next_year_birthday - today).days
    else:
        days_remaining = (this_year_birthday - today).days

    return days_remaining

def main():
    # """Main chatbot loop."""
    # speak("Welcome to the birthday chatbot!", wait_time=2)
    # time.sleep(1)

    while True:
        speak("Welcome to the Birthday Bot!", wait_time=2)
        spoken_birthday = listen()
        if spoken_birthday:
            birthday = parse_birthday(spoken_birthday)
            if birthday:
                days_left = days_until_birthday(birthday)

                if days_left is None:
                    speak("I couldn't understand your birthday. Please try again.")
                    input("Press Enter to try again...")
                    continue

                if days_left == 0:
                    speak("Your birthday is today! Happy birthday!")
                elif days_left > 360:
                    speak(f"Your birthday is in {days_left} days. Happy belated birthday!")
                else:
                    response = f"Your birthday is in {days_left} days."
                    print(response)
                    speak(response)

                input("Press Enter to continue...")

if __name__ == "__main__":
    main()