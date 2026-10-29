"""
Module d'extraction structurée via Ollama (LLM local).
Applique un prompt système strict, impose le format JSON et décharge immédiatement
le modèle de la RAM après l'inférence via 'keep_alive: 0'.
"""

import json
import re
import requests
from config import OLLAMA_API_URL, DEFAULT_MODEL, NUM_CTX, KEEP_ALIVE

SYSTEM_PROMPT = """Tu es un expert comptable en extraction de données de tickets de caisse et factures.
Analyse le texte brut issu d'un OCR et convertis-le en un document JSON strictement conforme au schéma ci-dessous.

SCHÉMA JSON REQUIS :
{
  "emetteur": "Nom ou enseigne de l'émetteur (string ou null)",
  "date": "Date au format YYYY-MM-DD si possible, sinon telle quelle (string ou null)",
  "numero_facture": "Numéro de facture ou ticket de caisse (string ou null)",
  "lignes": [
    {
      "description": "Désignation de l'article (string)",
      "quantite": 1.0,
      "prix_unitaire": 0.0,
      "total_ligne": 0.0
    }
  ],
  "total_ht": 0.0,
  "montant_tva": 0.0,
  "taux_tva_pourcent": 0.0,
  "total_ttc": 0.0,
  "devise": "EUR"
}

RÈGLES STRICTES :
1. Tous les montants numériques doivent être des nombres flottants (ex: 14.99). Convertis les virgules françaises ',' en points décimaux '.'.
2. Pour chaque ligne d'article : si la quantité est absente, fixe quantite = 1.0. Si le prix unitaire est absent, fixe-le égal à total_ligne.
3. Si le texte ne contient que le Total TTC et la TVA, calcule ou déduis le total_ht (total_ht = total_ttc - montant_tva).
4. Ne jamais inventer d'articles : si les lignes individuelles sont illisibles, renvoie une liste vide [].
5. N'ajoute AUCUN commentaire, AUCUN markdown (pas de ```json), AUCUNE phrase d'introduction ou de conclusion. Renvoie STRICTEMENT l'objet JSON valide."""


def check_ollama_status() -> tuple[bool, str]:
    """Vérifie si le serveur Ollama est démarré et joignable."""
    try:
        resp = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=3)
        if resp.status_code == 200:
            models = [m.get("name") for m in resp.json().get("models", [])]
            return True, f"Ollama actif. Modèles disponibles : {', '.join(models) if models else 'Aucun modèle téléchargé'}"
        return False, f"Ollama répond avec le code {resp.status_code}"
    except requests.exceptions.RequestException:
        return False, f"Impossible de contacter Ollama sur {OLLAMA_API_URL}. Lancez 'ollama serve' dans un terminal."


def extract_invoice_data(ocr_text: str, model_name: str = DEFAULT_MODEL) -> dict:
    """
    Envoie le texte OCR au modèle local Ollama pour extraction en JSON.
    Garantit la libération de la RAM en passant 'keep_alive: 0'.
    """
    if not ocr_text or not ocr_text.strip():
        return {
            "error": "Texte OCR vide",
            "emetteur": None,
            "date": None,
            "numero_facture": None,
            "lignes": [],
            "total_ht": 0.0,
            "montant_tva": 0.0,
            "taux_tva_pourcent": 0.0,
            "total_ttc": 0.0,
            "devise": "EUR"
        }

    user_prompt = f"Voici le texte brut extrait par OCR d'une facture ou d'un ticket de caisse :\n---\n{ocr_text}\n---\nExtrais les informations sous forme de JSON strict."

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "format": "json",  # Force Ollama à générer une structure JSON conforme
        "keep_alive": KEEP_ALIVE,  # "0" -> décharge le modèle de la RAM immédiatement après l'inférence
        "options": {
            "temperature": 0.1,  # Faible température pour éviter les hallucinations
            "num_ctx": NUM_CTX,  # 2048 tokens pour aller 2x plus vite sur CPU
            "num_thread": 4      # 4 cœurs physiques pour performance optimale
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/chat",
            json=payload,
            timeout=240  # Laisse le temps au CPU de calculer sereinement lors du 1er chargement
        )
        response.raise_for_status()
        result = response.json()
        content = result.get("message", {}).get("content", "").strip()

        # Nettoyage préventif au cas où le LLM entourerait de balises markdown
        cleaned_content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
        cleaned_content = re.sub(r"\s*```$", "", cleaned_content, flags=re.MULTILINE).strip()

        parsed_json = json.loads(cleaned_content)
        return parsed_json

    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de communication avec Ollama : {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Erreur de décodage JSON du modèle : {str(e)}", "raw_content": content if 'content' in locals() else ""}
