"""Génère la page statique de Légibug à partir des fiches JSON."""
import json
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parent
fiches = json.loads((root / "fiches.json").read_text(encoding="utf-8"))
template = (root / "modele.html").read_text(encoding="utf-8")

def render(fiche):
    output = [
        f'<article id="{escape(fiche["id"])}">',
        f'<div class="topic">{escape(fiche["type"])} · {escape(fiche["domaine"])}</div>',
        f'<h3>{escape(fiche["titre"])}</h3>',
    ]
    if fiche["textes"]:
        output.append('<div class="comparaison">')
        for texte in fiche["textes"]:
            href = escape(texte["url"])
            label = escape(texte["reference"])
            output.extend([
                '<figure>',
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
    output.append('</article>')
    return '\n'.join(output)

assert template.count('<!-- FICHES -->') == 1
assert len({fiche["id"] for fiche in fiches}) == len(fiches)
output = template.replace('<!-- FICHES -->', '\n'.join(map(render, fiches)))
(root / "index.html").write_text(output, encoding="utf-8")
