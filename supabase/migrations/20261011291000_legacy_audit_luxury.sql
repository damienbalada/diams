-- Suite de l'audit : les trois plafonds « exploitation animale » saisis en août
-- (reviewer curation-2026-08, sources de presse) pour Hermès, Kering et LVMH sont
-- remplacés par les citations de leurs documents d'enregistrement universels 2025
-- déposés à l'AMF (lot 15, vérifié mot pour mot).
update evidence set review_status = 'rejected', reviewer = 'remplace:audit-2026-10-11'
where review_status = 'approved' and reviewer = 'curation-2026-08' and id in (
  'eb4ecbbe-49f2-43e2-9c56-474b157d59a1', '9f6874cb-620c-46df-aaef-f40354dc58a4', 'f7240554-e34e-4212-894b-9bb8e78ae7f5'
);
