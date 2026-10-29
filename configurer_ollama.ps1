# Script d'installation locale et d'extraction d'Ollama sur le disque D:
$zipPath = "D:\Ollama\ollama.zip"
$destPath = "D:\Ollama"

if (Test-Path $zipPath) {
    Write-Output "Extraction d'Ollama dans D:\Ollama..."
    Expand-Archive -Path $zipPath -DestinationPath $destPath -Force
    Remove-Item -Path $zipPath -Force
    Write-Output "Extraction terminée avec succès."
}

# Vérifier que ollama.exe est bien présent
if (Test-Path "$destPath\ollama.exe") {
    Write-Output "Ollama exécutable détecté : $destPath\ollama.exe"
    
    # Ajouter D:\Ollama au PATH utilisateur si pas déjà présent
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*D:\Ollama*") {
        [System.Environment]::SetEnvironmentVariable("Path", "$userPath;D:\Ollama", "User")
        Write-Output "D:\Ollama ajouté au PATH utilisateur."
    }
} else {
    Write-Output "Fichier ollama.exe non trouvé dans $destPath."
}
