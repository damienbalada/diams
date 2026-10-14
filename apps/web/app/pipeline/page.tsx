import { CONNECTORS, GUARDS } from "@/lib/connectors";

export const dynamic = "force-dynamic";
export const metadata = { title: "Sources et collecte" };

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
          Chaque valeur est chargée et affichée <strong>dans l'échelle de sa source</strong>
          (« 92/100 » pour Égapro, « note A » pour le CDP, un taux en pour cent) : aucune
          conversion, aucune note, aucune addition.
        </p>
      </div>

      <div className="panel">
        <h3>Niveau de rattachement</h3>
        <p className="muted small">
          Gouvernance, fiscalité, climat, lobbying et salaires chez les fournisseurs sont
          publiés au niveau du <strong>groupe</strong> : une marque reprend ces données de
          son groupe, signalées « donnée du groupe » sur sa fiche. L'index Égapro, dû par
          chaque société employeuse, vient du propriétaire direct de la marque (celui
          d'ITM Entreprises pour les marques des Mousquetaires). Ce qui relève du produit
          reste propre à la marque : matières et exploitation animales, transparence textile,
          labels (l'indice de transparence de la mode note directement Gucci). La fiche d'une
          marque affiche toujours le groupe propriétaire et un lien vers sa fiche, parce que c'est lui qui
          reçoit l'argent.
        </p>
      </div>
    </main>
  );
}
