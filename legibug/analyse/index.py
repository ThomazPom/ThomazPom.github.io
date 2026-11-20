"""Index LEGI article versions and their outgoing citation metadata."""
import sqlite3
import sys
import tarfile
import xml.etree.ElementTree as ET

database = sqlite3.connect(sys.argv[1])
database.executescript("""
CREATE TABLE IF NOT EXISTS article (
    path TEXT PRIMARY KEY, id TEXT, cid TEXT, num TEXT,
    start TEXT, end TEXT, state TEXT, body TEXT
);
CREATE INDEX IF NOT EXISTS article_id ON article(id);
CREATE TABLE IF NOT EXISTS citation (
    path TEXT, target TEXT, label TEXT
);
CREATE INDEX IF NOT EXISTS citation_path ON citation(path);
""")
rows, citations = [], []
TEXT_STATES = {"VIGUEUR", "VIGUEUR_ETEN", "VIGUEUR_DIFF", "ABROGE_DIFF"}

def flush():
    for path, *_ in rows:
        database.execute('DELETE FROM citation WHERE path=?', (path,))
    database.executemany('INSERT OR REPLACE INTO article VALUES (?,?,?,?,?,?,?,?)', rows)
    database.executemany('INSERT INTO citation VALUES (?,?,?)', citations)
    rows.clear()
    citations.clear()

with tarfile.open(fileobj=sys.stdin.buffer, mode='r|gz') as archive, database:
    for member in archive:
        if not member.isfile():
            continue
        if member.name.endswith('/liste_suppression_legi.dat'):
            for line in archive.extractfile(member):
                path = line.decode().strip()
                if path and '/article/' in path:
                    path = path.removesuffix('.xml') + '.xml'
                    database.execute('DELETE FROM article WHERE path=?', (path,))
                    database.execute('DELETE FROM citation WHERE path=?', (path,))
            continue
        if '/article/LEGI/ARTI/' not in member.name or not member.name.endswith('.xml'):
            continue
        if '/global/' not in member.name:
            continue
        path = 'legi/global/' + member.name.split('/global/', 1)[1]
        root = ET.parse(archive.extractfile(member)).getroot()
        meta = root.find('./META/META_SPEC/META_ARTICLE')
        context = root.find('./CONTEXTE/TEXTE')
        if meta is None or context is None:
            continue
        identifier = root.findtext('./META/META_COMMUN/ID', '')
        content = root.find('./BLOC_TEXTUEL/CONTENU')
        state = meta.findtext('ETAT', '')
        rows.append((path, identifier, context.get('cid', ''), meta.findtext('NUM', ''),
                     meta.findtext('DATE_DEBUT', ''), meta.findtext('DATE_FIN', ''),
                     state, ' '.join(content.itertext()) if content is not None and
                     state in TEXT_STATES else ''))
        if state in TEXT_STATES:
            citations.extend((path, link.get('id', ''), link.text or '')
                             for link in root.findall('./LIENS/LIEN')
                             if link.get('typelien') == 'CITATION' and link.get('sens') == 'source'
                             and link.get('id', '').startswith('LEGIARTI'))
        if len(rows) >= 1000:
            flush()
    flush()
print(database.execute('SELECT count(*) FROM article').fetchone()[0], 'article files indexed')
