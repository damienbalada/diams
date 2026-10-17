-- Standards d'abattage et de transport (ANI_SLAUGHTER) : l'indicateur n'était déclaré applicable qu'à la
-- mode et au luxe (migration du 16/10), alors qu'il concerne d'abord les acheteurs de viande et de
-- volaille. Première preuve (Bonduelle, European Chicken Commitment) invisible sans cette liste (17/10/2026).
insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'ANI_SLAUGHTER'
  and s.code in ('food', 'restaurant', 'retail_distribution', 'fmcg_group', 'pet_care')
on conflict do nothing;
