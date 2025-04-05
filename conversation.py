import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from io import BytesIO
import requests
import sounddevice as sd
import soundfile as sf

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY not set. Please configure in the .env file.")

client = ElevenLabs(api_key=api_key)

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
        #print(f"Audio transcription: {transcription.text}")
        return transcription.text
    except Exception as e:
        print(f"Error in Speech-to-Text: {e}")


def record_audio(duration=5, fs=44100):
    """
    Records audio from the microphone.
    Returns a BytesIO object in WAV format.
    """
    print(f"Recording starting for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Recording finished.")
    
    # record in BytesIO object as WAV
    buffer = BytesIO()
    sf.write(buffer, recording, fs, format='WAV')
    buffer.seek(0)
    return buffer

def speech_to_text_from_mic():
    audio_data = record_audio(duration=10)
    return speech_to_text(audio_data)


def test():
    # Text-to-Speech
    sample_text = "Hello, this is a test of the Eleven Labs Text-to-Speech API."
    print("Starting Text-to-Speech...")
    text_to_speech(sample_text)

    # Speech-to-Text
    audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
    print("Loading audio file for Speech-to-Text...")
    try:
        response = requests.get(audio_url)
        response.raise_for_status()
        audio_data = BytesIO(response.content)
        print("Starting Speech-to-Text...")
        speech_to_text(audio_data)
    except Exception as e:
        print(f"Error downloading or processing the audio file: {e}")

if __name__ == "__main__":
    # Speech-to-Text
    text = speech_to_text_from_mic()

    # Text-to-Speech
    text_to_speech(text)
