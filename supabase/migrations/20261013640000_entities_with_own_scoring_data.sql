-- Entités qui ont des données de notation propres (preuves publiées, régimes de
-- publication obligatoire, dispenses). Les autres — la plupart des marques — sont notées
-- uniquement à partir de leur groupe racine (compute_score_input) : deux marques sans
-- donnée propre qui partagent le groupe racine, le secteur, le pays et l'indicateur
-- « sans exploitation animale » reçoivent exactement la même note. Le site s'en sert pour
-- ne calculer cette note qu'une fois (temps de calcul de l'accueil et du classement).
-- Fonction en droits de l'appelant : même visibilité que compute_score_input.
create or replace function entities_with_own_scoring_data()
returns setof uuid
language sql
stable
set search_path = public
as $$
  select entity_id from evidence_active
  union
  select entity_id from entity_regimes
  union
  select entity_id from obligation_exemptions
$$;

comment on function entities_with_own_scoring_data() is
  'Identifiants des entités ayant des preuves publiées, des régimes ou des dispenses propres (déduplication du calcul des notes de marques).';
