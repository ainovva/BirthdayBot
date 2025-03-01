import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3
import datetime
import whisper
from bs4 import BeautifulSoup
import spacy
import re

# Initialize Text-to-Speech
input("Press Enter to start recording...")
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

def speak(text):
    """Convert text to speech and play it."""
    engine.say(text)
    engine.runAndWait()

def record_audio(filename="input.wav", duration=5, samplerate=16000):
    """Record audio and save it as a WAV file."""
    speak("When is your birthday? Say the month and day, like March 19th. That's Benji's birthday!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, audio_data)
    return filename

def transcribe_audio(filename="input.wav"):
    """Transcribe recorded audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    print("You said:", result["text"])
    return result["text"]

def extract_date(text):
    """Extract a valid month and day from text using SpaCy and regex for better accuracy."""
    doc = nlp(text)
    month = None
    day = None

    # Define valid month names
    months = {m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"], start=1)}

    # Step 1: Remove ordinal suffixes (e.g., "19th" -> "19")
    text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text)
    

    # Step 2: Use SpaCy to detect months
    for ent in doc.ents:
        if ent.label_ == "DATE":
            tokens = ent.text.split()
            for token in tokens:
                if token in months:  # Match month names
                    month = token

    # Step 3: Use regex to extract the day separately
    day_match = re.search(r'\b(\d{1,2})\b', text)  # Matches 1-2 digit numbers
    if day_match:
        day = day_match.group(1)

    
    return (month, day) if month and day else (None, None)

def days_until_birthday(text):
    """Calculate days until the next occurrence of the given birthday."""
    today = datetime.date.today()
    month, day = extract_date(text)

    if not month or not day:
        return None  # Return None if the date couldn't be determined

    try:
        birth_date = datetime.date(today.year, datetime.datetime.strptime(month, "%B").month, int(day))
        if birth_date < today:
            birth_date = datetime.date(today.year + 1, birth_date.month, birth_date.day)
        return (birth_date - today).days
    except Exception:
        return None
    

def main():
    while True:
        record_audio()
        speak("Ok, let me process that.")
        birthday = transcribe_audio()
        speak("I understood you said " + birthday)
        print(birthday)
        days_left = days_until_birthday(birthday)
        if days_left is None:
            speak("I couldn't understand your birthday. Please try again.")
            input("Press Enter to try again...")
            continue
        if days_left == 0:
            speak("Your birthday is today! Happy birthday to you!")
            input("Press Enter to continue...")
            continue
        if days_left > 360:
            speak(f"Your birthday is in {days_left} days, happy belated birthday!")
            input("Press Enter to continue...")
            continue
        response = f"Your birthday is in {days_left} days."
        print(response)
        speak(response)
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
