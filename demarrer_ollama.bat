@echo off
title Serveur Ollama (Mode CPU Pur - Disque D:)
chcp 65001 > nul
set "OLLAMA_MODELS=D:\Ollama\models"
set "OLLAMA_HOST=127.0.0.1:11434"
:: Désactiver CUDA et Vulkan pour forcer 100% CPU Intel AVX2 (très rapide et 0 plantage de carte graphique)
set "CUDA_VISIBLE_DEVICES="
set "OLLAMA_VULKAN=0"
echo [INFO] Démarrage d'Ollama en mode CPU Pur sur D:\Ollama\models ...
"D:\Ollama\ollama.exe" serve
