from apprbp import record_audio

def test_recording():
    filename = "test.wav"
    record_audio(filename)
    print(f"Recording saved to {filename}")

if __name__ == "__main__":
    test_recording()