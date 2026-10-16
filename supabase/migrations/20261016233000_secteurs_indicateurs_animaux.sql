-- Secteurs des indicateurs animaux (16/10/2026). Les politiques matières de la mode (duvet, laine,
-- angora et mohair, peaux exotiques, cuir, abattage) concernent aussi les groupes de luxe (LVMH, Kering,
-- Hermès), comme le label « sans fourrure » ; les tests sur les animaux concernent toute entité qui vend
-- des cosmétiques : beauté, soin du corps (Garnier), groupes de grande consommation (L'Oréal, Unilever)
-- et de luxe (parfums). Sans cette liste, les preuves de ces entités n'étaient pas affichées.
insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where (i.code in ('ANI_DOWN_RDS', 'ANI_WOOL_MULESING', 'ANI_ANGORA_MOHAIR', 'ANI_EXOTIC_SKINS', 'ANI_LEATHER_TRACE', 'ANI_SLAUGHTER')
       and s.code in ('fashion_leather', 'luxury_group'))
   or (i.code = 'ANI_TESTING' and s.code in ('beauty_fragrance', 'personal_care', 'fmcg_group', 'luxury_group'))
on conflict do nothing;
