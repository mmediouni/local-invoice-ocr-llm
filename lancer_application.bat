@echo off
title Scanner Factures & Tickets Local (IA & OCR)
chcp 65001 > nul
echo ======================================================================
echo   Démarrage du Scanner de Factures et Tickets de Caisse (100%% Local)
echo ======================================================================
echo.

:: 1. Configuration des chemins et désactivation GPU (Mode CPU Pur)
set "PATH=%PATH%;D:\Ollama"
set "OLLAMA_MODELS=D:\Ollama\models"
set "CUDA_VISIBLE_DEVICES="
set "OLLAMA_VULKAN=0"

:: 2. Vérification du serveur Ollama
curl -s http://localhost:11434/api/tags > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "D:\Ollama\ollama.exe" (
        echo [INFO] Démarrage du serveur Ollama en mode CPU Pur sur D:\Ollama...
        start "" /B "D:\Ollama\ollama.exe" serve
        timeout /t 3 /nobreak > nul
    ) else (
        echo [AVERTISSEMENT] Ollama n'est pas encore démarré.
    )
)

:: 3. Lancement de l'interface Web Streamlit
echo [INFO] Lancement de l'application Streamlit...
python -m streamlit run app.py
pause
