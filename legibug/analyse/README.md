# Reproduire le relevé LEGI

Le relevé utilise les archives XML en accès libre de la DILA. La base SQLite et les archives restent locales. Le script traite les données en flux et tient compte des listes de suppression lors de l’application des mises à jour.

Pour l’édition au 20 novembre 2026, le stock global du 8 novembre est suivi des mises à jour du 8 novembre au soir jusqu’au 19 novembre inclus. Le fichier émis le 20 novembre à 22 h 22 est hors de cette première extraction. La date d’observation des versions est le 20 novembre.

```bash
set -euo pipefail
base=https://echanges.dila.gouv.fr/OPENDATA/LEGI/
curl -fsSL "${base}Freemium_legi_global_20261108-140000.tar.gz" | python3 index.py legi.sqlite
curl -fsSL "$base" | rg -o 'LEGI_202611(08|09|1[0-9])-[0-9]{6}\.tar\.gz' | sort -u > deltas.txt
while read -r delta; do
  curl -fsSL "$base$delta" | python3 index.py legi.sqlite
done < deltas.txt
python3 coverage.py legi.sqlite 2026-11-20 > coverage.csv
python3 local_refs.py legi.sqlite 2026-11-20 > local-refs.csv
python3 candidates.py legi.sqlite 2026-11-20 > candidates.csv
python3 sample.py 30 < candidates.csv > sample.csv
python3 derogations.py legi.sqlite 2026-11-20 > derogations.csv
```

Le décompte repose sur des identifiants de versions et leurs dates. Les listes de renvois sont des pistes à examiner. Une référence historique volontaire, un changement d’identifiant ou un numéro qui désigne un article d’un autre code peut produire un signal. L’échantillon des pistes mesure la précision du repérage parmi ces pistes. Il ne permet pas d’estimer la fréquence de toutes les incohérences juridiques.

Le relevé des dérogations explicites repère des formulations comme « nonobstant toutes dispositions contraires », y compris sans article cité. Un résultat peut être une exception voulue, une règle intégrée au même article ou une mesure dont la période est terminée. Le script produit des pistes à relire, sans conclure à un conflit.

[Archives LEGI de la DILA](https://echanges.dila.gouv.fr/OPENDATA/LEGI/)

Pour le décompte au 21 novembre, appliquer ensuite l’archive supplémentaire et changer la date de validité. Le tirage publié et sa relecture restent rattachés à l’extraction du 20 novembre.

```bash
curl -fsSL "${base}LEGI_20261120-222218.tar.gz" | python3 index.py legi.sqlite
python3 coverage.py legi.sqlite 2026-11-21 > coverage-2026-11-21.csv
```
