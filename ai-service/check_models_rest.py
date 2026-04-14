import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"Requesting models list from: {url.replace(api_key, 'REDACTED')}")
try:
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"Found {len(models)} models:")
        for m in models:
            name = m.get('name', '')
            methods = m.get('supportedGenerationMethods', [])
            if 'generateContent' in methods:
                print(f"- {name}")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
