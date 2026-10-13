-- Homonymes entre propriétaires différents : précision ajoutée au nom affiché pour qu'un
-- lecteur ne confonde pas deux marques (contrôle du 13/10/2026).
update entities set display_name = 'Gallia (laits infantiles)', updated_at = now()
 where slug = 'gallia' and coalesce(display_name, legal_name) = 'Gallia';
update entities set display_name = 'Mont Blanc (crèmes desserts)', updated_at = now()
 where slug = 'mont-blanc-desserts' and coalesce(display_name, legal_name) = 'Mont Blanc';
update entities set display_name = 'Vichy (soins dermatologiques)', updated_at = now()
 where slug = 'vichy' and coalesce(display_name, legal_name) = 'Vichy';
