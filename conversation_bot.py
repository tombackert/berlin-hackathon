# conversation_bot.py
import os
import sys
import tty
import termios
from io import BytesIO
from dotenv import load_dotenv
import numpy as np
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from mistral import initModel, sendMessage  # Unchanged functions

load_dotenv()

class VoiceInterface:
    def __init__(self):
        self.is_recording = False
        self.fs = 44100
        self.stream = None
        self.audio_frames = []
        self.el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.context = []  # Context for Mistral
        self.system_prompt = "You are a helpful assistant."

        initModel()

    def text_to_speech(self, text_data):
        try:
            audio = self.el_client.text_to_speech.convert(
                text=text_data,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            play(audio)
        except Exception as e:
            print(f"Text-to-Speech error: {e}")

    def speech_to_text(self, audio_data):
        try:
            transcription = self.el_client.speech_to_text.convert(
                file=audio_data,
                model_id="scribe_v1",
                tag_audio_events=True,
                language_code='eng'
            )
            return transcription.text
        except Exception as e:
            print(f"Speech-to-Text error: {e}")
            return None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.audio_frames.append(indata.copy())

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_frames = []
        self.stream = sd.InputStream(
            samplerate=self.fs,
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()
        print("\n🎙️ Recording started...")

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.stream = None
        
        audio_data = np.concatenate(self.audio_frames, axis=0)
        buffer = BytesIO()
        sf.write(buffer, audio_data, self.fs, format='WAV')
        buffer.seek(0)
        return buffer

    def process_interaction(self):
        audio_buffer = self.stop_recording()
        user_text = self.speech_to_text(audio_buffer)
        
        if user_text:
            print(f"Recognized: {user_text}")
            
            global context  # Take from mistral.py
            self.context = sendMessage(
                context=self.context,
                user_message=user_text,
                system_prompt=self.system_prompt
            )
            
            ai_response = self.context[-1]['content']
            print(f"AI: {ai_response}")
            self.text_to_speech(ai_response)

    def get_user_input(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def run(self):
        print("Press 's' to start/stop, 'q' to quit")
        while True:
            key = self.get_user_input()
            if key == 's':
                if not self.is_recording:
                    self.start_recording()
                else:
                    print("\nProcessing...")
                    self.process_interaction()
                    print("\nReady for new input")
                    print("Press 's' to start/stop, 'q' to quit")
            elif key == 'q':
                print("\nExiting program...")
                if self.is_recording:
                    self.stop_recording()
                break

if __name__ == "__main__":
    # Check environment variables
    required_keys = ['ELEVENLABS_API_KEY', 'MISTRAL_API_KEY']
    for key in required_keys:
        if not os.getenv(key):
            raise ValueError(f"Missing environment variable: {key}")
    
    VoiceInterface().run()