#!/bin/bash

echo "Inicializuji projekt druhej-plan-processor..."

# vytvoření datových složek
mkdir -p data/input
mkdir -p data/output

# vytvoření .gitkeep pro zachování složek v repozitáři
touch data/input/.gitkeep
touch data/output/.gitkeep

# inicializace gitu (pokud ještě neexistuje)
if [ ! -d ".git" ]; then
    git init
    echo "Git repozitář inicializován."
fi

# nastavení python virtual environmentu
echo "Vytvářím virtuální prostředí (venv)..."
python3 -m venv venv

# aktivace a instalace závislostí
source venv/bin/activate
echo "Instaluji závislosti z requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Projekt je připraven. Vlož hlavní skript 'rehearsal_processor.py' do rootu."