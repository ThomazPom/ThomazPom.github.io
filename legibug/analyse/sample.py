"""Draw a stable sample of candidate references, one row per source/target pair."""

import csv
import hashlib
import sys

sample_size = int(sys.argv[1])
seed = 'legibug-2026-11-20-v1'
reader = csv.DictReader(sys.stdin)
writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
keyed = {}
for row in reader:
    key = (row['id_source'], row['id_vise'])
    if key not in keyed or row['numero_dans_le_texte'] == '1':
        keyed[key] = row

def rank(key):
    return hashlib.sha256('|'.join((seed, *key)).encode()).digest()

writer.writeheader()
for key in sorted(keyed, key=rank)[:sample_size]:
    writer.writerow(keyed[key])
