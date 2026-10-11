import { CONNECTORS, GUARDS } from "@/lib/connectors";

export const dynamic = "force-dynamic";

// Page statique de transparence : décrit comment les faits entrent dans DIAMS.
// Aucune donnée externe, aucun accès base — c'est une page d'explication.
// La liste des connecteurs vient de lib/connectors.ts (source unique).

export default function PipelinePage() {
  return (
    <main>
      <h1>Sources et collecte</h1>
      <p className="muted">
        D'où viennent les faits. Chaque source est ingérée par un{" "}
        <strong>connecteur</strong> auditable, dont le code est public. Voici lesquels,
        ce qu'ils produisent, et les garanties qui s'appliquent à tous.{" "}
        <a href="/methodologie" style={{ textDecoration: "underline" }}>Méthodologie complète →</a>
      </p>

      <div className="panel">
        <h3>Trois garanties, pour toutes les sources</h3>
        {GUARDS.map((g) => (
          <div key={g.title} style={{ marginTop: 12 }}>
            <div className="row" style={{ gap: 8, alignItems: "center" }}>
              <span className="badge">garantie</span>
              <strong>{g.title}</strong>
            </div>
            <p className="muted small" style={{ marginTop: 4 }}>{g.body}</p>
          </div>
        ))}
      </div>

      <div className="panel">
        <h3>Connecteurs</h3>
        <div className="prose">
          <table>
            <thead>
              <tr>
                <th>Connecteur</th>
                <th>Pilier</th>
                <th>Ce qu'il produit</th>
                <th>Source</th>
                <th>Niveau</th>
              </tr>
            </thead>
            <tbody>
              {CONNECTORS.map((c) => (
                <tr key={c.name}>
                  <td><strong>{c.name}</strong></td>
                  <td>{c.pillar}</td>
                  <td>{c.produces}</td>
                  <td>{c.source}</td>
                  <td>{c.level}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="muted small" style={{ marginTop: 12 }}>
          Les indicateurs quantitatifs (taux effectif, présence en paradis fiscaux)
          sont chargés en <strong>valeur brute</strong> : c'est le moteur qui calcule
          le percentile intra-secteur et applique la direction (« plus haut = mieux »
          ou l'inverse). Normaliser à la main fausserait la comparaison sectorielle.
        </p>
      </div>

      <div className="panel">
        <h3>Niveau de rattachement</h3>
        <p className="muted small">
          Gouvernance, fiscalité et climat sont publiés au niveau du{" "}
          <strong>groupe</strong>. Certains benchmarks notent directement une{" "}
          <strong>marque</strong> (le Fashion Transparency Index note Gucci). Une marque
          est notée sur <strong>ses propres preuves</strong>, sans hériter de celles de
          son groupe ; sa fiche affiche toujours le groupe propriétaire et sa note,
          parce que c'est lui qui reçoit l'argent.
        </p>
      </div>
    </main>
  );
}
