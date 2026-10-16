"""Reconnaissance de caractères (OCR) des PDF scannés, sans texte (arrêtés préfectoraux de Géorisques).

Le texte reconnu est gardé en cache par empreinte du fichier : l'outil de collecte et le vérificateur
lisent ainsi exactement le même texte, et une citation « reconnue par OCR » se vérifie mot pour mot
contre lui. La reconnaissance perd parfois les accents ou colle des mots : la citation est reprise
telle quelle, jamais corrigée (décision de l'éditeur, 16/10/2026).
"""
from __future__ import annotations

import hashlib
import os
import re
import unicodedata

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache", "ocr")
_ENGINE = None


def pdf_text_or_ocr(pdf: bytes, min_chars_per_page: int = 80) -> tuple[str, bool]:
    """(texte, reconnu_par_ocr). Texte du PDF s'il en a ; sinon OCR (200 points par pouce)."""
    import pymupdf
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    native = " ".join(p.get_text() or "" for p in doc)
    if len(native.strip()) >= min_chars_per_page * max(1, len(doc)):
        return re.sub(r"\s+", " ", native), False
    key = hashlib.sha1(pdf).hexdigest()
    path = os.path.join(CACHE_DIR, key + ".txt")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read(), True
    global _ENGINE
    if _ENGINE is None:
        from rapidocr_onnxruntime import RapidOCR
        _ENGINE = RapidOCR()
    parts = []
    for page in doc:
        res, _ = _ENGINE(page.get_pixmap(dpi=200).tobytes("png"))
        parts.append(" ".join(r[1] for r in (res or [])))
    text = re.sub(r"\s+", " ", " ".join(parts)).strip()
    os.makedirs(CACHE_DIR, exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)
    return text, True


def loose_pattern(phrase: str) -> str:
    """Motif tolérant aux défauts de l'OCR : accents facultatifs, espaces facultatives entre lettres."""
    out = []
    for ch in phrase:
        if ch == " ":
            out.append(r"\s*")
            continue
        base = unicodedata.normalize("NFD", ch)[0]
        out.append(f"[{re.escape(base)}{re.escape(ch)}]" if base != ch else re.escape(ch))
        out.append(r"\s*")
    return "".join(out)
