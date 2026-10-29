"""
Configuration de l'application OCR & Extraction Factures.
Définit les paramètres du modèle local Ollama et les chemins Tesseract.
"""

import os
import shutil

# --- Configuration Ollama (LLM Local) ---
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")  # Recommandé : qwen2.5:3b ou llama3.2:3b
NUM_CTX = 2048  # Optimisé pour CPU : 2x plus rapide à charger et à inférer (KV cache divisé par 2)
KEEP_ALIVE = "0"  # Déchargement IMMÉDIAT du modèle de la RAM dès la fin de l'inférence

# --- Configuration Tesseract OCR ---
# Chemins Windows fréquents où Tesseract est généralement installé
POSSIBLE_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
]

def find_tesseract_path() -> str | None:
    """Cherche l'exécutable tesseract dans le PATH ou dans les répertoires standards Windows."""
    # 1. Vérifier si présent dans le PATH système
    path_in_env = shutil.which("tesseract")
    if path_in_env:
        return path_in_env
    
    # 2. Vérifier les répertoires d'installation Windows standards
    for path in POSSIBLE_TESSERACT_PATHS:
        if os.path.isfile(path):
            return path
            
    return None
