#!/usr/bin/env bash
# Render a .docx to PDF next to it (LibreOffice; needs the libreoffice-math package for the equations).
set -euo pipefail
for f in "$@"; do (cd "$(dirname "$f")" && soffice --headless --convert-to pdf "$(basename "$f")" >/dev/null 2>&1 && echo "$(dirname "$f")/$(basename "${f%.docx}").pdf"); done
