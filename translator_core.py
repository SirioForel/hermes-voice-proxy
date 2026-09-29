import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Inicializar cliente Gemini
# Asume que GEMINI_API_KEY está en el .env
client = genai.Client()

def translate_incoming(text: str, source_lang: str) -> str:
    """Traduce texto técnico desde el idioma de la reunión al español usando Gemini."""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=f"Eres un intérprete experto en soporte IT. Traduce el siguiente texto del {source_lang} al Español de forma natural y rápida. Solo devuelve la traducción, sin explicaciones ni comillas.",
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error de traducción en Gemini: {e}")
        return "..." # Fallback silencioso
