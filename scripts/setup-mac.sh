#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "  VIDA EN ORDEN — Setup local para macOS"
echo "=========================================="

# 1. Verificar Homebrew
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew no está instalado. Instálalo primero desde https://brew.sh"
  exit 1
fi

# 2. Dependencias base para Webapp + Máquina de Carruseles/Reels
echo "→ Verificando Node.js, FFmpeg y Poppler..."
command -v node >/dev/null 2>&1 || brew install node
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
command -v pdftotext >/dev/null 2>&1 || brew install poppler

# 3. Instalar dependencias de Node si existe package.json en marketing
if [ -f "marketing/package.json" ]; then
  echo "→ Instalando dependencias de la Máquina de Marketing..."
  (cd marketing && npm install)
fi

echo ""
echo "Listo. Para abrir el proyecto localmente:"
echo "  npx serve -l 4173 ."
echo "  - Test V.I.D.A.:  http://localhost:4173/producto/webapp/"
echo "  - Mesa de Juntas: http://localhost:4173/mesa-de-juntas/panel-movil/"
