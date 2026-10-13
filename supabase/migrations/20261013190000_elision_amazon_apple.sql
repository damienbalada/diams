-- Élision : « Circulaire de procuration 2026 d'Amazon / d'Apple » (et non « de Amazon »).
update evidence set excerpt = replace(replace(excerpt, ' de Amazon ', ' d''Amazon '), ' de Apple ', ' d''Apple ')
where excerpt ~ ' de (Amazon|Apple) ';
