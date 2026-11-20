"""Count current article IDs by DILA archive branch and by official code."""
import csv
import sqlite3
import sys

database, as_of = sys.argv[1:]
with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as db:
    selection = """
        WITH active AS (
          SELECT DISTINCT id, cid,
             CASE WHEN path LIKE '%/code_en_vigueur/%' THEN 'code'
                  WHEN path LIKE '%/TNC_en_vigueur/%' THEN 'texte_non_codifie'
                  ELSE 'autre' END AS branch
          FROM article
          WHERE start <= :as_of AND :as_of < end
            AND state IN ('VIGUEUR', 'VIGUEUR_ETEN', 'ABROGE_DIFF', 'VIGUEUR_DIFF')
        )
    """
    params = {'as_of': as_of}
    writer = csv.writer(sys.stdout)
    writer.writerow(('branche', 'cid', 'versions_en_vigueur'))
    rows = db.execute(selection + """
        SELECT branch, '', count(DISTINCT id) FROM active GROUP BY branch
        UNION ALL
        SELECT branch, cid, count(DISTINCT id) FROM active
        WHERE branch = 'code' GROUP BY branch, cid
        ORDER BY 1, 2
    """, params)
    writer.writerows(rows)
