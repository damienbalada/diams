-- Autres graphies relevées dans Open Products Facts (17/10/2026), reconnaissance des codes-barres seulement.
update entities set aliases = (select array(select distinct unnest(aliases || array['Flam Up', 'Flamup'])))
where slug = 'flam-up';
update entities set aliases = (select array(select distinct unnest(aliases || array['Moleskin'])))
where slug = 'moleskine';
