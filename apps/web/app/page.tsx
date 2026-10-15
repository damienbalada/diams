import { getPublicStats, getVitrines, listEntities, listSectors, type Vitrine } from "@/lib/data";
import { EntitySearch } from "@/components/EntitySearch";
import type { SearchableEntity } from "@/lib/search";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

// Marques et groupes très connus du grand public, choisis à la main (aucun classement de mérite).
const CONNUES = ["nutella", "coca-cola", "president", "zara", "lidl", "nike", "kinder", "evian", "loreal", "mcdonalds", "shein", "ikea"];
// « Les plus recherchées » : classement SIMULÉ tant que le site n'a pas d'utilisateurs ; à remplacer par
// les recherches réellement mesurées. La page le dit en toutes lettres.
const RECHERCHEES = ["shein", "nutella", "mcdonalds", "zara", "carrefour", "danone", "haribo-marque", "amazon"];
// Logos officiels (site de la marque, ou Wikimedia Commons à défaut), copiés dans public/logos.
const LOGOS: Record<string, string> = { "amazon": "/logos/amazon.svg", "carrefour": "/logos/carrefour.png", "coca-cola": "/logos/coca-cola.png", "danone": "/logos/danone.ico", "evian": "/logos/evian.png", "haribo-marque": "/logos/haribo-marque.png", "ikea": "/logos/ikea.svg", "kinder": "/logos/kinder.png", "lidl": "/logos/lidl.svg", "loreal": "/logos/loreal.png", "mcdonalds": "/logos/mcdonalds.png", "nike": "/logos/nike.png", "nutella": "/logos/nutella.jpg", "president": "/logos/president.png", "shein": "/logos/shein.png", "zara": "/logos/zara.svg" };
const TEINTES = ["#6c3bff", "#1f8a4c", "#2563c9", "#b4532a", "#0e7a8a", "#a86a12", "#b8325a", "#4a43c4"];
const teinte = (s: string) => TEINTES[[...s].reduce((a, c) => a + c.charCodeAt(0), 0) % TEINTES.length];

export default async function HomePage() {
  let entities: Awaited<ReturnType<typeof listEntities>> = [];
  let sectorName = new Map<string, string>();
  let stats: { evidence: number; sources: number } | null = null;
  let error: string | null = null;
  let connues: Vitrine[] = [];
  let recherchees: Vitrine[] = [];
  try {
    const [ents, sectors, st, vit] = await Promise.all([
      listEntities(), listSectors(), getPublicStats().catch(() => null),
      getVitrines([...new Set([...CONNUES, ...RECHERCHEES])]).catch(() => [] as Vitrine[]),
    ]);
    entities = ents;
    stats = st;
    const v = new Map(vit.map((x) => [x.slug, x]));
    connues = CONNUES.map((x) => v.get(x)).filter((x): x is Vitrine => !!x);
    recherchees = RECHERCHEES.map((x) => v.get(x)).filter((x): x is Vitrine => !!x);
    sectorName = new Map(sectors.map((x) => [x.id, x.name]));
  } catch (e) {
    error = (e as Error).message;
  }

  const name = (e: any) => String(e.display_name ?? e.legal_name);
  const byName = (a: any, b: any) => name(a).localeCompare(name(b), "fr", { sensitivity: "base" });
  // Groupe propriétaire de chaque entité : la recherche « Unilever » remonte ses marques, parce
  // que c'est là que va l'argent ; il sert aussi de sous-titre dans les résultats.
  const byId = new Map(entities.map((e: any) => [e.id, e]));
  const rootName = (e: any): string | null => {
    let cur: any = e;
    while (cur?.parent_id && byId.get(cur.parent_id)) cur = byId.get(cur.parent_id);
    return cur && cur.slug !== e.slug ? name(cur) : null;
  };
  const searchable: SearchableEntity[] = entities.map((e: any) => ({
    slug: e.slug, name: name(e), is_brand: e.is_brand, group: rootName(e), grade: null,
  }));
  const marques = entities.filter((e: any) => e.is_brand).length;
  const groupes = entities.filter((e: any) => !e.is_brand && !e.parent_id).length;

  // Index par rayon (secteur), par ordre alphabétique : aucun classement.
  const bySector = new Map<string, any[]>();
  for (const e of [...entities].sort(byName)) {
    const k = sectorName.get((e as any).sector_id) ?? "Autres";
    bySector.set(k, [...(bySector.get(k) ?? []), e]);
  }
  const sectorsSorted = [...bySector.entries()].sort((a, b) => a[0].localeCompare(b[0], "fr"));

  const Row = (e: any) => {
    const group = rootName(e);
    return (
      <a key={e.slug} className="ent-row" href={`/entreprise/${e.slug}`}>
        <span className="ent-kind" aria-hidden="true">{e.is_brand ? "🏷️" : "🏢"}</span>
        <span className="ent-main">
          <span className="ent-name">{name(e)}</span>
          {group && <small className="muted">{group}</small>}
        </span>
        <span className="chev" aria-hidden="true">›</span>
      </a>
    );
  };

  const Carte = (v: Vitrine, rang?: number) => (
    <a key={v.slug} className="vit-card" href={`/entreprise/${v.slug}`}>
      <span className="vit-top">
        {rang !== undefined && <span className="vit-rang">{rang}</span>}
        {LOGOS[v.slug] ? (
          <span className="vit-logo vit-logo-img" aria-hidden="true"><img src={LOGOS[v.slug]} alt="" loading="lazy" /></span>
        ) : (
          <span className="vit-logo" aria-hidden="true" style={{ background: teinte(v.name) }}>{v.name.replace(/[^\p{L}\p{N}]/gu, "").slice(0, 1).toUpperCase()}</span>
        )}
        <span>
          <span className="vit-name">{v.name}</span>
          <br />
          <span className="vit-group">{v.group ? `Groupe ${v.group}` : "Société mère"}</span>
        </span>
      </span>
      <span className="vit-chips">
        <span className="vit-chip">{v.faits} fait{v.faits > 1 ? "s" : ""} sourcé{v.faits > 1 ? "s" : ""}</span>
        {v.exploitation && <span className="vit-chip rouge">⚠️ Exploitation animale</span>}
        {v.vegetale && <span className="vit-chip vert">Entièrement végétale</span>}
        {v.sanction && <span className="vit-chip rouge">Sanctionné par une autorité</span>}
      </span>
    </a>
  );

  return (
    <main className="fiche-stack">
      <section className="hero">
        <div className="kicker">La carte d'identité des marques</div>
        <h1>Ce que font vraiment les entreprises que vous faites vivre.</h1>
        <p className="lead">
          Aucune note : des faits. Pour chaque marque, ce que disent les sources officielles, pilier par
          pilier, chacun daté et relié au document qui le prouve, vérifié mot pour mot. Quand on ne sait
          rien, c'est écrit ; à vous de vous faire un avis.
        </p>
        {entities.length > 0 && (
          <div className="stats">
            <div className="stat"><strong>{marques}</strong><span>marques</span></div>
            <div className="stat"><strong>{groupes}</strong><span>groupes et sociétés</span></div>
            {stats && <div className="stat"><strong>{stats.evidence}</strong><span>faits sourcés et vérifiés</span></div>}
          </div>
        )}
      </section>

      {error && (
        <div className="panel" style={{ borderColor: "#6b2222" }}>
          <strong>Connexion à la base non configurée.</strong>
          <p className="muted small">{error}</p>
        </div>
      )}

      <EntitySearch entities={searchable}>
        {connues.length > 0 && (
          <section aria-labelledby="connues">
            <div className="vitrine-head">
              <h2 className="section-title" id="connues">Les plus connues</h2>
              <span className="vitrine-note">Des noms que tout le monde connaît, choisis à la main</span>
            </div>
            <div className="vitrine">{connues.map((v) => Carte(v))}</div>
          </section>
        )}

        {recherchees.length > 0 && (
          <section aria-labelledby="recherchees">
            <div className="vitrine-head">
              <h2 className="section-title" id="recherchees">Les plus recherchées</h2>
              <span className="vitrine-note">Classement simulé : le site vient d'ouvrir, les recherches ne sont pas encore mesurées</span>
            </div>
            <div className="vitrine">{recherchees.map((v, i) => Carte(v, i + 1))}</div>
          </section>
        )}

        {sectorsSorted.length > 0 && (
          <section aria-labelledby="rayons">
            <h2 className="section-title" id="rayons">Parcourir par rayon</h2>
            <div className="rayons-tuiles">
              {sectorsSorted.map(([sector, list], i) => (
                <a key={sector} className="rayon-tuile" href={`#rayon-${i}`}>
                  <strong>{sector}</strong>
                  <span>{list.length} marques et groupes</span>
                </a>
              ))}
            </div>
          </section>
        )}

        <section className="how-grid">
          <div className="how-card">
            <div className="how-num">1</div>
            <strong>Des faits, pas une note</strong>
            <p className="muted small">
              Index Égapro, sortie de Russie, note climat CDP, lobbying déclaré, exploitation animale… chaque
              fait garde l'échelle de sa source. Personne ne les additionne à votre place.
            </p>
          </div>
          <div className="how-card">
            <div className="how-num">2</div>
            <strong>Chaque fait a sa preuve</strong>
            <p className="muted small">
              Rapports déposés auprès des autorités (AMF, SEC), registres publics (Égapro, HATVP), organismes
              reconnus. La citation exacte, la date et le lien sont à un clic.
            </p>
          </div>
          <div className="how-card">
            <div className="how-num">3</div>
            <strong>Les trous sont affichés</strong>
            <p className="muted small">
              « Aucune information » quand rien n'est publié ; « obligatoire, non publié » quand la loi l'exige
              et que la lecture du rapport le confirme. Et toujours : à qui va l'argent.
            </p>
          </div>
        </section>

        <section id="index">
          <h2 className="section-title">Toutes les marques, par rayon</h2>
          <p className="muted small" style={{ margin: "0 0 12px" }}>Par ordre alphabétique : aucun classement.</p>
          {sectorsSorted.map(([sector, list], i) => (
            <details className="pending" key={sector} id={`rayon-${i}`}>
              <summary>
                <span>{sector} <span className="muted">{list.length}</span></span>
              </summary>
              <div className="ent-list">{list.map(Row)}</div>
            </details>
          ))}
        </section>
      </EntitySearch>

      <p className="muted small" style={{ textAlign: "center", marginTop: 8 }}>
        <a href="/methodologie" style={{ textDecoration: "underline" }}>Méthodologie publique et versionnée</a>
        {" · "}
        <a href="/civique" style={{ textDecoration: "underline" }}>Volet civique (votes des partis)</a>
      </p>
    </main>
  );
}
