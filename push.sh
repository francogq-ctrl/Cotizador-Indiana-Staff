#!/bin/sh
# Deploy index.html → GitHub Pages (Cotizador-Indiana-Staff)
set -e
cd "$(dirname "$0")"
git add index.html
if git diff --cached --quiet; then
  echo "Sin cambios en index.html."
  exit 0
fi
git commit -m "${1:-Update cotizador}"
git push origin main
echo "Live: https://francogq-ctrl.github.io/Cotizador-Indiana-Staff/"
