-- Autres graphies relevées dans Open Products Facts pour le tabac (17/10/2026), reconnaissance des codes-
-- barres seulement : « Luckies », « Lucky Strike Red » (Lucky Strike), « Philip Morris » au sens du groupe.
update entities set aliases = (select array(select distinct unnest(aliases || array['Luckies', 'Lucky Strike Red'])))
where slug = 'lucky-strike';
update entities set aliases = (select array(select distinct unnest(aliases || array['PMI', 'Philip Morris France'])))
where slug = 'philip-morris-international';
update entities set aliases = (select array(select distinct unnest(aliases || array['Zigzag', 'Zig Zag'])))
where slug = 'zig-zag';
