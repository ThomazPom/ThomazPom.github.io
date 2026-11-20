"""Repère des dérogations explicites, même sans numéro d'article cité."""

import csv
import re
import sqlite3
import sys

SIGNALS = re.compile(
    r"\b(?:nonobstant toutes? dispositions? contraires?|"
    r"par dérogation aux? (?:dispositions|règles|principes)|"
    r"ne sont pas applicables par dérogation)\b",
    re.IGNORECASE,
)

database, date = sys.argv[1:]
connection = sqlite3.connect(database)
articles = connection.execute(
    """
    SELECT DISTINCT cid, id, num, body
    FROM article
    WHERE start <= ? AND end > ?
      AND state IN ('VIGUEUR', 'VIGUEUR_DIFF', 'ABROGE_DIFF')
    ORDER BY cid, id
    """,
    (date, date),
)
writer = csv.writer(sys.stdout)
writer.writerow(("texte", "version", "article", "formulation", "extrait"))
for cid, article_id, number, body in articles:
    normalized = " ".join(body.split())
    for match in SIGNALS.finditer(normalized):
        excerpt = normalized[max(0, match.start() - 70):match.end() + 130]
        writer.writerow((cid, article_id, number, match.group(), excerpt))
