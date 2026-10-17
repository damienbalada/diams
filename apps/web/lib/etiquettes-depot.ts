import "server-only";
import { getAdminSupabase } from "./admin";

/** Dépôt d'une photo d'étiquette (commun au formulaire du site et à l'API de l'appli mobile). */

export interface DepotState { status: "idle" | "ok" | "error"; message?: string }

const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
export const aujourdhui = () => new Date().toISOString().slice(0, 10);

/** Dépôt d'une photo d'étiquette depuis la fiche d'une marque. Aucune donnée personnelle demandée. */
export async function enregistrerDepot(fd: FormData): Promise<DepotState> {
  const slug = String(fd.get("entity_slug") ?? "");
  const nom = String(fd.get("product_name") ?? "").trim();
  const date = String(fd.get("purchase_date") ?? "").trim() || null;
  const lieu = String(fd.get("purchase_place") ?? "").trim().slice(0, 200) || null;
  const accord = fd.get("consent") === "on";
  const photo = fd.get("photo");
  if (nom.length < 2 || nom.length > 200) return { status: "error", message: "Indiquez le nom du produit (2 à 200 caractères)." };
  if (!accord) return { status: "error", message: "Cochez la case : sans votre accord, la photo ne peut pas servir de pièce justificative." };
  if (date && (!/^\d{4}-\d{2}-\d{2}$/.test(date) || date > aujourdhui())) return { status: "error", message: "La date d'achat n'est pas valable." };
  if (!(photo instanceof File) || photo.size === 0) return { status: "error", message: "Ajoutez la photo de l'étiquette." };
  if (!TYPES.has(photo.type)) return { status: "error", message: "Format accepté : JPEG, PNG ou WebP." };
  if (photo.size > 5 * 1024 * 1024) return { status: "error", message: "Photo trop lourde (5 Mo au plus)." };
  const sb = getAdminSupabase();
  if (!sb) return { status: "error", message: "Le dépôt d'étiquettes n'est pas configuré sur ce déploiement." };
  const { data: ent } = await sb.from("entities").select("id").eq("slug", slug).maybeSingle();
  if (!ent) return { status: "error", message: "Marque inconnue." };
  const ext = photo.type === "image/png" ? "png" : photo.type === "image/webp" ? "webp" : "jpg";
  const chemin = `${slug}/${crypto.randomUUID()}.${ext}`;
  const up = await sb.storage.from("etiquettes-a-verifier").upload(chemin, photo, { contentType: photo.type, upsert: false });
  if (up.error) return { status: "error", message: "La photo n'a pas pu être enregistrée. Réessayez plus tard." };
  const { error } = await sb.from("label_submissions").insert({
    entity_id: (ent as any).id, product_name: nom, photo_path: chemin, purchase_date: date, purchase_place: lieu, consent: true,
  });
  if (error) {
    await sb.storage.from("etiquettes-a-verifier").remove([chemin]);
    return { status: "error", message: "Le dépôt n'a pas pu être enregistré. Réessayez plus tard." };
  }
  return { status: "ok" };
}

