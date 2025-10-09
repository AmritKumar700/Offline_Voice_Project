import asyncio
import json
import os
import subprocess
import threading
import time
from datetime import datetime
import numpy as np

# --- Core AI Libraries ---
import whisper
import pyaudio
import pyttsx3
from vosk import Model, KaldiRecognizer

# --- 1. INTEGRATION: Import Your AI Agent's Logic ---
from agent import dispatcher

# ==============================================================================
# SETUP: Load Models and Engines
# ==============================================================================
print("Loading models, please wait...")

# --- Wake Word Configuration ---
WAKE_WORD = "computer"

# --- Models ---
try:
    # High-accuracy model for command recognition (official Whisper)
    whisper_model = whisper.load_model("base.en")
    # Lightweight model for wake word detection
    vosk_model = Model("offline_models/vosk-model-en-us-0.22")
except Exception as e:
    print(f"FATAL: Could not load a required model. {e}")
    exit()

# --- Text-to-Speech (TTS) Engine ---
tts_engine = pyttsx3.init(driverName='nsss')
tts_engine.setProperty('rate', 180)

# --- Audio Stream (PyAudio) ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)

def speak(text: str):
    """Converts text to speech."""
    # Ensure text is a string, as the agent might return other types
    text = str(text) 
    print(f"Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# ==============================================================================
# CORE VOICE PIPELINE
# ==============================================================================

class VoiceUI:
    def __init__(self):
        self.vosk_recognizer = KaldiRecognizer(vosk_model, 16000)
        print("\n--- Voice Assistant Ready ---")

    def listen_for_wake_word(self):
        """Uses lightweight Vosk to listen only for the wake word."""
        print(f"Listening for wake word: '{WAKE_WORD}'...")
        while True:
            data = stream.read(2048, exception_on_overflow=False)
            if self.vosk_recognizer.AcceptWaveform(data):
                result = json.loads(self.vosk_recognizer.Result())
                if WAKE_WORD in result.get("text", ""):
                    print("Wake word detected!")
                    return True

    def listen_for_command(self, timeout=7) -> str:
        """Uses powerful Whisper for high-accuracy command transcription."""
        print(f"Listening for command... ({timeout}s)")
        
        frames = []
        for _ in range(0, int(16000 / 4096 * timeout)):
            frames.append(stream.read(4096))
        
        # Convert the raw audio bytes into a format Whisper can understand
        audio_data = b''.join(frames)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Transcribe the audio
        result = whisper_model.transcribe(audio_np, fp16=False) # fp16=False is recommended for CPUs
        text = result.get("text", "").strip()
        
        print(f"Heard: '{text}'")
        return text

    def run(self):
        """The main operational loop for the assistant."""
        speak("Assistant initialized.")

        while True:
            if self.listen_for_wake_word():
                speak("Yes?")
                command = self.listen_for_command()
                
                if command:
                    # --- INTEGRATION: Send text to your AI Agent ---
                    print(f"Sending command to agent: '{command}'")
                    # We use asyncio.run() to correctly call your async dispatcher
                    agent_response = asyncio.run(dispatcher.dispatch_command(command))
                    
                    # --- RESPONSE: Speak the agent's reply ---
                    speak(agent_response)
                else:
                    speak("I didn't catch that.")

# ==============================================================================
# APPLICATION STARTUP
# ==============================================================================
if __name__ == "__main__":
    try:
        ui = VoiceUI()
        ui.run()
    except KeyboardInterrupt:
        print("\nShutting down assistant.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()