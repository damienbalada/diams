-- Doublons de marques (17/10/2026). TENA existait deux fois chez Essity (« tena », preuve ESEF 2024 ; et
-- « tena-marque », créée le 15/10) ; Lancelot deux fois (« lancelot » chez Agrial, prouvée par la page
-- « Nos marques » d'Agrial, propriétaire de la Brasserie Lancelot depuis 2021 ; et « lancelot-marque »
-- sous la société Brasserie Lancelot, sans rattachement de celle-ci à Agrial). On garde « tena » et
-- « lancelot » ; le journal de « lancelot-marque » est reporté sur « lancelot ».
update indicator_reviews r set entity_id = (select id from entities where slug = 'lancelot')
where r.entity_id = (select id from entities where slug = 'lancelot-marque');
delete from entity_ownership_sources where entity_id in (select id from entities where slug in ('tena-marque', 'lancelot-marque'));
delete from entities where slug in ('tena-marque', 'lancelot-marque');
