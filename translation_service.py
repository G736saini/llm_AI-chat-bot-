# translation_service.py
import requests

class TranslationService:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = "mymemory"  # Use MyMemory API as fallback
        print("✅ Translation service initialized with MyMemory API")
    
    def translate_text(self, text, target_language='hi'):
        """Translate text using MyMemory API"""
        if not text or not text.strip():
            return text
        
        try:
            # Use MyMemory Translation API (free)
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': 'en|hi',
                'de': 'user@example.com'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data['responseData']['translatedText']
                return translated_text if translated_text and translated_text != text else text
            else:
                return text
                
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text
    
    def is_initialized(self):
        return True