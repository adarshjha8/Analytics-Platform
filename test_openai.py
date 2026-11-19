
import os
from google import genai
from google.genai import errors

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not configured")

client = genai.Client(api_key=api_key)

models = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]

for model in models:
    try:
        print(f"Trying model: {model}")

        response = client.models.generate_content(
            model=model,
            contents="Explain a Python ETL pipeline in two sentences."
        )

        print("\nGEMINI API CONNECTION SUCCESSFUL!")
        print("Model:", model)
        print(response.text)
        break

    except errors.APIError as e:
        print(f"{model} failed: {e.code} - {e.message}")
    except Exception as e:
        print("Error:", e)
else:
    print("\nAll models are currently unavailable.")
