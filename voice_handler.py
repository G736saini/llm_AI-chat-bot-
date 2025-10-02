# voice_handler.py
import pyttsx3
import speech_recognition as sr
from config import Config

class VoiceHandler:
    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.initialize_voice()
    
    def initialize_voice(self):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties using Config
            self.engine.setProperty('rate', getattr(Config, 'VOICE_RATE', 150))
            self.engine.setProperty('volume', getattr(Config, 'VOICE_VOLUME', 1.0))
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            
            print("✅ Voice handler initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing voice handler: {e}")
            self.engine = None
            self.recognizer = None
    
    def text_to_speech(self, text, language='en'):
        """Convert text to speech"""
        if not self.engine:
            print("❌ Text-to-speech engine not available")
            return
        
        try:
            # Adjust voice based on language
            if language == 'hi':  # Hindi
                # Try to set Hindi voice if available
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'hindi' in voice.name.lower() or 'indian' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
    
    def speech_to_text(self):
        """Convert speech to text"""
        if not self.recognizer:
            print("❌ Speech recognition not available")
            return None
        
        try:
            with sr.Microphone() as source:
                print("🎙️ Listening... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("❌ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in speech-to-text: {e}")
            return None
    
    def stop_speaking(self):
        """Stop any ongoing speech"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass