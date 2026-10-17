-- Décisions de l'éditeur du 17/10/2026 sur le rapport de nuit (suite).

-- Point 4 : une preuve approuvée sur une copie enregistrée de la page (le site refusant les robots)
-- garde cette trace jusque sur la fiche. compute_score_input transmet désormais la trace d'approbation
-- (reviewer) de chaque preuve ; la fonction est réécrite à partir de sa définition actuelle.
do $$
declare
  d text;
  n1 int;
  n2 int;
begin
  select pg_get_functiondef(p.oid) into d from pg_proc p where p.proname = 'compute_score_input';
  n1 := (length(d) - length(replace(d, 'e.excerpt, s.name', ''))) / length('e.excerpt, s.name');
  n2 := (length(d) - length(replace(d, '''excerpt'', excerpt,', ''))) / length('''excerpt'', excerpt,');
  if position('e.reviewer' in d) > 0 then
    return; -- déjà fait
  end if;
  if n1 <> 4 or n2 <> 1 then
    raise exception 'compute_score_input : forme inattendue (% branches, % sorties)', n1, n2;
  end if;
  d := replace(d, 'e.excerpt, s.name', 'e.excerpt, e.reviewer, s.name');
  d := replace(d, '''excerpt'', excerpt,', '''excerpt'', excerpt, ''reviewer'', reviewer,');
  execute d;
end $$;

-- Point 17 : la part d'investissements alignés sur la taxonomie verte de l'UE n'était applicable qu'à
-- l'énergie et à l'automobile ; elle l'est partout, affichée à titre d'information quand elle est
-- documentée (rien sinon), sans signal.
delete from indicator_sectors
where indicator_id = (select id from indicators where code = 'ENV_TAXONOMY_CAPEX');
