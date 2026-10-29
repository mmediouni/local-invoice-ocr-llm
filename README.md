# 🧾 Scanner Léger de Factures & Tickets (100% Local, CPU, < 4 Go RAM)

Application locale, gratuite et respectueuse de la vie privée permettant de numériser des factures et tickets de caisse, d'en extraire le texte par OCR léger, puis de structurer les données en JSON propre via un LLM local 3B (Ollama).

---

## 🚀 Fonctionnalités Clés

- **100% Gratuit & Hors-ligne :** Aucune API payante, aucune clé secrète requise.
- **Budget RAM garanti (< 3 Go en pic) :** Conçu pour tourner sur une machine avec seulement 4 à 5 Go libres (CPU pur Intel AVX2).
- **Déchargement immédiat de la RAM :** Le modèle d'IA est libéré de la mémoire vive dès la fin de l'analyse (`keep_alive: 0`).
- **Stockage 100% sur Disque D: :** Ollama, le cache et les modèles d'IA sont installés et stockés sur le disque D: (préservation totale du disque C:).
- **Double Moteur OCR Léger :** 
  - **RapidOCR (ONNX CPU) :** Moteur haute précision préconfiguré, ne nécessite aucune installation externe.
  - **Tesseract OCR :** Compatible si déjà installé sur le système.
- **Support Images & PDF :** Accepte les images (`.png`, `.jpg`, `.jpeg`, `.webp`) ainsi que les factures numériques ou scannées en `.pdf`.
- **Validation Arithmétique Comptable :** Détection automatique des écarts (`Total HT + TVA == Total TTC` et somme des lignes d'articles).
- **Interface Web Moderne (Streamlit) :** Prévisualisation du document, rapport de cohérence comptable, tableau interactif des articles et exports JSON & CSV.
- **Bouton de test 1-clic :** Ticket d'exemple intégré pour tester instantanément l'application.

---

## 🛠️ Installation & Démarrage Rapide

### Méthode Automatique (Recommandée - 1 Clic)

1. **Installer les dépendances Python :**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Installer Ollama et le modèle IA sur le disque D: :**
   Double-cliquez simplement sur :
   👉 **`installer_ollama_et_modele.bat`**
   
   *Ce script s'occupe de tout : création des dossiers sur D:, jonction Windows pour protéger C:, téléchargement d'Ollama, configuration du mode CPU pur et téléchargement automatique du modèle `qwen2.5:3b`.*

---

## 🖥️ Lancement de l'Application

Double-cliquez simplement sur :
👉 **`lancer_application.bat`**

*(Ou en ligne de commande : `python -m streamlit run app.py`)*.

L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`.

---

## 📊 Répartition de la Consommation RAM

| Composant | Rôle | Consommation RAM | Libération |
|---|---|---|---|
| **Prétraitement Pillow** | Réduction 1800px, contraste thermique | ~40 Mo | Immédiate (`gc.collect`) |
| **OCR Léger (RapidOCR / Tesseract)** | Extraction du texte brut (CPU) | ~80 Mo (crête) | Libérée après extraction |
| **Ollama (`qwen2.5:3b` Q4)** | Structuration JSON + Compréhension | ~1.8 - 2.0 Go (crête) | **Immédiate** dès la réponse (`keep_alive: 0`) |
| **Interface Streamlit** | Interface Web & tableaux | ~100 Mo | Résident |
| **TOTAL CRÊTE (Analyse en cours)** | | **~2.0 à 2.2 Go** | Largement dans votre budget (4-5 Go max) |
| **TOTAL AU REPOS (Entre deux factures)**| | **~100 Mo** | Vos autres applications disposent de toute la RAM |

---

## 📁 Architecture du Code

- `installer_ollama_et_modele.bat` : Installateur 1-clic Windows d'Ollama et du modèle sur le disque D:.
- `installer_ollama.ps1` : Script PowerShell d'automatisation de l'installation et des redirections de disques.
- `lancer_application.bat` : Lanceur 1-clic avec vérification et démarrage automatique d'Ollama en mode CPU.
- `demarrer_ollama.bat` : Lanceur manuel d'Ollama configuré en 100% CPU sur D:.
- `config.py` : Paramètres d'inférence (contexte 2048, 4 threads, chemins).
- `ocr_engine.py` : Moteur hybride RapidOCR (ONNX) + Tesseract + extracteur direct PDF.
- `extractor.py` : Client Ollama avec prompt système strict, mode JSON et `keep_alive: 0`.
- `validator.py` : Contrôle mathématique, tolérances d'arrondi et détection d'erreurs.
- `app.py` : Interface utilisateur Streamlit avec diagnostic matériel et exports.
- `generate_sample_receipt.py` : Générateur de ticket de test (`sample_ticket.png`).
