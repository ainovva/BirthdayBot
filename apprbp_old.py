import datetime
import re
import vosk
import json
import dateparser
import pyttsx3
import sounddevice as sd
import scipy.io.wavfile as wav

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech and play it."""
    engine.say(text)
    engine.runAndWait()

def speak_prompt():
    """Prompt the user to press Enter and start recording."""
    speak("When is your birthday? Say the month and day, like March 19th.")
    return

def record_audio(filename="input.wav", duration=8, samplerate=16000):
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, audio_data)
    return filename

def transcribe_audio(filename="input.wav"):
    """Transcribe recorded audio using Vosk (lightweight ASR model)."""
    model = vosk.Model("model/model")  # Make sure to download and place a Vosk model in this folder
    recognizer = vosk.KaldiRecognizer(model, 16000)

    with open(filename, "rb") as f:
        recognizer.AcceptWaveform(f.read())

    result = json.loads(recognizer.Result())
    text = result.get("text", "")
    print("You said:", text)
    return text

def days_until_birthday(text):
    """Calculate the number of days until the next occurrence of the given birthday."""
    if not text.strip():
        print("No valid input detected.")
        return None

    try:
        parsed_date = dateparser.parse(text)
        if not parsed_date:
            raise ValueError("Invalid date format")

        month = parsed_date.strftime("%B")
        day = parsed_date.day
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None

    today = datetime.date.today()
    birthday = datetime.date(today.year, month, day)

    if birthday < today:
        birthday = datetime.date(today.year + 1, birthday.month, birthday.day)

    return (birthday - today).days

def main():
    while True:
        speak_prompt()
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