# main_chatbot.py
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich import box
import requests

from config import Config
from voice_handler import VoiceHandler
from translation_service import TranslationService
from chat_engine import ChatEngine

class ChatBot:
    def __init__(self):
        self.console = Console()
        
        # Initialize services with proper configuration
        self.voice_handler = VoiceHandler()
        
        # Pass Google API key directly to translation service
        self.translation_service = TranslationService(api_key=Config.GOOGLE_API_KEY)
        
        self.chat_engine = ChatEngine()
        self.is_running = True
        self.current_language = 'en'
        
        # Test services immediately
        self.test_all_services()
        
        # Check and validate API keys
        self.validated_models = self.validate_api_keys_and_models()
    
    def test_all_services(self):
        """Test all services on startup"""
        self.console.print("\n" + "="*60)
        self.console.print("🧪 TESTING ALL SERVICES")
        self.console.print("="*60)
        
        # Test Voice Handler
        if self.voice_handler.engine:
            self.console.print("✅ Voice Handler: Initialized")
        else:
            self.console.print("❌ Voice Handler: Failed to initialize")
        
        # Test Translation Service
        if self.translation_service.is_initialized():
            self.console.print(f"✅ Translation Service: {self.translation_service.client.upper()} API")
            
            # Test translation
            test_text = "Hello, how are you?"
            try:
                translated = self.translation_service.translate_text(test_text, 'hi')
                self.console.print(f"   📝 Test: '{test_text}' → '{translated}'")
            except Exception as e:
                self.console.print(f"   ❌ Translation test failed: {e}")
        else:
            self.console.print("❌ Translation Service: Failed to initialize")
        
        # Test Chat Engine
        if hasattr(self.chat_engine, 'client') and self.chat_engine.client:
            self.console.print("✅ Chat Engine: Initialized")
        else:
            self.console.print("❌ Chat Engine: Failed to initialize")
        
        self.console.print("="*60)
        self.console.print("🧪 Service testing completed!")
        self.console.print("="*60 + "\n")
    
    def validate_api_keys_and_models(self):
        """Validate API keys and get available models"""
        validated = {
            'groq': {'valid': False, 'models': [], 'error': None},
            'google': {'valid': False, 'models': [], 'error': None}
        }
        
        # Validate Groq API Key
        try:
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {Config.GROQ_API_KEY}"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json().get('data', [])
                available_models = [model['id'] for model in models_data]
                
                specific_models = ['allam-2-7b', 'whisper-large-v3', 'llama-3.1-8b-instant']
                validated_models = [model for model in specific_models if model in available_models]
                
                validated['groq']['valid'] = True
                validated['groq']['models'] = validated_models
            else:
                validated['groq']['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            validated['groq']['error'] = str(e)
        
        # Validate Google API Key
        try:
            if self.translation_service.is_initialized():
                validated['google']['valid'] = True
                validated['google']['models'] = ["Translation API"]
            else:
                validated['google']['error'] = "Translation service not initialized"
        except Exception as e:
            validated['google']['error'] = str(e)
        
        self.display_validation_results(validated)
        return validated
    
    def display_validation_results(self, validated):
        """Display API key validation results"""
        groq_status = validated['groq']
        google_status = validated['google']
        
        validation_text = """
🔍 [bold]API Key Validation Results:[/bold]

"""
        
        # Groq status
        if groq_status['valid']:
            validation_text += f"✅ [green]Groq API: VALID[/green]\n"
            validation_text += f"   Available models: {len(groq_status['models'])}\n"
            for model in groq_status['models']:
                validation_text += f"   - {model}\n"
        else:
            validation_text += f"❌ [red]Groq API: INVALID[/red]\n"
            validation_text += f"   Error: {groq_status['error']}\n"
        
        validation_text += "\n"
        
        # Google status
        if google_status['valid']:
            validation_text += f"✅ [green]Google API: VALID[/green]\n"
            validation_text += f"   Available services: {', '.join(google_status['models'])}\n"
        else:
            validation_text += f"❌ [red]Google API: INVALID[/red]\n"
            validation_text += f"   Error: {google_status['error']}\n"
        
        self.console.print(Panel(validation_text, title="API Validation", 
                               style="green" if groq_status['valid'] and google_status['valid'] else "yellow"))
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
🤖 [bold cyan]AI ChatBot[/bold cyan] - Multi-Model Assistant

[bold]Available Models:[/bold]
• 🇸🇦 allam-2-7b - Arabic-focused AI model
• 🎙️ whisper-large-v3 - Advanced Speech Recognition
• ⚡ llama-3.1-8b-instant - Fast instant responses

[bold]Features:[/bold]
• 💬 AI-powered conversations
• 🎙️ Voice input and output
• 🌐 English to Hindi translation
• 📝 Multi-language support

[bold]Commands:[/bold]
• Type your message to chat with AI
• 'voice' - Use voice input
• 'translate <text>' - Translate text to Hindi
• 'clear' - Clear conversation history
• 'language' - Switch between English/Hindi
• 'model' - Change AI model
• 'status' - Show detailed status
• 'quit' or 'exit' - Exit program
"""
        
        self.console.print(Panel(welcome_text, box=box.DOUBLE, style="cyan"))
    
    def get_user_input(self):
        """Get input from user"""
        try:
            options = ["voice", "translate", "clear", "language", "model", "status", "quit", "exit"]
            
            input_method = Prompt.ask(
                "\n💬 How would you like to input?",
                choices=["text", "voice", "command"],
                default="text"
            )
            
            if input_method == "voice":
                text = self.voice_handler.speech_to_text()
                if text:
                    return text
                else:
                    self.console.print("❌ Voice input failed. Please type your message.")
                    return self.get_user_input()
            
            elif input_method == "command":
                command = Prompt.ask("🔧 Enter command", choices=options)
                return command
            
            else:  # text
                text = Prompt.ask("📝 Enter your message")
                return text
                
        except KeyboardInterrupt:
            return "quit"
        except Exception as e:
            self.console.print(f"❌ Input error: {e}")
            return self.get_user_input()
    
    def handle_command(self, command):
        """Handle special commands"""
        command = command.lower().strip()
        
        if command in ['quit', 'exit']:
            self.is_running = False
            return None
            
        elif command == 'clear':
            self.chat_engine.clear_history()
            self.console.print("✅ Conversation history cleared", style="green")
            return "clear"
            
        elif command == 'voice':
            text = self.voice_handler.speech_to_text()
            if text:
                return text
            else:
                return "voice_failed"
                
        elif command == 'language':
            self.current_language = 'hi' if self.current_language == 'en' else 'en'
            lang_name = "Hindi" if self.current_language == 'hi' else "English"
            self.console.print(f"🌐 Language switched to: {lang_name}", style="green")
            return "language_changed"
            
        elif command == 'model':
            if self.validated_models['groq']['valid']:
                new_model = self.get_available_models()
                self.chat_engine.set_model(new_model)
                self.console.print(f"🤖 AI model changed to: {new_model}", style="green")
            else:
                self.console.print("❌ Cannot change model: Groq API not available", style="red")
            return "model_changed"
            
        elif command == 'status':
            self.show_detailed_status()
            return "status_shown"
            
        elif command.startswith('translate'):
            text_to_translate = command[9:].strip()
            if text_to_translate:
                try:
                    translated = self.translation_service.translate_text(text_to_translate, 'hi')
                    self.console.print(
                        Panel(
                            f"[bold]English:[/bold] {text_to_translate}\n\n[bold green]Hindi:[/bold green] {translated}",
                            title="🌐 Translation Result",
                            border_style="yellow",
                            box=box.ROUNDED
                        )
                    )
                except Exception as e:
                    self.console.print(f"❌ Translation failed: {e}", style="red")
            else:
                self.console.print("❌ Please provide text to translate. Usage: translate <text>")
            return "translation_done"
            
        else:
            return command
    
    def get_available_models(self):
        """Get available models for selection"""
        if not self.validated_models['groq']['valid']:
            return "llama-3.1-8b-instant"
        
        available_models = self.validated_models['groq']['models']
        
        self.console.print("\n🤖 [bold]Available AI Models:[/bold]")
        for i, model in enumerate(available_models, 1):
            self.console.print(f"   {i}. {model}")
        
        try:
            choice = Prompt.ask(
                "Select model (number) or press Enter for default",
                default="3",
                show_choices=False
            )
            if choice.isdigit() and 1 <= int(choice) <= len(available_models):
                return available_models[int(choice) - 1]
        except:
            pass
        
        default_model = "llama-3.1-8b-instant" if "llama-3.1-8b-instant" in available_models else available_models[0]
        self.console.print(f"✅ Using model: [green]{default_model}[/green]")
        return default_model
    
    def show_detailed_status(self):
        """Show detailed status"""
        current_model = getattr(self.chat_engine, 'current_model', 'Not set')
        
        status_info = f"""
💡 [bold]Current Status:[/bold]

🤖 [bold cyan]Groq AI:[/bold cyan] {'✅ Connected' if self.validated_models['groq']['valid'] else '❌ Disabled'}
   Model: {current_model}
   Available Models: {len(self.validated_models['groq']['models'])}

🌐 [bold cyan]Google Services:[/bold cyan] {'✅ Connected' if self.validated_models['google']['valid'] else '❌ Disabled'}
   Translation: {'✅ Available' if self.translation_service.is_initialized() else '❌ Disabled'}

🔊 [bold cyan]Voice Features:[/bold cyan]
   Input: {'✅ Available' if self.voice_handler.recognizer else '❌ Disabled'}
   Output: {'✅ Available' if self.voice_handler.engine else '❌ Disabled'}

🌍 [bold cyan]Translation:[/bold cyan] {'✅ Available' if self.translation_service.is_initialized() else '❌ Disabled'}
   Current Language: {'Hindi' if self.current_language == 'hi' else 'English'}
"""
        
        self.console.print(Panel(status_info, title="Detailed Status", border_style="blue"))
    
    def show_status(self):
        """Show current status"""
        current_model = getattr(self.chat_engine, 'current_model', 'Not set')
        
        status_info = f"""
💡 [bold]Current Status:[/bold]
• AI Model: {current_model}
• Language: {'Hindi' if self.current_language == 'hi' else 'English'}
• Voice: {'✅ Available' if self.voice_handler.engine else '❌ Disabled'}
• Translation: {'✅ Available' if self.translation_service.is_initialized() else '❌ Disabled'}
"""
        
        self.console.print(Panel(status_info, title="Status", border_style="blue"))
    
    def process_message(self, message):
        """Process and respond to user message"""
        if not message or message in ["clear", "language_changed", "translation_done", "voice_failed", "model_changed", "status_shown"]:
            return
        
        if not self.validated_models['groq']['valid']:
            self.console.print("❌ Cannot process message: Groq API key is invalid", style="red")
            return
        
        current_model = getattr(self.chat_engine, 'current_model', 'Unknown')
        with self.console.status(f"[bold green]Thinking with {current_model}...", spinner="dots"):
            try:
                ai_response = self.chat_engine.send_message(message)
                
                if self.current_language == 'hi':
                    try:
                        translated_response = self.translation_service.translate_text(ai_response, 'hi')
                        ai_response = translated_response
                    except Exception as e:
                        self.console.print(f"❌ Translation failed: {e}", style="red")
                
            except Exception as e:
                self.console.print(f"❌ AI Error: {e}", style="red")
                return
        
        self.console.print(
            Panel(
                ai_response,
                title=f"🤖 AI Response ({current_model})",
                border_style="green",
                box=box.ROUNDED
            )
        )
        
        use_voice = Confirm.ask("🎙️ Speak response?")
        if use_voice:
            self.voice_handler.text_to_speech(ai_response, self.current_language)
    
    def run(self):
        """Main chatbot loop"""
        self.display_welcome()
        
        if self.validated_models['groq']['valid']:
            selected_model = self.get_available_models()
            self.chat_engine.set_model(selected_model)
        
        while self.is_running:
            try:
                self.show_status()
                user_input = self.get_user_input()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['voice', 'translate', 'clear', 'language', 'model', 'status', 'quit', 'exit']:
                    result = self.handle_command(user_input)
                    if result and result not in ["clear", "language_changed", "translation_done", "voice_failed", "model_changed", "status_shown"]:
                        self.process_message(result)
                else:
                    self.process_message(user_input)
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="bold red")
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="bold red")
                continue
    
    def cleanup(self):
        """Cleanup resources"""
        self.voice_handler.stop_speaking()
        self.console.print("✅ Chatbot shutdown complete", style="green")

def main():
    """Main function"""
    try:
        chatbot = ChatBot()
        chatbot.run()
    except Exception as e:
        console = Console()
        console.print(f"❌ Fatal error: {e}", style="bold red")
    finally:
        if 'chatbot' in locals():
            chatbot.cleanup()

if __name__ == "__main__":
    main()