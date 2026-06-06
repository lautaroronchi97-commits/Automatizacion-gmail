#!/usr/bin/env bash
# Sube credentials.json y token.json al repo como secrets de GitHub Actions.
#
# Requisitos:
#   - gh CLI instalado (https://cli.github.com) y autenticado (gh auth login).
#   - credentials.json y token.json en esta misma carpeta.
#
# Uso:
#   ./subir_secrets.sh
#   ./subir_secrets.sh usuario/repo   # opcional: forzar otro repo

set -euo pipefail

REPO="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

fail() { echo "ERROR: $*" >&2; exit 1; }

command -v gh >/dev/null 2>&1 || fail "Falta 'gh' (GitHub CLI). https://cli.github.com"
gh auth status >/dev/null 2>&1 || fail "gh CLI no autenticado. Corré 'gh auth login'."

[ -f "$HERE/credentials.json" ] || fail "No encuentro $HERE/credentials.json"
[ -f "$HERE/token.json" ] || fail "No encuentro $HERE/token.json. Corré primero: python gmail_organizer.py --dry-run --full"

CREDS_B64=$(base64 -w0 < "$HERE/credentials.json" 2>/dev/null || base64 < "$HERE/credentials.json" | tr -d '\n')
TOKEN_B64=$(base64 -w0 < "$HERE/token.json" 2>/dev/null || base64 < "$HERE/token.json" | tr -d '\n')

REPO_ARG=()
[ -n "$REPO" ] && REPO_ARG=(--repo "$REPO")

echo "Subiendo GMAIL_CREDENTIALS_B64..."
printf '%s' "$CREDS_B64" | gh secret set GMAIL_CREDENTIALS_B64 "${REPO_ARG[@]}" --body -

echo "Subiendo GMAIL_TOKEN_B64..."
printf '%s' "$TOKEN_B64" | gh secret set GMAIL_TOKEN_B64 "${REPO_ARG[@]}" --body -

echo
echo "Listo. Secrets cargados."
echo "Ahora andá a Actions -> 'Organizar Gmail diario' -> 'Run workflow' y probalo con label_only=true."
