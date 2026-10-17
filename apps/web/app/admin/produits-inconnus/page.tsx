import { getAdminSupabase } from "@/lib/admin";
import { listerProduitsInconnus, marquerTraite, refuserProduitInconnu } from "@/lib/produits-inconnus-admin";

export const dynamic = "force-dynamic";

const dfr = (d: string) => d.slice(0, 10).split("-").reverse().join("/");

/**
 * Produits non reconnus photographiés par les lecteurs. Les photos servent à trouver la marque et son
 * propriétaire : lire le dos (fabricant, « fabriqué pour… », adresse), puis ajouter la marque par un lot
 * avec une preuve citée (mentions légales, rapport annuel). Rien n'est publié depuis cette page.
 */
export default async function ProduitsInconnusPage() {
  if (!getAdminSupabase()) {
    return (
      <main>
        <h1>Produits inconnus</h1>
        <div className="panel"><strong>Back-office non configuré</strong> : la clé de service manque dans les variables d'environnement.</div>
      </main>
    );
  }
  const items = await listerProduitsInconnus();
  return (
    <main className="fiche-stack">
      <div>
        <a className="muted small" href="/admin/scans">← scans non reconnus</a>
        <div className="row between" style={{ marginTop: 8 }}>
          <h1 style={{ margin: 0 }}>Produits inconnus photographiés</h1>
          <span className="badge">{items.length} en attente</span>
        </div>
        <p className="muted small">
          Lisez la marque sur la face avant et le fabricant au dos (« fabriqué par », « fabriqué pour », adresse).
          Ajoutez ensuite la marque par un lot, avec son propriétaire vérifié dans un registre et une preuve citée.
          Refusez une photo illisible, sans rapport ou qui montre des données personnelles.
        </p>
      </div>
      {items.length === 0 && <div className="panel muted">Aucun envoi en attente.</div>}
      {items.map((p) => (
        <section key={p.id} className="panel" style={{ display: "grid", gap: 12 }}>
          <div className="small">
            <strong>{p.produit ?? "Produit sans nom"}</strong>
            {p.marque ? <> · marque lue par le lecteur : <strong>{p.marque}</strong></> : null}
            {" "}· code <code>{p.code}</code> · {p.alimentaire === true ? "alimentaire" : p.alimentaire === false ? "non alimentaire" : "type non précisé"}
            {" "}· envoyé le {dfr(p.depose)}{p.lieu ? ` · acheté à ${p.lieu}` : ""}{p.scans ? ` · scanné ${p.scans} fois` : ""}
          </div>
          <div className="row" style={{ gap: 12, flexWrap: "wrap", alignItems: "flex-start" }}>
            {p.photos.map((ph) => (
              <figure key={ph.nom} style={{ margin: 0 }}>
                <a href={ph.url} target="_blank" rel="noopener noreferrer">
                  <img src={ph.url} alt={`${ph.nom} du produit ${p.code}`} style={{ maxWidth: 320, maxHeight: 360, borderRadius: 8, border: "1px solid var(--border)" }} />
                </a>
                <figcaption className="small muted">{ph.nom}</figcaption>
              </figure>
            ))}
          </div>
          <form action={marquerTraite} className="row" style={{ gap: 8 }}>
            <input type="hidden" name="id" value={p.id} />
            <input type="text" name="note" placeholder="Ce qui a été fait (ex. : marque X ajoutée, lot 230)" maxLength={500} style={{ flex: 1 }} />
            <button type="submit" className="btn">Marquer traité</button>
          </form>
          <form action={refuserProduitInconnu} className="row" style={{ gap: 8 }}>
            <input type="hidden" name="id" value={p.id} />
            <input type="text" name="note" placeholder="Motif du refus (facultatif)" maxLength={500} style={{ flex: 1 }} />
            <button type="submit" className="btn">Refuser et supprimer les photos</button>
          </form>
        </section>
      ))}
    </main>
  );
}
