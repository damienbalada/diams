import { getAllScores, getPublicStats, listEntities, listSectors } from "@/lib/data";
import { rankBySector, sectorAnchor, type SectorRanking } from "@/lib/ranking";
import { EntitySearch } from "@/components/EntitySearch";
import type { SearchableEntity } from "@/lib/search";

export const dynamic = "force-dynamic";

const pct = (x: number) => `${Math.round(x * 100)} %`;

export default async function HomePage() {
  let entities: Awaited<ReturnType<typeof listEntities>> = [];
  let grades = new Map<string, string>();
  let ranked: SectorRanking[] = [];
  let stats: { evidence: number; sources: number } | null = null;
  let error: string | null = null;
  try {
    const [ents, scores, sectors, st] = await Promise.all([
      listEntities(), getAllScores(), listSectors(), getPublicStats().catch(() => null),
    ]);
    entities = ents;
    stats = st;
    ranked = rankBySector(scores, sectors).ranked;
    // Pas de lettre sous le seuil de fiabilité (Règle 5) : une note mal
    // documentée ne doit pas se lire comme un verdict.
    grades = new Map(scores.filter((s) => s.publishable).map((s) => [s.slug, s.grade]));
  } catch (e) {
    error = (e as Error).message;
  }

  const name = (e: any) => e.display_name ?? e.legal_name;
  const byName = (a: any, b: any) =>
    String(name(a)).localeCompare(String(name(b)), "fr", { sensitivity: "base" });

  // Groupe propriétaire de chaque entité : sert à la recherche (« Unilever »
  // doit remonter ses marques) et de sous-titre dans les résultats.
  const byId = new Map(entities.map((e: any) => [e.id, e]));
  const rootName = (e: any): string | null => {
    let cur: any = e;
    while (cur?.parent_id && byId.get(cur.parent_id)) cur = byId.get(cur.parent_id);
    return cur && cur.slug !== e.slug ? String(name(cur)) : null;
  };

  const searchable: SearchableEntity[] = entities.map((e: any) => ({
    slug: e.slug,
    name: String(name(e)),
    is_brand: e.is_brand,
    group: rootName(e),
    grade: grades.get(e.slug) ?? null,
  }));

  const rated = entities.filter((e: any) => grades.has(e.slug)).sort(byName);
  const pending = entities.filter((e: any) => !grades.has(e.slug)).sort(byName);

  const Row = (e: any) => {
    const g = grades.get(e.slug);
    const group = rootName(e);
    return (
      <a key={e.slug} className="ent-row" href={`/entreprise/${e.slug}`}>
        {g ? (
          <span className={`grade sm grade-${g}`}>{g}</span>
        ) : (
          <span className="grade sm grade-none" title="Pas encore notée">—</span>
        )}
        <span className="ent-main">
          <span className="ent-name">{name(e)}</span>
          {group && <small className="muted">{group}</small>}
        </span>
        <span className="chev" aria-hidden="true">›</span>
      </a>
    );
  };

  return (
    <main className="fiche-stack">
      <section className="hero">
        <div className="kicker">Score éthique des entreprises</div>
        <h1>Ce que font vraiment les entreprises que vous faites vivre.</h1>
        <p className="lead">
          Chaque note s'appuie sur des preuves officielles, datées et vérifiées mot pour mot
          dans les documents déposés par les entreprises. Quand les données manquent, on le dit,
          au lieu de deviner.
        </p>
        {rated.length > 0 && (
          <div className="stats">
            <div className="stat"><strong>{rated.length}</strong><span>entreprises notées</span></div>
            <div className="stat"><strong>{entities.length}</strong><span>marques et groupes suivis</span></div>
            {stats && <div className="stat"><strong>{stats.evidence}</strong><span>preuves sourcées</span></div>}
            <div className="stat"><strong>{ranked.length}</strong><span>secteurs comparables</span></div>
          </div>
        )}
      </section>

      {error && (
        <div className="panel" style={{ borderColor: "#6b2222" }}>
          <strong>Connexion Supabase non configurée.</strong>
          <p className="muted small">Renseignez <code>.env</code> (voir <code>.env.example</code>). {error}</p>
        </div>
      )}

      <EntitySearch entities={searchable}>
        {ranked.length > 0 && (
          <section>
            <div className="row between wrap" style={{ alignItems: "baseline" }}>
              <h2 className="section-title">Les mieux notées, secteur par secteur</h2>
              <a className="small muted" href="/classement" style={{ textDecoration: "underline" }}>Classement complet →</a>
            </div>
            <p className="muted small" style={{ margin: "0 0 12px" }}>
              On ne compare que des entreprises du même secteur : une banque et un fabricant de
              boissons ne sont pas jugés sur les mêmes critères.
            </p>
            <div className="sector-grid">
              {ranked.map((s) => {
                const rows = [...s.groups, ...s.brands].sort((a, b) => b.score - a.score).slice(0, 3);
                const total = s.groups.length + s.brands.length;
                return (
                  <a key={s.sector.code} className="sector-card" href={`/classement#${sectorAnchor(s.sector)}`}>
                    <div className="sector-head">
                      <strong>{s.sector.name}</strong>
                      <span className="muted small">{total} notée{total > 1 ? "s" : ""}</span>
                    </div>
                    {rows.map((r, i) => (
                      <div className="podium" key={r.slug}>
                        <span className="rank muted">{i + 1}</span>
                        <span className={`grade xs grade-${r.grade}`}>{r.grade}</span>
                        <span className="podium-name">{r.name}</span>
                        <span className="muted small">{pct(r.score)}</span>
                      </div>
                    ))}
                  </a>
                );
              })}
            </div>
          </section>
        )}

        <section className="how-grid">
          <div className="how-card">
            <div className="how-num">1</div>
            <strong>Des preuves officielles</strong>
            <p className="muted small">
              Rapports annuels déposés auprès des autorités de marché (AMF, SEC), registres publics
              (Égapro, HATVP), ONG auditées. Chaque chiffre renvoie à son document et à sa date.
            </p>
          </div>
          <div className="how-card">
            <div className="how-num">2</div>
            <strong>Le silence se paie, s'il est illégal</strong>
            <p className="muted small">
              Une donnée que la loi oblige à publier et qui manque compte zéro. Une donnée facultative
              absente ne pénalise pas : les petites entreprises ne sont pas condamnées d'avance.
            </p>
          </div>
          <div className="how-card">
            <div className="how-num">3</div>
            <strong>La fiabilité, affichée à part</strong>
            <p className="muted small">
              Chaque note s'accompagne d'un indice de fiabilité. Sous 30 %, pas de note : trop peu de
              preuves pour un verdict défendable.
            </p>
          </div>
        </section>

        <section>
          <h2 className="section-title">Toutes les entreprises</h2>
          {rated.length > 0 && (
            <>
              <h3 className="list-title">Notées <span className="muted">{rated.length}</span></h3>
              <div className="ent-list">{rated.map(Row)}</div>
            </>
          )}
          {pending.length > 0 && (
            <details className="pending">
              <summary>
                <span>En attente de données <span className="muted">{pending.length}</span></span>
                <span className="muted small">pas encore assez de preuves publiées pour une note</span>
              </summary>
              <div className="ent-list">{pending.map(Row)}</div>
            </details>
          )}
        </section>
      </EntitySearch>

      <p className="muted small" style={{ textAlign: "center", marginTop: 8 }}>
        <a href="/methodologie" style={{ textDecoration: "underline" }}>Méthodologie publique et versionnée</a>
        {" · "}
        <a href="/civique" style={{ textDecoration: "underline" }}>DIAMS Civique (votes des partis)</a>
      </p>
    </main>
  );
}
