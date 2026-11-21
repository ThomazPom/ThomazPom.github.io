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

## Vérification des règles sur les véhicules à la casse

La loi du 26 mai 2026 a retiré l’exigence d’un centre « agréé » dans l’article L. 541-21-5, qui organise l’enlèvement de plusieurs épaves. L’article R. 543-155-1 prévoit aujourd’hui un régime d’enregistrement avec une exception pour certains agréments délivrés avant 2025. L’annexe II de l’arrêté du 2 mai 2012 exige encore que les véhicules reçus par un broyeur aient été traités par un centre agréé, mais elle fixe le cahier des charges attaché à un agrément de broyeur. Avant de publier un conflit, il faut établir si cette clause s’impose encore à un broyeur qui reçoit des véhicules d’un centre enregistré et dépourvu d’agrément.

[Article 5 de la loi du 26 mai 2026](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000054131386) · [Article R. 543-155-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046669929) · [Arrêté du 2 mai 2012](https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000025835110)

L’article R. 543-155-2 permet à un broyeur de recevoir des véhicules provenant de centres VHU. Il exige une dépollution complète et un désassemblage avant broyage. L’article 21 de l’arrêté du 22 avril 2026 distingue expressément les centres enregistrés des centres agréés et les broyeurs autorisés des broyeurs agréés. Pour les deux catégories, il reprend uniquement l’obligation de déclaration d’activité en 2026 et 2027 prévue dans les annexes de 2012. Ce renvoi précis ne suffit pas à étendre aux broyeurs autorisés la clause de 2012 sur la provenance des véhicules. La question pratique reste celle du broyeur qui travaille encore sous un ancien agrément.

[Article R. 543-155-2](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046667169) · [Article 21 de l’arrêté du 22 avril 2026](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000054031458)

## Déclaration des dons des entreprises

L’article 6 de la loi du 26 mai 2026 abroge le 6 de l’article 238 bis du code général des impôts à compter du 1er janvier 2027. Au 21 novembre 2026, l’article 49 septies X de l’annexe III peut donc toujours renvoyer à ce 6 pour la déclaration des dons des entreprises. La piste est écartée pour la date étudiée. La version du règlement applicable au 1er janvier 2027 devra être vérifiée séparément.

[Article 6 de la loi du 26 mai 2026](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000054131445) · [Article 238 bis](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054402913) · [Article 49 septies X](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038561759)
