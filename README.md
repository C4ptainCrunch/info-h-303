# Fourtriangle

Fourtriangle est une application web développée pour le cours de info-h-303 à l'ULB.

Cette application sert d'annuaire d'établissement horeca : des bars, des restaurants et des hotels.

# Installation

Dépendances : `python3`, `postgresql`

    cd flask/
    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt
    createdb horeca
    psql -d horeca -f createdb.sql
    cd datas
    python loadxml.py


# Configuration et démarrage

Editez `flask/local_config.py` pour écraser les valeurs par défaut spécifiées dans `flask/config.py`.

Démarrez l'app avec :

    cd flask/
    python app.py


Vous pouvez ensuite vous créer un compte ou utiliser un des utilisateurs déjà présents (leur mot de passe est indentique à leur nom d'utilisateur).
Si vous avez besoin d'un administrateur, Boris:Boris est un bon choix ;)
