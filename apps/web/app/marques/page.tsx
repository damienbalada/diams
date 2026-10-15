import { listEntities, listSectors } from "@/lib/data";

export const dynamic = "force-dynamic";
export const maxDuration = 60;
export const metadata = { title: "Toutes les marques" };

/**
 * Index par secteur (aucun classement). Une page par secteur : la liste entière (plus de 3 400
 * lignes) d'un seul tenant pesait plusieurs mégaoctets sur téléphone (16/10/2026).
 */
export default async function MarquesPage() {
  const [entities, sectors] = await Promise.all([listEntities(), listSectors()]);
  const n = new Map<string, number>();
  for (const e of entities as any[]) n.set(e.sector_id, (n.get(e.sector_id) ?? 0) + 1);
  const liste = sectors.filter((s) => n.get(s.id)).sort((a, b) => a.name.localeCompare(b.name, "fr"));
  return (
    <main className="fiche-stack">
      <a className="muted small" href="/">← accueil et recherche</a>
      <section>
        <h1 style={{ margin: "8px 0 4px" }}>Toutes les marques</h1>
        <p className="muted small" style={{ margin: "0 0 12px" }}>
          {entities.length} marques et groupes, rangés par secteur. Pour trouver un nom, la recherche de l'accueil est plus rapide.
        </p>
        <nav aria-label="Secteurs" className="rayons-tuiles">
          {liste.map((s) => (
            <a key={s.id} className="rayon-tuile" href={`/marques/${s.code}`}>
              <strong>{s.name}</strong>
              <span>{n.get(s.id)} marques et groupes</span>
            </a>
          ))}
        </nav>
      </section>
    </main>
  );
}
