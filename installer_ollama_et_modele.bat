@echo off
title Installation Automatique Ollama + Modele IA (Disque D:)
chcp 65001 > nul
echo ======================================================================
echo   Installateur 1-Clic : Ollama + Modèle Qwen 2.5 3B (Disque D:)
echo ======================================================================
echo.
echo Ce script va :
echo  1. Créer les répertoires et la jonction sur le disque D:
echo  2. Configurer le mode 100%% CPU et interdire toute écriture sur C:
echo  3. Télécharger et installer la dernière version d'Ollama
echo  4. Télécharger le modèle IA qwen2.5:3b (1.9 Go) sur D:\Ollama\models
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer_ollama.ps1"
echo.
pause
