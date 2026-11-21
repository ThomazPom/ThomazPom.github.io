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

## Six mois pour une réponse de l’assureur après expertise

L’article L. 121-18 du code des assurances prévoit en principe une réponse sous six mois à compter de la déclaration si un expert est désigné. L’article L. 125-2 prévoit pour la garantie catastrophe naturelle une proposition dans le mois suivant la réception du rapport d’expertise définitif. Ces deux délais partent d’événements différents. En outre, l’article 30 de la loi du 26 mai 2026 rend le nouveau régime applicable aux contrats conclus ou tacitement reconduits à compter de la publication du décret qui doit fixer les exclusions. Le suivi du Sénat indique que ce décret est encore attendu. La règle des six mois ne fournit donc pas de conflit actuel démontré pour les assurés victimes d’une catastrophe naturelle.

[Article L. 121-18](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054136978) · [Article L. 125-2](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054141744) · [Suivi des décrets par le Sénat](https://www.senat.fr/application-des-lois/pjl23-550.html)

## Commission municipale des débits de boissons

L’article 1 de la loi du 26 mai 2026 a abrogé l’article L. 3331-7, qui créait une commission dans certaines communes et permettait au maire de la consulter sur les décisions relatives aux débits de boissons. Une recherche de « L. 3331-7 » et « commission municipale de débits de boissons » dans les articles en vigueur du corpus LEGI au 21 novembre n’a trouvé aucun texte qui maintienne cette consultation. L’article L. 3332-11 demande encore l’avis favorable du maire pour transférer la dernière licence IV d’une commune. Cet avis du maire et l’ancien avis de la commission sont deux actes distincts. La piste est écartée.

[Ancien article L. 3331-7](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000039787685/2026-05-24) · [Article L. 3332-11](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000041411152)

## Nomination au tour extérieur dans les corps d’inspection de l’État

La loi du 26 mai 2026 a abrogé les articles L. 326-6 et L. 326-7 du code général de la fonction publique. Ils permettaient à certains statuts de prévoir des nominations directes sous condition d’âge et après avis d’une commission. Le décret n° 94-1085 qui organisait cette consultation avait déjà été abrogé par le décret du 23 juillet 2025. Dans le corpus en vigueur au 21 novembre 2026, le renvoi retrouvé vers le L. 326-7 de ce code dispense certaines nominations de cette procédure. Il ne demande pas de saisir la commission. Les autres renvois du relevé concernent le code de la route ou l’ancien code du travail applicable à Mayotte. Aucun de ces renvois ne démontre le maintien d’une procédure de nomination pour de nouveaux candidats.

[Ancien article L. 326-6](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000044426794/2026-04-27) · [Décret du 23 juillet 2025](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000051954553) · [Disposition transitoire de l’ordonnance du 24 novembre 2021](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000044415252)

## Observatoire national des espaces naturels, agricoles et forestiers

L’article 1, XIII et XIV, de la loi du 26 mai 2026 abroge l’article L. 112-1 du code rural, qui fixait les missions de l’observatoire national, et retire sa mention de la loi sur la biodiversité. L’article D. 112-1-12 du code rural lui attribue encore les missions énumérées par le texte abrogé et prévoit un rapport annuel. L’article D. 112-1-15 prévoit encore au moins une réunion plénière par an. Ce décalage est vérifié. La recherche n’a pas établi qu’une commune doive encore transmettre des données à cet observatoire. Les commissions départementales de préservation des espaces naturels, agricoles et forestiers relèvent d’un autre article, L. 112-1-1.

[Loi du 26 mai 2026, article 1](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000054131317) · [Article D. 112-1-12](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000030817272) · [Article D. 112-1-15](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000030817258)

L’article D. 141-7-1 du code rural demande encore à la fédération des Safer d’envoyer chaque année au ministre de l’Agriculture une synthèse nationale des prix des terres et de leurs changements d’usage pour contribuer aux indicateurs de l’article L. 112-1. Cet objectif renvoie donc toujours aux indicateurs du texte abrogé. Le décret adresse la synthèse au ministre et les données départementales aux préfets. Le circuit d’information n’a donc pas perdu son destinataire, même si sa finalité affichée renvoie à l’ancien observatoire.

[Article D. 141-7-1, synthèses départementales et nationale](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006071367/LEGISCTA000006152464/2026-06-02/)
