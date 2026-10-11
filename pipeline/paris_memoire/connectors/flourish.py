"""Lecture des visualisations Flourish publiées (données embarquées dans la page).

Plusieurs organismes publient leurs classements complets sous forme de
visualisations Flourish (KnowTheChain, CDP…) : la page d'intégration contient
les données telles qu'elles sont affichées (`_Flourish_data`) et le nom des
colonnes (`_Flourish_data_column_names`). On les lit sans interprétation.
"""
from __future__ import annotations

import json


def flourish_url(vis_id: int) -> str:
    return f"https://flo.uri.sh/visualisation/{vis_id}/embed?auto=1"


def flourish_json(html: str, name: str):
    """Objet JSON affecté à la variable `name` dans la page d'intégration."""
    start = html.index(f"{name} = ") + len(name) + 3
    return json.JSONDecoder().raw_decode(html[start:])[0]


def table_rows(html: str, dataset: str = "rows") -> list[dict[str, str]]:
    """Jeu de données tabulaire (une liste de `columns` par ligne) → dictionnaires."""
    cols = flourish_json(html, "_Flourish_data_column_names")
    names = cols.get("data", cols)[dataset]["columns"]   # selon la version de Flourish
    data = flourish_json(html, "_Flourish_data")
    return [dict(zip(names, r.get("columns") or [])) for r in data.get("data", data)[dataset]]
