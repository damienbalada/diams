# Seeds historiques — ne pas rejouer

Ces fichiers (01 → 35) racontent **comment** la base a été constituée, lot par
lot, avec les justifications de curation en commentaire. Ils restent utiles pour
l'audit (pourquoi telle preuve, telle source), mais **ils ne reflètent plus
l'état de production** : des preuves ont depuis été remplacées par les
connecteurs (SBTi, Égapro, benchmarks) ou retirées.

Mesure du 10/10/2026 : rejouer ces seeds sur une base vierge produit
**64 preuves absentes de la production** (42 SBTi saisies à la main puis
remplacées par le connecteur, 19 lignes « loi de 1995 » retirées, 3 benchmarks
mis à jour).

**Reconstruire une base = migrations puis [`../99_snapshot.sql`](../99_snapshot.sql)**,
généré depuis la production par `node scripts/snapshot-db.mjs`.
