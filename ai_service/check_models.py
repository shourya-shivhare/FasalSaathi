import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
llm = ChatGoogleGenerativeAI(model=model_name)
print(f"Testing {model_name}...")
try:
    res = llm.invoke("Hi")
    print(f"Success: {res.content}")
except Exception as e:
    print(f"Error with {model_name}: {e}")
