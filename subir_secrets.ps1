# Sube credentials.json y token.json al repo como secrets de GitHub Actions.
#
# Requisitos:
#   - gh CLI instalado (https://cli.github.com) y autenticado (gh auth login).
#   - credentials.json y token.json en esta misma carpeta.
#
# Uso:
#   .\subir_secrets.ps1
#   .\subir_secrets.ps1 -Repo "usuario/repo"   # si querés forzar otro repo
#
# Si gh CLI no detecta el repo solo, pasalo con -Repo.

[CmdletBinding()]
param(
    [string]$Repo = ""
)

$ErrorActionPreference = "Stop"

function Fail($msg) {
    Write-Host "ERROR: $msg" -ForegroundColor Red
    exit 1
}

# 1) gh CLI?
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Fail "No encuentro 'gh' (GitHub CLI). Instalalo desde https://cli.github.com y corré 'gh auth login'."
}

# 2) Autenticado?
& gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Fail "gh CLI no está autenticado. Corré 'gh auth login' primero."
}

# 3) Archivos presentes?
$creds = Join-Path $PSScriptRoot "credentials.json"
$token = Join-Path $PSScriptRoot "token.json"
if (-not (Test-Path $creds)) { Fail "No encuentro 'credentials.json' en $PSScriptRoot" }
if (-not (Test-Path $token)) {
    Fail "No encuentro 'token.json' en $PSScriptRoot. Corré primero: python gmail_organizer.py --dry-run --full"
}

# 4) Base64 (sin saltos de linea).
$credsB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($creds))
$tokenB64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($token))

# 5) Subir secrets.
$repoArg = @()
if ($Repo) { $repoArg = @("--repo", $Repo) }

Write-Host "Subiendo GMAIL_CREDENTIALS_B64..." -ForegroundColor Cyan
$credsB64 | & gh secret set GMAIL_CREDENTIALS_B64 @repoArg --body -
if ($LASTEXITCODE -ne 0) { Fail "Falló gh secret set para GMAIL_CREDENTIALS_B64." }

Write-Host "Subiendo GMAIL_TOKEN_B64..." -ForegroundColor Cyan
$tokenB64 | & gh secret set GMAIL_TOKEN_B64 @repoArg --body -
if ($LASTEXITCODE -ne 0) { Fail "Falló gh secret set para GMAIL_TOKEN_B64." }

Write-Host ""
Write-Host "Listo. Secrets cargados." -ForegroundColor Green
Write-Host "Ahora andá a Actions -> 'Organizar Gmail diario' -> 'Run workflow' y probalo con label_only=true." -ForegroundColor Green
