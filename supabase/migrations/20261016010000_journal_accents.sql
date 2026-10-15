-- Journal de relecture : 123 lignes du 15/10/2026 dont le texte avait été mal décodé
-- (« publiÃ© » au lieu de « publié »). Seules trois suites de caractères sont concernées
-- (é, à, è) ; le sens des lignes ne change pas.
update indicator_reviews
set detail = replace(replace(replace(detail, 'Ã©', 'é'), 'Ã' || chr(160), 'à'), 'Ã¨', 'è')
where detail ~ 'Ã';
