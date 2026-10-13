import { getAllScores, listSectors, type EntityScore } from "@/lib/data";
import { rankBySector, sectorAnchor, type SectorInfo } from "@/lib/ranking";

export const dynamic = "force-dynamic";
export const metadata = { title: "Classement par secteur" };

const gradeColor: Record<string, string> = {
  A: "var(--a)", B: "var(--b)", C: "var(--c)", D: "var(--d)", E: "var(--e)",
};
const pct = (x: number) => `${Math.round(x * 100)}%`;
const frYearMonth = (iso: string | null) => {
  if (!iso) return "—";
  const [y, m] = iso.split("-");
  return `${m}/${y}`;
};

function Table({ rows, ranked = true }: { rows: EntityScore[]; ranked?: boolean }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="rank-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
        <colgroup>
          {ranked && <col style={{ width: "6%" }} />}
          <col />
          <col style={{ width: "12%" }} />
          <col className="col-hide-mobile" style={{ width: "11%" }} />
          <col style={{ width: "13%" }} />
          <col className="col-hide-mobile" style={{ width: "14%" }} />
        </colgroup>
        <thead>
          <tr className="muted small">
            {ranked && <th style={{ textAlign: "left", padding: "6px 4px" }}>#</th>}
            <th style={{ textAlign: "left", padding: "6px 4px" }}>Entité</th>
            <th style={{ textAlign: "center", padding: "6px 4px" }}>Note</th>
            <th className="col-hide-mobile" style={{ textAlign: "right", padding: "6px 4px" }}>Sur 100</th>
            <th style={{ textAlign: "right", padding: "6px 4px" }}>Fiabilité</th>
            <th className="col-hide-mobile" style={{ textAlign: "right", padding: "6px 4px" }}>Mis à jour</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.slug} style={{ borderTop: "1px solid var(--border)" }}>
              {ranked && <td className="muted small" style={{ padding: "8px 4px" }}>{i + 1}</td>}
              <td style={{ padding: "8px 4px" }}>
                <a href={`/entreprise/${r.slug}`} style={{ fontWeight: 600 }}>{r.name}</a>
                {r.group && <span className="muted small"> · {r.group}</span>}
              </td>
              <td style={{ textAlign: "center", padding: "8px 4px" }}>
                {ranked ? (
                  <span className={`grade sm grade-${r.grade}`} style={{ display: "inline-grid" }}>{r.grade}</span>
                ) : (
                  <span className="muted small">—</span>
                )}
              </td>
              <td style={{ textAlign: "right", padding: "8px 4px" }} className={`col-hide-mobile ${ranked ? "" : "muted"}`}>{ranked ? pct(r.score) : "—"}</td>
              <td className="muted" style={{ textAlign: "right", padding: "8px 4px" }}>{pct(r.confidence)}</td>
              <td className="muted small col-hide-mobile" style={{ textAlign: "right", padding: "8px 4px" }}>{frYearMonth(r.last_observed)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function ClassementPage() {
  let scores: EntityScore[] = [];
  let sectors: SectorInfo[] = [];
  let error: string | null = null;
  try {
    [scores, sectors] = await Promise.all([getAllScores(), listSectors()]);
  } catch (e) {
    error = (e as Error).message;
  }
  // Règle 6 : un tableau par secteur (mêmes indicateurs applicables), groupes et
  // marques séparés. On ne classe QUE les entités au-dessus du seuil de fiabilité :
  // une note bâtie sur trop peu de preuves n'est ni bonne ni mauvaise.
  const { ranked, empty } = rankBySector(scores, sectors);
  const byConfidence = (a: EntityScore, b: EntityScore) => b.confidence - a.confidence;
  const unranked = scores.filter((s) => !s.publishable).sort(byConfidence);

  return (
    <main>
      <h1>Classement</h1>
      <p className="muted small">
        Par secteur, trié par note (profil « Équilibré »). On ne compare que des entités
        évaluées sur les mêmes indicateurs : une banque et un fabricant de boissons ne se
        classent pas l'un contre l'autre. Seules les entités dont la
        <strong> fiabilité dépasse 30 %</strong> sont classées.
      </p>

      {error && (
        <div className="panel" style={{ borderColor: "#6b2222" }}>
          <strong>Chargement impossible.</strong>
          <p className="muted small">{error}</p>
        </div>
      )}

      {ranked.map((s) => (
        <section className="panel" key={s.sector.id || s.sector.code} id={sectorAnchor(s.sector)}>
          <div className="row between wrap" style={{ gap: 8 }}>
            <h2 style={{ margin: 0, fontSize: 18 }}>{s.sector.name}</h2>
            <span className="muted small">
              {s.groups.length + s.brands.length} classée(s)
              {s.unranked > 0 && ` · ${s.unranked} en attente de données`}
            </span>
          </div>
          {s.groups.length > 0 && (
            <>
              {s.brands.length > 0 && <h3 className="small muted" style={{ margin: "12px 0 0" }}>Groupes</h3>}
              <Table rows={s.groups} />
            </>
          )}
          {s.brands.length > 0 && (
            <>
              <h3 className="small muted" style={{ margin: "12px 0 0" }}>Marques</h3>
              <Table rows={s.brands} />
            </>
          )}
        </section>
      ))}

      {empty.length > 0 && (
        <details className="panel" style={{ borderStyle: "dashed" }}>
          <summary className="small">
            <strong>Secteurs sans entité classée pour l'instant</strong> ({empty.length})
          </summary>
          <p className="muted small" style={{ margin: "10px 0 0" }}>
            {empty.map((s) => `${s.sector.name} (${s.unranked})`).join(" · ")}
          </p>
        </details>
      )}

      {unranked.length > 0 && (
        <details className="panel" style={{ borderStyle: "dashed" }}>
          <summary className="small">
            <strong>Non classées — données insuffisantes</strong> ({unranked.length})
          </summary>
          <p className="muted small" style={{ margin: "10px 0" }}>
            Pas assez de preuves pour attribuer une note défendable : fiabilité sous 30 %, ou
            moins de 30 % du socle d'indicateurs documenté (base de la note, voir la
            méthodologie). Ce n'est pas un jugement négatif — c'est un manque de transparence
            de l'entité, ou une couverture encore partielle.
          </p>
          <Table rows={unranked} ranked={false} />
        </details>
      )}
    </main>
  );
}
