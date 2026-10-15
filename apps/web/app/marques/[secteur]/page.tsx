import { listEntities, listSectors } from "@/lib/data";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function generateMetadata({ params }: { params: Promise<{ secteur: string }> }) {
  const { secteur } = await params;
  const s = (await listSectors().catch(() => [])).find((x) => x.code === secteur);
  return { title: s ? `${s.name} : toutes les marques` : "Secteur introuvable" };
}

/** Les marques et groupes d'un secteur, par ordre alphabétique (aucun classement). */
export default async function SecteurPage({ params, searchParams }: { params: Promise<{ secteur: string }>; searchParams: Promise<{ lettre?: string }> }) {
  const { secteur } = await params;
  const { lettre: lettreDemandee } = await searchParams;
  const [entities, sectors] = await Promise.all([listEntities(), listSectors()]);
  const s = sectors.find((x) => x.code === secteur);
  if (!s) {
    return (
      <main>
        <a className="muted small" href="/marques">← tous les secteurs</a>
        <div className="panel" style={{ marginTop: 12 }}>Secteur introuvable : {secteur}</div>
      </main>
    );
  }
  const name = (e: any) => String(e.display_name ?? e.legal_name);
  const byId = new Map(entities.map((e: any) => [e.id, e]));
  const rootName = (e: any): string | null => {
    let cur: any = e;
    while (cur?.parent_id && byId.get(cur.parent_id)) cur = byId.get(cur.parent_id);
    return cur && cur.slug !== e.slug ? name(cur) : null;
  };
  const tous = entities
    .filter((e: any) => e.sector_id === s.id)
    .sort((a: any, b: any) => name(a).localeCompare(name(b), "fr", { sensitivity: "base" }));
  // Initiale sans accent ; chiffres et signes regroupés sous « # ».
  const initiale = (e: any) => {
    const c = name(e).normalize("NFKD").replace(/[̀-ͯ]/g, "").charAt(0).toUpperCase();
    return /[A-Z]/.test(c) ? c : "#";
  };
  // Au-delà de 200 noms, une page par lettre (la liste entière pèse trop lourd sur téléphone).
  const parLettre = tous.length > 200;
  const lettres = [...new Set(tous.map(initiale))].sort((a, b) => (a === "#" ? 1 : b === "#" ? -1 : a.localeCompare(b)));
  const lettre = parLettre ? (lettres.includes((lettreDemandee ?? "").toUpperCase()) ? lettreDemandee!.toUpperCase() : lettres[0]) : null;
  const list = lettre ? tous.filter((e) => initiale(e) === lettre) : tous;
  return (
    <main className="fiche-stack">
      <a className="muted small" href="/marques">← tous les secteurs</a>
      <section>
        <h1 style={{ margin: "8px 0 4px" }}>{s.name}</h1>
        <p className="muted small" style={{ margin: "0 0 12px" }}>
          {tous.length} marques et groupes, par ordre alphabétique : aucun classement.
        </p>
        {parLettre && (
          <nav aria-label="Initiale" className="lettres">
            {lettres.map((l) => (
              <a key={l} href={`/marques/${s.code}?lettre=${encodeURIComponent(l)}`} aria-current={l === lettre ? "page" : undefined} className={l === lettre ? "lettre on" : "lettre"}>{l}</a>
            ))}
          </nav>
        )}
        {lettre && <h2 className="section-title" style={{ marginTop: 12 }}>{lettre} <span className="muted">{list.length}</span></h2>}
        <div className="ent-list">
          {list.map((e: any) => {
            const g = rootName(e);
            return (
              <a key={e.slug} className="ent-row" href={`/entreprise/${e.slug}`}>
                <span className="ent-kind" aria-hidden="true">{e.is_brand ? "🏷️" : "🏢"}</span>
                <span className="ent-main">
                  <span className="ent-name">{name(e)}</span>
                  {g && <small className="muted">{g}</small>}
                </span>
                <span className="chev" aria-hidden="true">›</span>
              </a>
            );
          })}
        </div>
      </section>
    </main>
  );
}
