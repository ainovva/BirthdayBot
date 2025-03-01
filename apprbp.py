import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3
import datetime
import re
import vosk
import json
import dateparser

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech and play it."""
    engine.say(text)
    engine.runAndWait()

def record_audio(filename="input.wav", duration=5, samplerate=16000):
    """Record audio and save it as a WAV file."""
    speak("When is your birthday? Say the month and day, like March 19th.")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, audio_data)
    return filename

def transcribe_audio(filename="input.wav"):
    """Transcribe recorded audio using Vosk (lightweight ASR model)."""
    model = vosk.Model("model")  # Make sure to download and place a Vosk model in this folder
    recognizer = vosk.KaldiRecognizer(model, 16000)

    with open(filename, "rb") as f:
        recognizer.AcceptWaveform(f.read())

    result = json.loads(recognizer.Result())
    text = result.get("text", "")
    print("You said:", text)
    return text

def extract_date(text):
    """Extract date using regex and dateparser."""
    text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text)  # Remove ordinal suffixes
    parsed_date = dateparser.parse(text)

    if parsed_date:
        return parsed_date.strftime("%B"), parsed_date.day
    return None, None

def days_until_birthday(text):
    """Calculate days until next birthday."""
    today = datetime.date.today()
    month, day = extract_date(text)

    if not month or not day:
        return None

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