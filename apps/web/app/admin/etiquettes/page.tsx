import { getAdminSupabase } from "@/lib/admin";
import { listerEtiquettesEnAttente, validerEtiquette, refuserEtiquette } from "@/lib/etiquettes";

export const dynamic = "force-dynamic";

const dfr = (d: string) => d.slice(0, 10).split("-").reverse().join("/");

/**
 * Vérification des étiquettes envoyées par les lecteurs. Rien n'est publié sans qu'un éditeur ait
 * recopié la liste d'ingrédients en la relisant contre la photo. Valider rend la photo publique
 * (pièce justificative) et ajoute le produit à la fiche de la marque.
 */
export default async function EtiquettesPage() {
  if (!getAdminSupabase()) {
    return (
      <main>
        <h1>Étiquettes à vérifier</h1>
        <div className="panel"><strong>Back-office non configuré</strong> : la clé de service manque dans les variables d'environnement.</div>
      </main>
    );
  }
  const items = await listerEtiquettesEnAttente();
  return (
    <main className="fiche-stack">
      <div>
        <a className="muted small" href="/admin/revue">← file de revue des preuves</a>
        <div className="row between" style={{ marginTop: 8 }}>
          <h1 style={{ margin: 0 }}>Étiquettes à vérifier</h1>
          <span className="badge">{items.length} en attente</span>
        </div>
        <p className="muted small">
          Recopiez la liste d'ingrédients <strong>telle qu'elle figure sur la photo</strong>, mot pour mot, allergènes compris.
          Les ingrédients d'origine animale sont repérés à la validation, comme pour les fiches des sites de marques.
          « Végétal » ne s'inscrit que si l'étiquette porte une mention de la marque ou un label d'un tiers : recopiez-la.
          Refusez une photo illisible, d'un autre produit ou sans rapport.
        </p>
      </div>
      {items.length === 0 && <div className="panel muted">Aucune étiquette en attente.</div>}
      {items.map((e) => (
        <section key={e.id} className="panel" style={{ display: "grid", gap: 12 }}>
          <div className="small">
            <strong>{e.produit}</strong> · marque <a href={`/entreprise/${e.marque.slug}`}>{e.marque.nom}</a>
            {" "}· déposée le {dfr(e.depose)}{e.date ? ` · achetée le ${dfr(e.date)}` : ""}{e.lieu ? ` (${e.lieu})` : ""}
          </div>
          {e.photo && (
            <a href={e.photo} target="_blank" rel="noopener noreferrer">
              <img src={e.photo} alt={`Étiquette de ${e.produit}`} style={{ maxWidth: "100%", maxHeight: 520, borderRadius: 8, border: "1px solid var(--border)" }} />
            </a>
          )}
          <form action={validerEtiquette} className="form-stack">
            <input type="hidden" name="id" value={e.id} />
            <label className="field">
              <span className="small">Nom du produit (corrigez-le d'après l'étiquette si besoin)</span>
              <input type="text" name="product_name" defaultValue={e.produit} maxLength={200} />
            </label>
            <label className="field">
              <span className="small">Liste des ingrédients, recopiée mot pour mot</span>
              <textarea name="transcription" rows={6} required minLength={3} placeholder="Ingrédients : …" />
            </label>
            <label className="field">
              <span className="small">Mention « végétal », « vegan » ou label lu sur l'étiquette <em className="muted">(facultatif, recopiée)</em></span>
              <input type="text" name="vegetal" maxLength={200} placeholder="Ex. : 100 % végétal ; V-Label" />
            </label>
            <button type="submit" className="btn">Valider et publier</button>
          </form>
          <form action={refuserEtiquette} className="row" style={{ gap: 8 }}>
            <input type="hidden" name="id" value={e.id} />
            <input type="text" name="note" placeholder="Motif du refus (facultatif)" maxLength={500} style={{ flex: 1 }} />
            <button type="submit" className="btn">Refuser</button>
          </form>
        </section>
      ))}
    </main>
  );
}
