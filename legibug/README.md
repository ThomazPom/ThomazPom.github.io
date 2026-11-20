# Publier une découverte dans Légibug

Modifier `fiches.json`, puis exécuter `python3 legibug/generer.py` depuis la racine du dépôt. Le script régénère `legibug/index.html` à partir du modèle et des données. Ajouter les fichiers modifiés au même commit, puis pousser sur la branche `main`. GitHub Pages publie cette version.

Chaque fiche décrit une relation entre les textes, avec une explication et des sources. Le champ `textes` contient les références, les URL et les citations vérifiées à afficher côte à côte. Les fiches existantes sont enrichies au fil des vérifications.
