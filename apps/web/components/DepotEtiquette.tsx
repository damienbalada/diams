"use client";

import { useActionState, useState, startTransition } from "react";
import { deposerEtiquette, type DepotState } from "@/lib/etiquettes";

const INITIAL: DepotState = { status: "idle" };

/** Réduit la photo dans le navigateur (2 000 px au plus, JPEG) : envoi rapide et sous la limite du serveur. */
async function reduire(f: File): Promise<Blob> {
  try {
    const img = await createImageBitmap(f);
    const k = Math.min(1, 2000 / Math.max(img.width, img.height));
    const c = document.createElement("canvas");
    c.width = Math.round(img.width * k);
    c.height = Math.round(img.height * k);
    c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
    const b = await new Promise<Blob | null>((ok) => c.toBlob(ok, "image/jpeg", 0.85));
    return b ?? f;
  } catch {
    return f; // format que le navigateur ne sait pas lire : envoyé tel quel, le serveur tranche
  }
}

/**
 * Dépôt de la photo de l'étiquette d'un produit de la marque. La liste d'ingrédients est recopiée et
 * relue contre la photo avant toute publication ; la photo devient alors la pièce justificative.
 */
export function DepotEtiquette({ slug, marque }: { slug: string; marque: string }) {
  const [state, action, pending] = useActionState(deposerEtiquette, INITIAL);
  const [prep, setPrep] = useState(false);

  async function envoyer(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const photo = fd.get("photo");
    if (photo instanceof File && photo.size > 0) {
      setPrep(true);
      fd.set("photo", new File([await reduire(photo)], "etiquette.jpg", { type: "image/jpeg" }));
      setPrep(false);
    }
    startTransition(() => action(fd));
  }

  return (
    <details className="ci-depot">
      <summary>📷 Ajouter l'étiquette d'un produit {marque}</summary>
      {state.status === "ok" ? (
        <p className="small">
          ✅ Merci. La photo est enregistrée, en attente de vérification. Nous recopierons la liste d'ingrédients et la relirons
          contre votre photo avant de publier quoi que ce soit ; la photo servira alors de pièce justificative.
        </p>
      ) : (
        <form onSubmit={envoyer} className="form-stack">
          <input type="hidden" name="entity_slug" value={slug} />
          <p className="small muted" style={{ margin: 0 }}>
            Photographiez la <strong>liste des ingrédients</strong>, lisible et en entier, avec le nom du produit si possible.
            Aucune donnée personnelle n'est demandée.
          </p>
          <label className="field">
            <span className="small">Photo de l'étiquette</span>
            <input type="file" name="photo" accept="image/jpeg,image/png,image/webp" capture="environment" required />
          </label>
          <label className="field">
            <span className="small">Nom du produit</span>
            <input type="text" name="product_name" minLength={2} maxLength={200} required placeholder="Ex. : Pâte à tartiner noisettes 400 g" />
          </label>
          <label className="field">
            <span className="small">Date d'achat <em className="muted">(facultatif)</em></span>
            <input type="date" name="purchase_date" />
          </label>
          <label className="field">
            <span className="small">Lieu d'achat <em className="muted">(facultatif : enseigne et ville)</em></span>
            <input type="text" name="purchase_place" maxLength={200} placeholder="Ex. : Carrefour Market, Lyon" />
          </label>
          <label className="small" style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <input type="checkbox" name="consent" required />
            <span>J'ai pris cette photo moi-même et j'autorise sa publication et sa réutilisation libre (licence Creative Commons CC BY 4.0) comme pièce justificative.</span>
          </label>
          {state.status === "error" && <p className="small" style={{ color: "#b0261a", margin: 0 }}>{state.message}</p>}
          <button type="submit" className="btn" disabled={pending || prep}>{prep ? "Préparation de la photo…" : pending ? "Envoi…" : "Envoyer l'étiquette"}</button>
        </form>
      )}
    </details>
  );
}
