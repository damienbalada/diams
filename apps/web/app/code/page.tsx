export const metadata = { title: "Chercher par code-barres" };

/** Saisie d'un code-barres (l'appli mobile le lit avec l'appareil photo et ouvre la même page). */
export default function CodePage() {
  return (
    <main className="fiche-stack">
      <a className="muted small" href="/">← accueil</a>
      <section className="panel">
        <h1 style={{ margin: "0 0 6px" }}>Chercher par code-barres</h1>
        <p className="muted small" style={{ margin: 0 }}>
          Les chiffres sous le code-barres du produit (8 à 13 chiffres). La marque est lue dans Open Food Facts ou Open Beauty Facts,
          bases collaboratives, puis rapprochée des marques de l'Index.
        </p>
        <form className="code-form" action="/code/aller" method="get">
          <label htmlFor="code" className="small" style={{ flexBasis: "100%" }}>Code-barres</label>
          <input id="code" name="c" inputMode="numeric" pattern="[0-9]{8,14}" required placeholder="3017620422003" autoComplete="off" />
          <button type="submit">Voir la fiche</button>
        </form>
      </section>
    </main>
  );
}
