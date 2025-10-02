# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyAG-qx8FgW8gGzxZpuh9LlgFojsX3d7hmU')
    
    # Voice Settings
    VOICE_RATE = 150
    VOICE_VOLUME = 1.0
    VOICE_LANGUAGE = 'en'
    
    # Model Settings
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    
    # Translation Settings
    TRANSLATION_TIMEOUT = 15