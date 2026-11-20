"""Report explicit article numbers that only match historical same-code versions."""

import csv
import re
import sqlite3
import sys
from collections import defaultdict

database, date = sys.argv[1:]
article_reference = re.compile(
    r"\b(?:articles?|art\.)\s+([LRDA])\s*\.\s*(\d+(?:[-‑–]\d+)+)",
    re.IGNORECASE,
)
external_title = re.compile(
    r"^\s*(?:du code\b|de la loi\b|du décret\b|de l['’]ordonnance\b)",
    re.IGNORECASE,
)
number_pattern = re.compile(r"\s*([LRDA])\.?\s*(\d+(?:[-‑–]\d+)+)\s*", re.IGNORECASE)


def article_key(number):
    match = number_pattern.fullmatch(number)
    if match:
        return match[1].upper() + match[2].replace('‑', '-').replace('–', '-')
    return None


with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as db:
    active = set()
    retired = defaultdict(list)
    for cid, number, identifier, start, end, state in db.execute(
        "SELECT DISTINCT cid, num, id, start, end, state FROM article WHERE cid LIKE 'LEGITEXT%'"
    ):
        key = article_key(number)
        if key is None:
            continue
        if state in ('VIGUEUR', 'VIGUEUR_ETEN', 'ABROGE_DIFF', 'VIGUEUR_DIFF') and start <= date < end:
            active.add((cid, key))
        elif state.startswith('ABROG') and end <= date:
            retired[cid, key].append((end, identifier))

    writer = csv.writer(sys.stdout)
    writer.writerow(('code', 'id_source', 'article_vise', 'id_vise', 'fin_version', 'extrait'))
    for cid, identifier, body in db.execute("""
        SELECT DISTINCT cid, id, body FROM article
        WHERE state IN ('VIGUEUR', 'VIGUEUR_ETEN', 'ABROGE_DIFF', 'VIGUEUR_DIFF') AND start <= ? AND end > ?
          AND cid LIKE 'LEGITEXT%'
    """, (date, date)):
        seen = set()
        body = ' '.join(body.split())
        for match in article_reference.finditer(body):
            key = article_key(''.join(match.groups()))
            pair = cid, key
            if key in seen or pair in active or pair not in retired:
                continue
            if external_title.match(body[match.end():]):
                continue
            seen.add(key)
            end, target = max(retired[pair])
            excerpt = body[max(0, match.start() - 75):match.end() + 90]
            writer.writerow((cid, identifier, key, target, end, excerpt))
