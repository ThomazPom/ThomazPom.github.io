"""Génère la page statique de Légibug à partir des fiches JSON."""
import csv
import json
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parent
fiches = json.loads((root / "fiches.json").read_text(encoding="utf-8"))
template = (root / "modele.html").read_text(encoding="utf-8")

def article_ids(fiche):
    relation = fiche["relation"]
    entries = relation["participants"] + fiche["sources"]
    entries += [
        renvoi[role]
        for renvoi in relation.get("renvois", [])
        for role in ("source", "cible")
    ]
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
    if entree := fiche.get("entree"):
        output.append(f'<p class="entree">{escape(entree["face_a_face"])}</p>')
        output.append(f'<p>{escape(entree["texte"])}</p>')
        output.append(f'<p>{escape(entree["raison"])}</p>')
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
    if renvois := relation.get("renvois"):
        output.append('<details><summary>Voir les renvois vérifiés</summary><ul>')
        for renvoi in renvois:
            source = renvoi["source"]
            cible = renvoi["cible"]
            output.append(
                f'<li><a href="{escape(source["url"])}">{escape(source["reference"])}</a>'
                f' renvoie à <a href="{escape(cible["url"])}">{escape(cible["reference"])}</a>'
                f' (abrogé le {escape(renvoi["fin_validite"])})</li>'
            )
        output.append('</ul></details>')
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

def render_review():
    with (root / "analyse" / "sample.csv").open(encoding="utf-8", newline="") as stream:
        sample = list(csv.DictReader(stream))
    with (root / "analyse" / "relecture.csv").open(encoding="utf-8", newline="") as stream:
        review = list(csv.DictReader(stream))
    seen = set()
    for row in review:
        rank = int(row["rang"])
        if rank in seen or not 1 <= rank <= len(sample):
            raise ValueError(f"Rang de relecture invalide ou en double : {rank}")
        if any(row[key] != sample[rank - 1][key] for key in ("id_source", "id_vise")):
            raise ValueError(f"Identifiants de relecture divergents au rang {rank}")
        seen.add(rank)
    counts = Counter(row["statut"] for row in review)
    if counts.keys() - {"confirmé", "écarté", "à vérifier"}:
        raise ValueError("Statut de relecture inconnu")
    return (
        f"<p>{len(review)} pistes examinées sur {len(sample)} dans le tirage. "
        f"{counts['confirmé']} renvois confirmés, {counts['écarté']} pistes écartées "
        f"et {counts['à vérifier']} à approfondir.</p>"
    )


assert template.count('<!-- FICHES -->') == 1
assert len({fiche["id"] for fiche in fiches}) == len(fiches)
vedettes = sorted(
    (fiche for fiche in fiches if "entree" in fiche),
    key=lambda fiche: fiche["entree"]["ordre"],
)
intro = "\n".join(
    f'<li><h3><a href="#{escape(fiche["id"])}">{escape(fiche["entree"]["titre"])}</a></h3>'
    f'<p class="entree">{escape(fiche["entree"]["face_a_face"])}</p>'
    f'<p><strong>Pourquoi ces réponses diffèrent</strong><br>{escape(fiche["entree"]["raison"])}</p></li>'
    for fiche in vedettes[:8]
)
output = template.replace("<!-- EXEMPLES -->", intro)
output = output.replace("<!-- FICHES -->", "\n".join(map(render, vedettes + [fiche for fiche in fiches if "entree" not in fiche])))
totaux = Counter(fiche["type"] for fiche in fiches)
couverture = (
    f"<p><strong>{len(fiches)} fiches publiées</strong> dans le catalogue.</p>"
    + "<ul>"
    + "".join(f"<li>{escape(nature)} ({total})</li>" for nature, total in totaux.most_common())
    + "</ul>"
)
output = output.replace("<!-- COUVERTURE -->", couverture)
output = output.replace("<!-- RELECTURE -->", render_review())
(root / "index.html").write_text(output, encoding="utf-8")
