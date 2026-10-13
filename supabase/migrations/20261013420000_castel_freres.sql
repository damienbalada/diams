-- Castel Frères (vins de grande surface : Roche Mazet, Baron de Lestac, Vieux Papes…),
-- d'après son site officiel castel-freres.com. SIREN vérifié dans l'annuaire officiel des
-- entreprises (siège à Blanquefort) et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'castel-freres', 'Castel Frères', 'Castel Frères', '9695004E833OWFEYKQ86', '482283694', 'FR', s.id, false
from sectors s where s.code = 'wines_spirits'
on conflict (slug) do nothing;
