#!/usr/bin/env bash
# Bojnalay — one-command setup & launch
# Works from any folder: it finds its own directory first.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "🍲 Bojnalay — Smart Thali Planner (Jaunpur, Uttar Pradesh)"
echo "-----------------------------------------------------------"

# 1. Virtual environment
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Dependencies
echo "⬇️  Installing Flask..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

# 3. Database + sample data (only when empty)
if [ ! -f database/bojnalay.db ]; then
  echo "🌱 Seeding recipes and sample weekly thali..."
  python seed_recipes.py
fi

echo ""
echo "✅ Ready! Open http://127.0.0.1:5000 in your browser."
echo "   (Press Ctrl+C to stop the server.)"
echo ""
exec python app.py
