import requests
import json

def check_groq_api_key(api_key):
    """Check if Groq API key is valid"""
    print("🔍 Checking Groq API key...")
    print(f"Key: {api_key[:10]}...{api_key[-4:]}")
    
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Groq API Key: VALID")
            models = response.json().get('data', [])
            print(f"   Available models: {len(models)}")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model['id']}")
            return True
        elif response.status_code == 401:
            print("❌ Groq API Key: INVALID (Unauthorized)")
            return False
        elif response.status_code == 403:
            print("❌ Groq API Key: FORBIDDEN (No permission)")
            return False
        else:
            print(f"❌ Groq API Key: ERROR (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Groq API Key: REQUEST FAILED - {e}")
        return False

def check_google_api_key(api_key):
    """Check if Google API key is valid"""
    print("\n🔍 Checking Google API key...")
    print(f"Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test with Geocoding API (commonly available)
    test_urls = [
        {
            "name": "Geocoding API",
            "url": f"https://maps.googleapis.com/maps/api/geocode/json?address=Google&key={api_key}"
        },
        {
            "name": "Places API", 
            "url": f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input=Google&key={api_key}"
        }
    ]
    
    for test in test_urls:
        print(f"   Testing {test['name']}...")
        
        try:
            response = requests.get(test['url'])
            data = response.json()
            
            if response.status_code == 200:
                if 'error' in data:
                    error = data['error']
                    error_status = error.get('status', 'UNKNOWN_ERROR')
                    error_message = error.get('message', 'No error message')
                    
                    if error_status == 'INVALID_ARGUMENT':
                        print(f"❌ Google API Key: INVALID")
                        print(f"   Error: {error_message}")
                        return False
                    elif error_status == 'PERMISSION_DENIED':
                        print(f"⚠️  Google API Key: Valid but {test['name']} not enabled")
                        print(f"   Message: {error_message}")
                        # Continue testing other APIs
                        continue
                    elif error_status == 'RESOURCE_EXHAUSTED':
                        print(f"⚠️  Google API Key: Valid but quota exceeded")
                        return True
                    else:
                        print(f"⚠️  Google API Key: {error_status} - {error_message}")
                        continue
                else:
                    print(f"✅ Google API Key: VALID ({test['name']} working)")
                    return True
                    
            else:
                print(f"   HTTP {response.status_code}: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Request failed: {e}")
    
    print("❌ Google API Key: INVALID or no APIs enabled")
    return False

def validate_api_key_format(api_key, service):
    """Basic format validation"""
    if service == "google":
        if not api_key.startswith('AIza'):
            return False, "Should start with 'AIza'"
        if len(api_key) != 39:
            return False, f"Length {len(api_key)} (expected 39)"
        return True, "Format OK"
    
    elif service == "groq":
        if not api_key.startswith('gsk_'):
            return False, "Should start with 'gsk_'"
        if len(api_key) < 40:
            return False, f"Length {len(api_key)} (too short)"
        return True, "Format OK"
    
    return False, "Unknown service"

def comprehensive_api_check():
    """Comprehensive check of both API keys"""
    print("🚀 Starting Comprehensive API Key Validation\n")
    
    # Your API keys
    GOOGLE_API_KEY = "AIzaSyAG-qx8FgW8gGzxZpuh9LlgFojsX3d7hmU"
    GROQ_API_KEY = "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"
    
    # Check Groq API Key
    print("=" * 50)
    groq_format_ok, groq_format_msg = validate_api_key_format(GROQ_API_KEY, "groq")
    print(f"Groq API Key Format: {'✅' if groq_format_ok else '❌'} {groq_format_msg}")
    
    if groq_format_ok:
        groq_valid = check_groq_api_key(GROQ_API_KEY)
    else:
        groq_valid = False
    
    # Check Google API Key  
    print("\n" + "=" * 50)
    google_format_ok, google_format_msg = validate_api_key_format(GOOGLE_API_KEY, "google")
    print(f"Google API Key Format: {'✅' if google_format_ok else '❌'} {google_format_msg}")
    
    if google_format_ok:
        google_valid = check_google_api_key(GOOGLE_API_KEY)
    else:
        google_valid = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")
    print(f"Groq API Key:   {'✅ VALID' if groq_valid else '❌ INVALID'}")
    print(f"Google API Key: {'✅ VALID' if google_valid else '❌ INVALID'}")
    
    if groq_valid and google_valid:
        print("\n🎉 Both API keys are working properly!")
    else:
        print("\n🔧 Some API keys need attention:")
        if not groq_valid:
            print("- Check Groq API key at: https://console.groq.com")
        if not google_valid:
            print("- Check Google API key at: https://console.cloud.google.com")

# Run the comprehensive check
if __name__ == "__main__":
    comprehensive_api_check()