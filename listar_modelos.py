"""
Script para listar los modelos disponibles en Google Gemini
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

# Configurar API de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Error: No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=GEMINI_API_KEY)

# Listar modelos disponibles
print("📋 Modelos disponibles en Google Gemini API:\n")
try:
    for model in genai.list_models():
        print(f"• {model.name}")
        print(f"  Métodos soportados: {[m for m in dir(model) if not m.startswith('_')]}")
        print()
except Exception as e:
    print(f"Error al listar modelos: {e}")
