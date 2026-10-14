"""Accès Supabase via l'API REST (PostgREST), en service_role.

La service_role contourne la RLS : réservée au back-office / pipeline, jamais
exposée côté navigateur.
"""
from __future__ import annotations

from typing import Any

import httpx

from . import config


def _headers() -> dict[str, str]:
    return {
        "apikey": config.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }


#: L'API renvoie au plus 1 000 lignes par appel (réglage par défaut de Supabase).
PAGE = 1000


def get_all(client: httpx.Client, table: str, params: dict[str, Any], headers: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Toutes les lignes d'une table, page par page (tri stable sur l'identifiant,
    sauf tri explicite), au lieu des seules 1 000 premières."""
    out: list[dict[str, Any]] = []
    base = dict(params)
    base.setdefault("order", "id.asc")
    offset = 0
    while True:
        r = client.get(f"{config.SUPABASE_URL}/rest/v1/{table}", params={**base, "limit": PAGE, "offset": offset},
                       headers=headers or _headers())
        r.raise_for_status()
        rows = r.json()
        out += rows
        if len(rows) < PAGE:
            return out
        offset += PAGE


def list_entities(client: httpx.Client | None = None) -> list[dict[str, Any]]:
    """Toutes les entités avec leurs identifiants actuels."""
    config.require_supabase()
    c = client or httpx.Client(timeout=30)
    try:
        return get_all(c, "entities", {"select": "id,slug,legal_name,display_name,country,lei,siren,is_brand"})
    finally:
        if client is None:
            c.close()


def update_entity(entity_id: str, fields: dict[str, Any], client: httpx.Client | None = None) -> None:
    """Met à jour une entité (ex: {'lei': ..., 'siren': ...})."""
    config.require_supabase()
    c = client or httpx.Client(timeout=30)
    try:
        r = c.patch(
            f"{config.SUPABASE_URL}/rest/v1/entities",
            params={"id": f"eq.{entity_id}"},
            headers={**_headers(), "Prefer": "return=minimal"},
            json=fields,
        )
        r.raise_for_status()
    finally:
        if client is None:
            c.close()
