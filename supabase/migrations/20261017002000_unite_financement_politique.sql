-- Financement politique (FEC) : les montants sont en dollars des États-Unis, pas en euros.
update indicators set unit = '$' where code = 'GEO_POL_FINANCING' and unit = '€';
