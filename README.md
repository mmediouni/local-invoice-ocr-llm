# 🧾 Scanner Léger de Factures & Tickets (100% Local, CPU, < 4 Go RAM)

Application locale, gratuite et respectueuse de la vie privée permettant de numériser des factures et tickets de caisse, d'en extraire le texte par OCR léger, puis de structurer les données en JSON propre via un LLM local 3B (Ollama).

---

## 🚀 Fonctionnalités Clés

- **100% Gratuit & Hors-ligne :** Aucune API payante, aucune clé secrète requise.
- **Budget RAM garanti (< 3 Go en pic) :** Conçu spécifiquement pour tourner sur une machine de 12 Go avec seulement 4 à 5 Go libres.
- **Déchargement immédiat de la RAM :** Le modèle d'IA est éjecté de la mémoire vive dès la fin de l'analyse (`keep_alive: 0`).
- **Double Moteur OCR Léger :** 
  - **RapidOCR (ONNX CPU) :** Moteur haute précision préconfiguré, ne nécessite aucune installation externe ni droits d'administrateur.
  - **Tesseract OCR :** Compatible si déjà installé sur le système.
- **Support Images & PDF :** Accepte les images (`.png`, `.jpg`, `.jpeg`, `.webp`) ainsi que les factures numériques ou scannées en `.pdf`.
- **Validation Arithmétique Comptable :** Détection automatique des écarts (`Total HT + TVA == Total TTC` et somme des lignes d'articles).
- **Interface Web Moderne (Streamlit) :** Prévisualisation de l'image, rapport de validation en direct, tableau interactif des articles et exports JSON & CSV.
- **Bouton de test 1-clic :** Ticket d'exemple intégré pour tester instantanément l'application.

---

## 🛠️ Installation & Démarrage Rapide

### 1. Installer Ollama et télécharger le modèle 3B
1. Installez Ollama :
```powershell
winget install Ollama.Ollama
```
2. Téléchargez le modèle Qwen 2.5 3B (recommandé pour les factures en français) :
```powershell
ollama pull qwen2.5:3b
```

### 2. Installer les dépendances Python
Dans le dossier du projet :
```powershell
pip install -r requirements.txt
```

---

## 🖥️ Lancement de l'Application

Vous avez deux façons très simples de lancer l'application :

### Méthode 1 : Double-clic
Double-cliquez simplement sur le fichier **[`lancer_application.bat`](file:///d:/Dev/py/ocr-1/lancer_application.bat)**.

### Méthode 2 : Ligne de commande
```powershell
python -m streamlit run app.py
```
L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`.

---

## 📊 Répartition de la Consommation RAM

| Composant | Rôle | Consommation RAM | Libération |
|---|---|---|---|
| **Prétraitement Pillow** | Réduction 1800px, contraste thermique | ~40 Mo | Immédiate (`gc.collect`) |
| **OCR Léger (RapidOCR / Tesseract)** | Extraction du texte brut (CPU) | ~80 Mo (crête) | Libérée après extraction |
| **Ollama (`qwen2.5:3b` Q4)** | Structuration JSON + Compréhension | ~2.0 - 2.4 Go (crête) | **Immédiate** dès la réponse (`keep_alive: 0`) |
| **Interface Streamlit** | Interface Web & tableaux | ~100 Mo | Résident |
| **TOTAL CRÊTE (Analyse en cours)** | | **~2.5 à 2.7 Go** | Largement dans votre budget (4-5 Go max) |
| **TOTAL AU REPOS (Entre deux factures)**| | **~100 Mo** | Vos autres applications disposent de toute la RAM |

---

## 📁 Architecture du Code

- [`config.py`](file:///d:/Dev/py/ocr-1/config.py) : Détection automatique des exécutables et paramètres Ollama.
- [`ocr_engine.py`](file:///d:/Dev/py/ocr-1/ocr_engine.py) : Moteur hybride RapidOCR (ONNX) + Tesseract + extracteur direct PDF.
- [`extractor.py`](file:///d:/Dev/py/ocr-1/extractor.py) : Client Ollama avec prompt système strict, mode JSON et `keep_alive: 0`.
- [`validator.py`](file:///d:/Dev/py/ocr-1/validator.py) : Contrôle mathématique, tolérances d'arrondi et détection d'erreurs.
- [`app.py`](file:///d:/Dev/py/ocr-1/app.py) : Interface utilisateur Streamlit avec diagnostic matériel et exports.
- [`generate_sample_receipt.py`](file:///d:/Dev/py/ocr-1/generate_sample_receipt.py) : Générateur de ticket de test (`sample_ticket.png`).
- [`lancer_application.bat`](file:///d:/Dev/py/ocr-1/lancer_application.bat) : Lanceur rapide Windows.
