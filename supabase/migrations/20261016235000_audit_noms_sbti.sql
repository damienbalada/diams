-- Audit des noms (16/10/2026) : la ligne SBTi « B&S Group S.A. — Commitment removed » (distributeur
-- luxembourgeois) était rattachée à H&M Group, dont les objectifs sont validés. Rattachement faux, retiré.
delete from evidence ev using indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id
  and i.code = 'ENV_SBTI_VALIDATED' and e.slug = 'hm-group' and ev.excerpt like '%B&S Group S.A.%';
