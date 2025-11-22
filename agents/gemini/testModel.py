import google.genai as genai
import os # We import 'os' just in case we still want to pull it from the environment
from common.common import instruction_prompt as common_instruction_prompt
# Get the API key from the environment variable, or hardcode it if necessary for debugging.
# Make sure to replace "YOUR_ACTUAL_API_KEY" with your key string.
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# =============================
# CONFIGURATION
# =============================  # Change this to your folder
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
if not GEMINI_API_KEY:
    raise SystemExit("Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env or environment.")

# Pass the API key to the client constructor directly.
client = genai.Client(api_key=api_key)

import google.genai as genai
from google.genai import types # Import the types module
import os
import re

def invoke_gemini_api(input_query: str) -> str:
   
    client = genai.Client(api_key=api_key)

    # Define your system instruction string
    instruction_prompt = common_instruction_prompt

    # Call generate_content and pass the config with the system_instruction
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=input_query,
        config=types.GenerateContentConfig( # Use the config parameter
            system_instruction=instruction_prompt,
        ),
    )
    return response.text


input_query = """ 
        Let z = cos θ + isin θ. Then the value of
    15
    X
    m=1
    Im(z
    2m−1
    ) at θ = 2◦
    is
    (A) 1
    sin 2◦
    (B) 1
    3 sin 2◦
    (C) 1
    2 sin 2◦
    (D) 1
    4 sin 2◦
    """
print(invoke_gemini_api(input_query))