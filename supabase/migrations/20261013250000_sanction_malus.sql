-- v0.7.4 (décision de l'éditeur, 13/10/2026 : « une règle plus sévère ») : une sanction
-- officielle récente ne pèse plus seulement dans le pilier gouvernance ; elle retire
-- des points à la note globale, décision par décision, selon le montant de l'amende.
insert into scoring_params (key, value, description) values
  ('sanction_malus_severe', 15, 'Points retirés à la note globale (sur 100) par décision officielle d''amende d''au moins 1 Md€ (v0.7.4).'),
  ('sanction_malus_major',   8, 'Points retirés par décision officielle d''amende d''au moins 100 M€ (v0.7.4).'),
  ('sanction_malus_other',   3, 'Points retirés par autre décision officielle (amende moindre, infraction constatée, immunité de clémence) (v0.7.4).'),
  ('sanction_malus_cap',    25, 'Plafond du retrait cumulé pour sanctions (v0.7.4).')
on conflict (key) do update set value = excluded.value, description = excluded.description;
