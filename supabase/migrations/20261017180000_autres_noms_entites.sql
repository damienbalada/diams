-- Autres noms des entités (17/10/2026) : graphies sous lesquelles une marque ou un groupe est saisi dans les
-- bases ouvertes de produits (« procter-gamble », « p&g », « papermate », « scjohnson »…). Ils servent
-- seulement à reconnaître un code-barres scanné ; ils ne sont jamais affichés comme nom et ne prouvent
-- rien (la propriété reste prouvée par la preuve d'appartenance). Ne sont retenues que des graphies sans
-- ambiguïté (pas « johnson », partagé par SC Johnson et Johnson & Johnson).
alter table entities add column if not exists aliases text[] not null default '{}';
comment on column entities.aliases is
  'Autres graphies du nom, pour reconnaître un produit scanné (jamais affichées, ne prouvent rien).';

update entities e set aliases = v.noms, updated_at = now()
from (values
  ('procter-gamble', array['Procter Gamble', 'P&G', 'P G', 'Procter and Gamble']),
  ('aldi-france', array['Aldi']),
  ('leclerc', array['Leclerc', 'E Leclerc']),
  ('sc-johnson', array['SCJohnson', 'SC Johnson', 'S C Johnson']),
  ('paper-mate', array['Papermate']),
  ('head-shoulders', array['Head and Shoulders', 'Head Shoulders']),
  ('l-arbre-vert', array['L Arbre Vert', 'Arbre Vert']),
  ('melitta', array['Melitta']),
  ('lea-nature', array['Léa Nature', 'Lea Nature']),
  ('le-livre-de-poche', array['Livre de Poche']),
  ('calmann-levy', array['Calman Levy', 'Calmann Levy']),
  ('mr-propre', array['Monsieur Propre']),
  ('cillit-bang', array['Cilit Bang', 'Cillit']),
  ('bic', array['BIC SA', 'Bic Kids']),
  ('hamelin', array['Groupe Hamelin']),
  ('systeme-u', array['Super U', 'Hyper U', 'U Express']),
  ('eco-plus-leclerc', array['Eco Plus'])
) as v(slug, noms)
where e.slug = v.slug;
