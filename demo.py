import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from io import BytesIO
import sounddevice as sd
import soundfile as sf
import numpy as np
import sys
import tty
import termios

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY not set. Please configure in the .env file.")

client = ElevenLabs(api_key=api_key)

# Globals
is_recording = False
fs = 44100 # Sampling rate
stream = None
audio_frames = []

def text_to_speech(text_data):
    """Converts text to speech and plays the audio file."""
    try:
        audio = client.text_to_speech.convert(
            text=text_data,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # Adjust the voice_id if necessary
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        play(audio)
    except Exception as e:
        print(f"Error in Text-to-Speech: {e}")

def speech_to_text(audio_data):
    """Converts speech to text and outputs the result."""
    try:
        transcription = client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",  # Currently only "scribe_v1" is supported
            tag_audio_events=True, # Tags audio events like laughter or applause
            language_code='eng',   # Automatic language detection if None
            diarize=True           # Enable speaker recognition
        )
        return transcription.text
    except Exception as e:
        print(f"Error in Speech-to-Text: {e}")

def audio_callback(indata, frames, time, status):
    """Callback function for audio recording."""
    global audio_frames
    if status:
        print(status, file=sys.stderr)
    audio_frames.append(indata.copy())

def toggle_recording():
    """Starts or stops the recording."""
    global is_recording, stream, audio_frames
    if not is_recording:
        # Start recording
        is_recording = True
        audio_frames = []
        stream = sd.InputStream(samplerate=fs, channels=1, callback=audio_callback)
        stream.start()
        print("\n🎙️ Recording started... Press 's' to stop.")
    else:
        # Stop recording
        is_recording = False
        stream.stop()
        stream.close()
        stream = None
        print("Processing recording...")
        audio_data = np.concatenate(audio_frames, axis=0)
        buffer = BytesIO()
        sf.write(buffer, audio_data, fs, format='WAV')
        buffer.seek(0)
        text = speech_to_text(buffer)
        if text:
            print(f"Recognized: {text}")
            text_to_speech(text)
        print("\nPress 's' for new recording or 'q' to exit.")

def getch():
    """Reads a single character from the keyboard (without Enter)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("Press 's' to start/stop recording or 'q' to exit.")
    while True:
        key = getch()
        if key == 's':
            toggle_recording()
        elif key == 'q':
            print("\nExiting program...")
            if is_recording:
                toggle_recording()  # Stop if still active
            break

if __name__ == "__main__":
    main()