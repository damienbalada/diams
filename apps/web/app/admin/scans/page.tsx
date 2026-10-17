import { getAdminSupabase } from "@/lib/admin";
import { listerScansNonReconnus, parMarque } from "@/lib/scans";

export const dynamic = "force-dynamic";

const dfr = (d: string) => d.slice(0, 10).split("-").reverse().join("/");
const MOTIF: Record<string, string> = {
  code_inconnu: "Code absent des bases ouvertes",
  marque_absente: "Marque pas encore dans l'Index",
  marque_non_renseignee: "Marque non renseignée dans la base ouverte",
};

/**
 * Codes-barres scannés que l'Index ne reconnaît pas, regroupés par marque : la liste des marques à
 * ajouter en priorité (propriétaire vérifié dans un registre, comme toujours).
 */
export default async function ScansPage() {
  if (!getAdminSupabase()) {
    return (
      <main>
        <h1>Scans non reconnus</h1>
        <div className="panel"><strong>Back-office non configuré</strong> : la clé de service manque dans les variables d'environnement.</div>
      </main>
    );
  }
  const scans = await listerScansNonReconnus();
  const marques = parMarque(scans);
  const autres = scans.filter((s) => s.motif !== "marque_absente");
  return (
    <main className="fiche-stack">
      <div>
        <a className="muted small" href="/admin/revue">← file de revue des preuves</a>
        <h1 style={{ margin: "8px 0 0" }}>Scans non reconnus</h1>
        <p className="muted small">
          Chaque code scanné sans résultat est compté ici (aucune donnée sur la personne qui scanne). Les marques
          les plus demandées sont à ajouter d'abord, avec leur propriétaire vérifié dans un registre.
        </p>
      </div>

      <section className="panel" style={{ display: "grid", gap: 8 }}>
        <h2 style={{ margin: 0 }}>Marques à ajouter ({marques.length})</h2>
        {marques.length === 0 && <p className="muted small">Aucune pour l'instant.</p>}
        {marques.length > 0 && (
          <table className="small" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Marque lue</th><th align="right">Scans</th><th align="right">Produits</th><th align="left">Exemple</th></tr></thead>
            <tbody>
              {marques.map((m) => (
                <tr key={m.marque} style={{ borderTop: "1px solid var(--line, #e7e3f6)" }}>
                  <td><strong>{m.marque || "(sans nom)"}</strong></td><td align="right">{m.scans}</td><td align="right">{m.codes}</td><td className="muted">{m.exemple}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel" style={{ display: "grid", gap: 8 }}>
        <h2 style={{ margin: 0 }}>Codes sans marque lisible ({autres.length})</h2>
        <p className="muted small">Absents des bases ouvertes, ou sans marque renseignée : à compléter dans Open Food Facts, Open Beauty Facts ou Open Products Facts.</p>
        {autres.length > 0 && (
          <table className="small" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Code</th><th align="left">Motif</th><th align="left">Produit</th><th align="right">Scans</th><th align="left">Dernier</th></tr></thead>
            <tbody>
              {autres.map((s) => (
                <tr key={s.code} style={{ borderTop: "1px solid var(--line, #e7e3f6)" }}>
                  <td><code>{s.code}</code></td><td>{MOTIF[s.motif]}</td><td className="muted">{s.produit ?? "—"}</td><td align="right">{s.nombre}</td><td>{dfr(s.dernier)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
