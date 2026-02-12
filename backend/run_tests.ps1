# run_tests.ps1
# Script de PowerShell para ejecutar tests de forma fácil

param(
    [string]$Type = "all",
    [switch]$Coverage,
    [switch]$Verbose,
    [switch]$StopOnFail
)

Write-Host "🧪 GoalApp - Test Runner" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio backend
Set-Location -Path $PSScriptRoot

# Verificar que pytest esté instalado
try {
    $null = Get-Command pytest -ErrorAction Stop
} catch {
    Write-Host "❌ pytest no está instalado" -ForegroundColor Red
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Construir comando pytest
$pytestCmd = "pytest"

# Añadir tipo de test
switch ($Type) {
    "unit" {
        Write-Host "📊 Ejecutando tests unitarios..." -ForegroundColor Green
        $pytestCmd += " tests/unit/"
    }
    "integration" {
        Write-Host "🔗 Ejecutando tests de integración..." -ForegroundColor Green
        $pytestCmd += " tests/integration/"
    }
    "auth" {
        Write-Host "🔐 Ejecutando tests de autenticación..." -ForegroundColor Green
        $pytestCmd += " tests/integration/test_auth.py"
    }
    default {
        Write-Host "🎯 Ejecutando todos los tests..." -ForegroundColor Green
    }
}

# Añadir opciones
if ($Verbose) {
    $pytestCmd += " -v"
}

if ($StopOnFail) {
    $pytestCmd += " -x"
}

if ($Coverage) {
    Write-Host "📈 Con cobertura de código..." -ForegroundColor Yellow
    $pytestCmd += " --cov=app --cov-report=html --cov-report=term"
}

Write-Host ""
Write-Host "Ejecutando: $pytestCmd" -ForegroundColor Gray
Write-Host ""

# Ejecutar tests
Invoke-Expression $pytestCmd

# Mostrar mensaje de cobertura si aplica
if ($Coverage -and $LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Reporte de cobertura generado en: htmlcov/index.html" -ForegroundColor Green
    Write-Host "Para ver el reporte: start htmlcov/index.html" -ForegroundColor Cyan
}

# Salir con el código de pytest
exit $LASTEXITCODE
