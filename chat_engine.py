from groq import Groq
from config import Config

class ChatEngine:
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.initialize_chat()
    
    def initialize_chat(self):
        """Initialize Groq client"""
        try:
            if Config.GROQ_API_KEY:
                self.client = Groq(api_key=Config.GROQ_API_KEY)
                print("✅ Chat engine initialized successfully")
                
                # System message to set context
                system_message = {
                    "role": "system",
                    "content": "You are a helpful AI assistant. You can communicate in both English and Hindi. Provide clear, concise responses."
                }
                self.conversation_history.append(system_message)
                
            else:
                print("❌ Groq API key not found")
        except Exception as e:
            print(f"❌ Error initializing chat engine: {e}")
    
    def send_message(self, message, use_history=True):
        """Send message to AI and get response"""
        if not self.client:
            return "❌ Chat engine not available. Please check your API key."
        
        try:
            # Add user message to history
            user_message = {"role": "user", "content": message}
            
            if use_history:
                messages = self.conversation_history + [user_message]
            else:
                messages = [user_message]
            
            # Get response from Groq
            response = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            
            # Add to conversation history
            if use_history:
                self.conversation_history.append(user_message)
                self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            error_msg = f"❌ Error communicating with AI: {str(e)}"
            print(error_msg)
            return error_msg
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant. You can communicate in both English and Hindi."
            }
        ]
        print("✅ Conversation history cleared")
    
    def get_history_summary(self):
        """Get summary of conversation history"""
        return f"Conversation has {len(self.conversation_history) - 1} messages"