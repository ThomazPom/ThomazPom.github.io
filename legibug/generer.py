"""Génère la page statique de Légibug à partir des fiches JSON."""
import json
import re
from collections import defaultdict
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parent
fiches = json.loads((root / "fiches.json").read_text(encoding="utf-8"))
template = (root / "modele.html").read_text(encoding="utf-8")

def article_ids(fiche):
    entries = fiche["relation"]["participants"] + fiche["sources"]
    return {
        match.group()
        for entry in entries
        if (match := re.search(r"LEGIARTI[0-9]+", entry["url"]))
    }


fiches_par_article = defaultdict(list)
for fiche in fiches:
    for article in article_ids(fiche):
        fiches_par_article[article].append(fiche["id"])


def render(fiche):
    output = [
        f'<article id="{escape(fiche["id"])}">',
        f'<div class="topic">{escape(fiche["type"])} · {escape(fiche["domaine"])}</div>',
        f'<h3>{escape(fiche["titre"])}</h3>',
    ]
    relation = fiche["relation"]
    if relation["question"]:
        output.append(f'<p class="question">{escape(relation["question"])}</p>')
    if relation["participants"]:
        output.append('<div class="comparaison">')
        for texte in relation["participants"]:
            href = escape(texte["url"])
            label = escape(texte["reference"])
            output.extend([
                '<figure>',
                f'<div class="topic">{escape(texte["role"])}</div>',
                f'<blockquote>{escape(texte["citation"])}</blockquote>',
                f'<figcaption><a href="{href}">{label}</a></figcaption>',
                '</figure>',
            ])
        output.append('</div>')
    output.extend(f'<p>{escape(paragraph)}</p>' for paragraph in fiche["explication"])
    links = [
        f'<a href="{escape(source["url"])}">{escape(source["label"])}</a>'
        for source in fiche["sources"]
    ]
    output.append('<p class="sources">' + ''.join(links) + '</p>')
    related_ids = {
        related_id
        for article in article_ids(fiche)
        for related_id in fiches_par_article[article]
        if related_id != fiche["id"]
    }
    if related_ids:
        links = [
            f'<a href="#{escape(other["id"])}">{escape(other["titre"])}</a>'
            for other in fiches if other["id"] in related_ids
        ]
        output.append('<p class="sources"><strong>Articles en commun</strong>' + ''.join(links) + '</p>')
    output.append('</article>')
    return '\n'.join(output)

assert template.count('<!-- FICHES -->') == 1
assert len({fiche["id"] for fiche in fiches}) == len(fiches)
output = template.replace('<!-- FICHES -->', '\n'.join(map(render, fiches)))
(root / "index.html").write_text(output, encoding="utf-8")
