-- Leaping Bunny (Cruelty Free International) : programme de certification « sans tests sur les animaux »
-- (produits finis et ingrédients, contrôle des fournisseurs, audits indépendants). L'annuaire public des
-- marques approuvées sert de registre, comme l'annuaire B Corp : la fiche d'une marque sous
-- /approved-brands/listing/ établit l'approbation.
insert into sources (code, name, tier, publisher, url, description)
values ('LEAPING_BUNNY', 'Annuaire des marques approuvées Leaping Bunny (Cruelty Free International)', 'audited_ngo',
        'Cruelty Free International', 'https://www.crueltyfreeinternational.org/approved-brands/',
        'Marques cosmétiques et d''entretien certifiées sans tests sur les animaux (programme Leaping Bunny, audits indépendants), en anglais.')
on conflict (code) do nothing;
