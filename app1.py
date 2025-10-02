# app.py
import streamlit as st
import requests
import pyttsx3
import speech_recognition as sr
import os
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="AI ChatBot with Translation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
GROQ_API_KEY = "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"
GOOGLE_API_KEY = "AIzaSyAG-qx8FgW8gGzxZpuh9LlgFojsX3d7hmU"

class VoiceHandler:
    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.initialize_voice()
    
    def initialize_voice(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            return True
        except Exception as e:
            st.error(f"Voice initialization failed: {e}")
            return False
    
    def text_to_speech(self, text):
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except Exception as e:
                st.error(f"Text-to-speech error: {e}")
                return False
        return False
    
    def speech_to_text(self):
        if self.recognizer:
            try:
                with sr.Microphone() as source:
                    st.info("🎙️ Listening... Speak now!")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.WaitTimeoutError:
                st.error("No speech detected")
            except sr.UnknownValueError:
                st.error("Could not understand audio")
            except Exception as e:
                st.error(f"Speech recognition error: {e}")
        return None

class TranslationService:
    def __init__(self):
        self.use_mymemory = True  # Use MyMemory API as fallback
    
    def translate_text(self, text, target_language='hi'):
        """Translate text using MyMemory API (free and doesn't require enablement)"""
        if not text or not text.strip():
            return text
        
        try:
            # Use MyMemory Translation API
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
            st.error(f"Translation error: {e}")
            return text

class ChatEngine:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.conversation_history = []
    
    def send_message(self, message):
        try:
            # Prepare messages with history
            messages = []
            for role, content in self.conversation_history[-6:]:  # Keep last 6 exchanges
                messages.append({"role": role, "content": content})
            
            messages.append({"role": "user", "content": message})
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            response = completion.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append(("user", message))
            self.conversation_history.append(("assistant", response))
            
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        self.conversation_history = []

def main():
    # Initialize session state
    if 'chat_engine' not in st.session_state:
        st.session_state.chat_engine = ChatEngine(GROQ_API_KEY)
    if 'voice_handler' not in st.session_state:
        st.session_state.voice_handler = VoiceHandler()
    if 'translation_service' not in st.session_state:
        st.session_state.translation_service = TranslationService()
    if 'current_language' not in st.session_state:
        st.session_state.current_language = 'en'
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 AI ChatBot")
        st.markdown("---")
        
        # Language selection
        st.subheader("🌐 Language Settings")
        language = st.radio(
            "Select Language:",
            ["English", "Hindi"],
            index=0 if st.session_state.current_language == 'en' else 1
        )
        st.session_state.current_language = 'en' if language == "English" else 'hi'
        
        # Model info
        st.subheader("⚙️ Settings")
        st.info(f"Current Model: llama-3.1-8b-instant")
        st.info(f"Voice: {'✅ Available' if st.session_state.voice_handler.engine else '❌ Disabled'}")
        st.info(f"Translation: ✅ Available")
        
        # Controls
        st.markdown("---")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_engine.clear_history()
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🎙️ Voice Input", use_container_width=True):
            voice_text = st.session_state.voice_handler.speech_to_text()
            if voice_text:
                # Add voice input to chat
                st.session_state.messages.append({"role": "user", "content": voice_text})
                st.rerun()
    
    # Main area
    st.title("💬 AI ChatBot with Translation")
    st.markdown("Chat with AI and get instant English to Hindi translation!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                ai_response = st.session_state.chat_engine.send_message(prompt)
                
                # Translate if Hindi is selected
                if st.session_state.current_language == 'hi':
                    with st.spinner("🌐 Translating to Hindi..."):
                        translated_response = st.session_state.translation_service.translate_text(ai_response, 'hi')
                    
                    # Display both versions
                    st.subheader("English:")
                    st.write(ai_response)
                    st.subheader("Hindi Translation:")
                    st.write(translated_response)
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"**English:** {ai_response}\n\n**Hindi:** {translated_response}"
                    })
                else:
                    # Display only English
                    st.write(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Text-to-speech option
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔊 Speak Response", use_container_width=True):
                text_to_speak = st.session_state.translation_service.translate_text(ai_response, 'hi') if st.session_state.current_language == 'hi' else ai_response
                st.session_state.voice_handler.text_to_speech(text_to_speak)
        
        with col2:
            if st.button("🔄 New Conversation", use_container_width=True):
                st.rerun()
    
    # Translation section
    st.markdown("---")
    st.subheader("🌐 Quick Translation")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        text_to_translate = st.text_area(
            "Enter text to translate to Hindi:",
            placeholder="Type your English text here...",
            height=100
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🚀 Translate", use_container_width=True):
            if text_to_translate:
                with st.spinner("Translating..."):
                    translated = st.session_state.translation_service.translate_text(text_to_translate, 'hi')
                
                st.success("Translation Complete!")
                st.text_area("Hindi Translation:", value=translated, height=100)
                
                # Speak translation
                if st.button("🔊 Speak Translation", use_container_width=True):
                    st.session_state.voice_handler.text_to_speech(translated)
            else:
                st.warning("Please enter some text to translate.")

if __name__ == "__main__":
    main()