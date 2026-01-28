# Script de démarrage rapide pour Callbot Julie
# Usage: .\setup.ps1

Write-Host "🤖 CALLBOT JULIE - CNP ASSURANCES" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
Write-Host "📋 Vérification de Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python n'est pas installé!" -ForegroundColor Red
    exit 1
}

# Créer l'environnement virtuel
Write-Host ""
Write-Host "📦 Création de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  L'environnement virtuel existe déjà" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Environnement virtuel créé" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host ""
Write-Host "🔌 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Installer les dépendances
Write-Host ""
Write-Host "📚 Installation des dépendances..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dépendances installées" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de l'installation" -ForegroundColor Red
    exit 1
}

# Vérifier le fichier .env
Write-Host ""
Write-Host "🔐 Vérification de la configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Fichier .env trouvé" -ForegroundColor Green
} else {
    Write-Host "⚠️  Fichier .env non trouvé" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "📝 Fichier .env créé depuis .env.example" -ForegroundColor Green
        Write-Host "⚠️  N'oubliez pas d'ajouter votre clé API OpenAI!" -ForegroundColor Yellow
    }
}

# Résumé
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✅ Installation terminée!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Éditez le fichier .env et ajoutez votre OPENAI_API_KEY" -ForegroundColor White
Write-Host "   2. Testez avec: python src/main.py" -ForegroundColor White
Write-Host "   3. Lancez l'API: python src/api.py" -ForegroundColor White
Write-Host "   4. Exécutez les tests: pytest tests/" -ForegroundColor White
Write-Host ""
