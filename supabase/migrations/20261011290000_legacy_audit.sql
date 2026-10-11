-- =============================================================================
-- Audit des lignes saisies à la main avant les connecteurs (curation-v1) — fin
-- -----------------------------------------------------------------------------
-- 248 lignes approuvées sans vérification contre leur source (saisie initiale).
-- Les connecteurs déterministes et les lots vérifiés mot pour mot en ont
-- remplacé l'essentiel (KnowTheChain, BBFAW, KSE, CDP, registre UE, SBTi, FTI,
-- Fur Free Retailer, Break Free From Plastic, rapports annuels déposés à l'AMF,
-- InfluenceMap). Restent :
--
-- 1. REMPLACÉES par une donnée officielle plus récente (retirées) : les lignes
--    ci-dessous, chacune couverte par un connecteur ou un lot vérifié.
--
-- 2. INVÉRIFIABLES en l'état (remises EN ATTENTE, donc hors des notes, pas
--    supprimées) : paraphrases sans citation, ou source citée qui ne contient
--    pas le fait (« cuir » de Chanel absent de l'article cité ; amende CNIL à
--    Google donnée pour 90 M€ ; rapport de la Rapporteuse spéciale de l'ONU
--    déjà marqué « à valider »…). Elles reviendront dans la note quand elles
--    seront vérifiées mot pour mot dans une source primaire.
--
-- 3. FTI : la liste complète 2023 est chargée (import_fti) → indicateur
--    complémentaire. « Sans fourrure » : label du programme Fur Free Retailer
--    → presence_only (présent, il compte ; absent, il ne dit rien).
-- =============================================================================

update evidence set review_status = 'rejected', reviewer = 'remplace:audit-2026-10-11'
where review_status = 'approved' and reviewer = 'curation-v1' and id in (
  'eb4ecbbe-49f2-43e2-9c56-474b157d59a1', '9f6874cb-620c-46df-aaef-f40354dc58a4', 'f7240554-e34e-4212-894b-9bb8e78ae7f5',
  '978dbd23-5d56-4e61-9da0-09f43d60055e',
  'f0e044e7-fde7-40ec-80c9-f436687cc362', '83a99cf0-be56-4268-af51-d87d7223a3bd', '3088c9e1-c024-4181-8128-bc0eda9ff233',
  'bde3c590-c13a-46fa-889b-cee3325cdfad', 'f86c80d2-4c62-4c96-ae1a-daeb028e9678',
  'fb4bed5f-fb66-43d1-830d-bcb666278c87', '180373ec-a799-42f7-9e34-a49779c0d461', '6ca2a783-3a3e-43df-a1dd-980468f58fa9',
  'b8579d76-d26e-455e-901c-94925862eeba',
  'fdcf35b5-fe41-44d2-aced-99af9002ba37', 'a2f7f2f8-8624-44cd-bb5f-8c618fadff39', '960a0064-4ca8-4e0c-8b72-fc04ae4c3c59',
  '56b228fb-17e9-45b5-a5e1-ad6fe8afe586', '1b4222f2-5fac-4615-aac4-30ea2f97122c', 'ea261649-c717-4814-b4a6-96a441e81f5d',
  '887046fc-e810-4634-9ef9-c09fcd2549ed', 'ceb7f45b-4ddf-4dca-80f8-a337e2e2a2ce', '54dfbf51-4014-45fb-badf-ee0b909ba7c9',
  '5899e888-8506-454c-9009-6654d2121357', '2cd521d1-8ba3-41f2-a3da-e96a95012385',
  '2fbe4131-4604-45cc-a862-c030c622fed2',
  'eca51d14-0a4c-493b-a706-7f08f1378c89', '03dd8fbd-e5b1-41ea-b164-e9c780565bac'
);

update evidence set review_status = 'pending', reviewer = 'a-verifier:sans-citation-2026-10-11'
where review_status = 'approved' and reviewer in ('curation-v1', 'curation-2026-08') and id in (
  '1b258982-8ba9-4fa3-afbc-7bbef5cce8df', 'e908cfd5-a7e7-4f8b-8d64-46a7951688cb', '0af90b0c-9181-43e2-87cc-2dfcb256d357',
  '8ffb897b-6232-4004-a7bb-2e7fba915140', '31219579-1fab-4584-9ac4-e5afaab356c8', '81822f43-c80d-49e0-b9ae-4214d6ae0f3e',
  '60129e22-d0be-4810-979d-3e5e605d8b6e',
  'bd95b5e9-b384-418b-aa02-437e6b1e318c', '1ab353c5-372c-4820-9d6d-cce65edc359b', '0da2c9e7-697d-4e96-beab-55c7c5f8e84b',
  'cf4484aa-1928-4564-9ab3-5d55d1bec1b9', '8500996d-b81c-4433-aa54-6cb6815e8898',
  '8e4deecd-80ef-4f90-99d5-a24c78060f84', '2ab0319e-4e9c-49b5-b9b7-03da2245782b', '122a00e9-c113-4202-8f86-414adf7476e6',
  'ddf20725-8b33-4ad6-819c-8233cab33f56',
  '870e2af0-1231-4301-a7bc-6cd2bd131b83', '87cc556a-7749-49e1-8fa7-c53cc91275c2', '8ae7ebfb-63c2-4944-9e02-8067444eb78c',
  '29a51a15-8f3a-46f1-99fd-f4e90c91175a',
  '3533c087-b1c7-4858-8b50-97774de39fce', 'b934d4a3-8c02-4b7b-8d73-0de498512be2', '1543b3f6-914e-4833-a621-7a53f1492326',
  '2f54fce3-086e-4d36-9ca3-f1c770355b60',
  '7d80ad16-0eae-45d3-bcdf-65a93b0979fb',
  '0bde00ec-7171-4614-90db-a1472a463dbe', '18f5a47f-3bf3-46a9-a970-fc9ec187adf8',
  'a9532122-d91f-47be-b7d2-77b09eef4b9e', '5336a3c7-38eb-413d-a859-400fee17fafe', 'b98bb21f-3a79-401b-bcb7-a69bdb4a821d',
  'a47919ad-9d1a-49d2-a0a5-1f362ad6d38a', 'e822e632-f02b-4aec-afcd-56a357a772e4', '1bc830e6-665c-4e40-b0ac-65c3256b2ff1',
  '7392ce78-6797-4865-81fc-86242f3f5148', '9ed2f668-3369-4ffd-9ea6-becad930d7f2',
  'aa924f4d-81d1-40f2-aa6a-a389b2b4b3ac', '5a00361c-fa57-450a-bcb8-e46c3e42ea88', 'ad04d935-fee0-4104-9878-ea9fda008688',
  '8dde4f42-19f2-48b3-a6b6-3ad672aa398e', 'b035dbc9-3352-45f3-9b73-771166dec7f7', 'cf1ee3ab-d164-423a-9948-aabfb7adb9e3',
  '6b4e744e-ef50-43a4-b10f-61bca178f88a', '1d200882-f446-4c05-9490-3cb3a8284e8f', '6c812da8-f1fc-4a35-ad07-d2a35b59137e',
  '3823f8b5-291d-4a87-b837-e9993b718323', '13fff197-3031-4615-855c-daf73172b6fe',
  '99401aee-86fa-4a93-965b-a6989aa0e06d', 'f4bcf141-c4a9-4dfb-9a1b-651c9b2e3e09',
  '21662339-afe3-417f-a9dc-e277a9753438', 'dbc881b9-093a-4b71-adac-ab002fc88f3f', '45047aa8-462f-47b3-9a83-c990ceb5c410',
  '8e8631a3-706f-4100-8f5b-9cb309a71f80'
);

update indicators set complementary = true where code = 'SUP_FTI_SCORE';
update indicators set presence_only = true where code = 'ANI_FUR_FREE';
