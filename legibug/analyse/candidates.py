"""List article citations requiring manual review as CSV."""
import csv
import re
import unicodedata
import sqlite3
import sys

def normalized(text):
    text = unicodedata.normalize('NFKC', text).upper()
    return re.sub(r'([LRDA])\s*\.\s*(?=\d)', r'\1', text).translate(str.maketrans('‑–—', '---'))


def explicit_reference(body, number):
    target = normalized(number)
    if not re.fullmatch(r'[LRDA]?\d[0-9-]*', target):
        return False
    return re.search(r'(?<![A-Z0-9-])' + re.escape(target) + r'(?![0-9-])',
                     normalized(body)) is not None


database_path, as_of = sys.argv[1:]
with sqlite3.connect(database_path) as database:
    database.execute('CREATE INDEX IF NOT EXISTS article_cid_num ON article(cid, num)')
    rows = database.execute("""
        SELECT DISTINCT source.cid, source.num, source.id,
                        target.cid, target.num, target.id, target.end, citation.label,
                        EXISTS (
                          SELECT 1 FROM article AS replacement
                          WHERE replacement.cid = target.cid AND replacement.num = target.num
                            AND replacement.state IN ('VIGUEUR', 'VIGUEUR_ETEN', 'ABROGE_DIFF', 'VIGUEUR_DIFF')
                            AND replacement.start <= :date AND :date < replacement.end
                        ),
                        source.body
        FROM citation
        JOIN article AS source ON source.path = citation.path
        JOIN article AS target ON target.id = citation.target
        WHERE source.state IN ('VIGUEUR', 'VIGUEUR_ETEN', 'ABROGE_DIFF', 'VIGUEUR_DIFF')
          AND source.start <= :date AND :date < source.end
          AND target.state LIKE 'ABROG%'
          AND target.end <= :date
          AND target.num <> ''
        ORDER BY source.cid, source.num, target.cid, target.num
    """, {'date': as_of})
    writer = csv.writer(sys.stdout)
    writer.writerow(('texte_source', 'article_source', 'id_source',
                     'texte_vise', 'article_vise', 'id_vise', 'fin_version', 'citation', 'numero_reutilise', 'numero_dans_le_texte'))
    for *fields, body in rows:
        writer.writerow((*fields, int(explicit_reference(body, fields[4]))))
