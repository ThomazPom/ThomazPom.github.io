# Publier une découverte dans Légibug

Modifier `fiches.json`, puis exécuter `python3 legibug/generer.py` depuis la racine du dépôt. Le script régénère `legibug/index.html` à partir du modèle et des données. Ajouter les fichiers modifiés au même commit, puis pousser sur la branche `main`. GitHub Pages publie cette version.

Chaque fiche porte sur une question juridique. Le champ `relation.participants` accepte autant de dispositions que nécessaire. Chaque participant indique sa référence, sa source, une citation et son rôle dans cette question. Plusieurs fiches peuvent renvoyer au même article, y compris à des alinéas différents. L’explication porte sur l’effet de leur combinaison.
