# Fourtriangle

Fourtriangle est une application web développée pour le cours de info-h-303 à l'ULB.

Cette application sert d'annuaire d'établissement horeca : des bars, des restaurants et des hotels.

# Installation

Dépendances : `python3`, `postgresql`

    cd flask/
    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt
    cd datas
    createdb horeca
    python loadxml.py


# Configuration et démarrage

    Editez `flask/local_config.py` pour écraser les valeurs par défaut spécifiées dans `flask/config.py`

    cd flask/
    python app.py
