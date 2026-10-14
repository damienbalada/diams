-- Relecture de la refonte : quatre groupes français n'avaient pas de SIREN (et trois pas de LEI),
-- ce qui empêchait le rapprochement Égapro et les connecteurs par LEI (Hermès apparaissait sans
-- index Égapro alors qu'il déclare 99/100 pour 2025). Identifiants confirmés le 15/10/2026 dans
-- l'annuaire officiel des entreprises (sociétés actives) et dans le registre GLEIF (relevés
-- « ACTIVE » ; pour AXA, l'autre enregistrement porte un statut nul).
update entities set siren = '652014051', lei = coalesce(lei, '549300B8P6MUJ1YWTS08'), updated_at = now() where slug = 'carrefour' and siren is null;
update entities set siren = '302178892', updated_at = now() where slug = 'remy-cointreau' and siren is null;
update entities set siren = '572076396', lei = coalesce(lei, '969500Y4IJGHJE2MTJ13'), updated_at = now() where slug = 'hermes' and siren is null;
update entities set siren = '572093920', lei = coalesce(lei, 'F5WCUMTUM4RKZ1MAIE39'), updated_at = now() where slug = 'axa' and siren is null;
