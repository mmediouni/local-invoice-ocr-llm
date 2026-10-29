# Script d'installation automatisée d'Ollama et du modèle IA sur le disque D:
$ErrorActionPreference = "Stop"

$installDir = "D:\Ollama"
$modelsDir = "$installDir\models"
$dotOllamaDir = "$installDir\dot_ollama"
$zipPath = "$installDir\ollama.zip"
$ollamaExe = "$installDir\ollama.exe"
$modelName = "qwen2.5:3b"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Installation Automatique d'Ollama et du Modèle IA sur le Disque D:  " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Création des répertoires sur D:
Write-Host "[1/6] Création des dossiers sur le disque D:..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
New-Item -ItemType Directory -Path $dotOllamaDir -Force | Out-Null
Write-Host "  -> Dossiers $modelsDir et $dotOllamaDir prêts." -ForegroundColor Green

# 2. Jonction invisible C:\Users\<user>\.ollama -> D:\Ollama\dot_ollama
$userProfileOllama = "$env:USERPROFILE\.ollama"
if (-not (Test-Path $userProfileOllama)) {
    Write-Host "[2/6] Création de la jonction pour protéger le disque C:..." -ForegroundColor Yellow
    cmd /c mklink /J "$userProfileOllama" "$dotOllamaDir" | Out-Null
    Write-Host "  -> Jonction créée : 0 octet ne sera consommé sur C:." -ForegroundColor Green
} else {
    Write-Host "[2/6] Jonction .ollama déjà existante." -ForegroundColor Green
}

# 3. Configuration des variables d'environnement (CPU pur + Stockage D:)
Write-Host "[3/6] Configuration des variables Windows (Mode CPU + Stockage D:)..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', $modelsDir, 'User')
[System.Environment]::SetEnvironmentVariable('CUDA_VISIBLE_DEVICES', '-1', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_VULKAN', '0', 'User')

$env:OLLAMA_MODELS = $modelsDir
$env:CUDA_VISIBLE_DEVICES = "-1"
$env:OLLAMA_VULKAN = "0"
$env:OLLAMA_HOST = "127.0.0.1:11434"
Write-Host "  -> Variables OLLAMA_MODELS, CUDA_VISIBLE_DEVICES=-1 et OLLAMA_VULKAN=0 configurées." -ForegroundColor Green

# 4. Téléchargement et extraction d'Ollama si pas encore présent
if (-not (Test-Path $ollamaExe)) {
    Write-Host "[4/6] Téléchargement officiel d'Ollama (version Windows portable)..." -ForegroundColor Yellow
    $downloadUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
    curl.exe -L $downloadUrl -o $zipPath

    Write-Host "  -> Extraction dans $installDir..." -ForegroundColor Yellow
    Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
    Remove-Item -Path $zipPath -Force
    Write-Host "  -> Ollama installé avec succès dans $installDir." -ForegroundColor Green
} else {
    Write-Host "[4/6] Ollama est déjà installé dans $installDir." -ForegroundColor Green
}

# Ajout au PATH
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$installDir*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
    Write-Host "  -> $installDir ajouté au PATH utilisateur." -ForegroundColor Green
}

# 5. Démarrage du serveur Ollama si non actif
Write-Host "[5/6] Démarrage du serveur Ollama en mode CPU pur..." -ForegroundColor Yellow
$serverRunning = $false
try {
    $resp = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $serverRunning = $true
} catch {}

if (-not $serverRunning) {
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "  -> Serveur Ollama démarré et à l'écoute sur http://127.0.0.1:11434." -ForegroundColor Green
} else {
    Write-Host "  -> Le serveur Ollama est déjà actif." -ForegroundColor Green
}

# 6. Téléchargement du modèle IA
Write-Host "[6/6] Téléchargement du modèle IA $modelName vers $modelsDir..." -ForegroundColor Yellow
& $ollamaExe pull $modelName

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  Installation Terminée avec Succès !                                 " -ForegroundColor Green
Write-Host "  Tous les fichiers et modèles sont stockés sur le disque D:.        " -ForegroundColor Green
Write-Host "  Vous pouvez lancer l'application via 'lancer_application.bat'.     " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
