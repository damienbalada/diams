# Outils de la collecte complète (15/10/2026)

Lecture des rapports réglementés, groupe par groupe. Rien n'est écrit en base sans passer par
`import_curated` puis `verify_curated` (citation retrouvée mot pour mot, mots de l'indicateur,
valeur ou calcul recontrôlé), ni par le journal de relecture (`ecrit_journal.py`).

- `recense_esef.py` : dernier rapport annuel (12 mois) de chaque entité avec LEI sur filings.xbrl.org.
- `manques_rapport.py` : indicateurs de rapport sans preuve ni lecture consignée, par groupe.
- `gm.py <slug>` / `g.py <slug> "<motif>"` : recherches dans le texte du rapport (mode « ~ » tolérant
  aux espaces parasites des extractions).
- `lot100.py` + `lot100_ecrire.py` : les preuves et lignes de journal du lot 100, rédigées à la main
  (citations exactes, cadre, calculs en toutes lettres) ; écrit le CSV de `curated/` et le journal.
- `ecrit_journal.py <fichier.json> [--apply]` : écrit les lectures (`reviewer = lecture-rapport`).
