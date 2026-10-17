"use server";

import { revalidatePath } from "next/cache";
import { getAdminSupabase, requireAdmin } from "./admin";
import { analyserIngredients } from "./ingredients";

/** Étiquettes photographiées par la communauté : dépôt (public), vérification (administration). */

export interface DepotState { status: "idle" | "ok" | "error"; message?: string }

const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const aujourdhui = () => new Date().toISOString().slice(0, 10);

/** Dépôt d'une photo d'étiquette depuis la fiche d'une marque. Aucune donnée personnelle demandée. */
export async function deposerEtiquette(_prev: DepotState, fd: FormData): Promise<DepotState> {
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

export interface EtiquetteEnAttente {
  id: string; produit: string; marque: { slug: string; nom: string }; photo: string | null;
  date: string | null; lieu: string | null; depose: string;
}

/** Dépôts en attente, avec un lien temporaire (1 h) vers la photo privée. */
export async function listerEtiquettesEnAttente(): Promise<EtiquetteEnAttente[]> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  const { data, error } = await sb.from("label_submissions")
    .select("id, product_name, photo_path, purchase_date, purchase_place, created_at, entities(slug, display_name, legal_name)")
    .eq("status", "pending").order("created_at").limit(50);
  if (error) throw new Error(error.message);
  return Promise.all((data ?? []).map(async (r: any) => {
    const s = await sb.storage.from("etiquettes-a-verifier").createSignedUrl(r.photo_path, 3600);
    return {
      id: r.id, produit: r.product_name, marque: { slug: r.entities?.slug, nom: r.entities?.display_name ?? r.entities?.legal_name },
      photo: s.data?.signedUrl ?? null, date: r.purchase_date, lieu: r.purchase_place, depose: r.created_at,
    };
  }));
}

/**
 * Validation : la liste d'ingrédients a été recopiée contre la photo. La photo passe dans l'espace
 * public (pièce justificative) et le produit entre dans la table products, approuvé.
 */
export async function validerEtiquette(fd: FormData): Promise<void> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  const id = String(fd.get("id"));
  const liste = String(fd.get("transcription") ?? "").trim();
  const nom = String(fd.get("product_name") ?? "").trim();
  const vegetal = String(fd.get("vegetal") ?? "").trim();
  if (liste.length < 3) throw new Error("Recopiez la liste d'ingrédients telle qu'elle figure sur la photo.");
  const { data: d, error } = await sb.from("label_submissions").select("*").eq("id", id).eq("status", "pending").maybeSingle();
  if (error || !d) throw new Error("Dépôt introuvable ou déjà traité.");
  const dep: any = d;
  const fichier = await sb.storage.from("etiquettes-a-verifier").download(dep.photo_path);
  if (fichier.error || !fichier.data) throw new Error("Photo introuvable.");
  const up = await sb.storage.from("etiquettes").upload(dep.photo_path, fichier.data, { contentType: fichier.data.type || "image/jpeg", upsert: true });
  if (up.error) throw new Error(up.error.message);
  const url = sb.storage.from("etiquettes").getPublicUrl(dep.photo_path).data.publicUrl;
  const a = analyserIngredients(liste);
  // Végétal : seulement si l'étiquette porte une mention de la marque ou un label d'un tiers, recopiés ici.
  const statut = a.statut === "aucun_ingredient_animal_declare" && vegetal
    ? (/label|vegan society|certifi/i.test(vegetal) ? "vegetal_certifie" : "vegetal_declare")
    : a.statut;
  const { data: prod, error: e2 } = await sb.from("products").upsert({
    entity_id: dep.entity_id, name: nom || dep.product_name, source_url: url, ingredients: liste,
    animal_ingredients: a.animaux, doubtful_ingredients: a.douteux, status: statut,
    vegetal_proof: statut.startsWith("vegetal") ? `Mention de l'étiquette : « ${vegetal} »` : null,
    observed_on: dep.purchase_date ?? aujourdhui(), reviewer: "admin:etiquette-relue", review_status: "approved",
    source_kind: "etiquette", purchase_date: dep.purchase_date, purchase_place: dep.purchase_place,
  }, { onConflict: "entity_id,source_url" }).select("id").single();
  if (e2) throw new Error(e2.message);
  await sb.from("label_submissions").update({
    status: "approved", transcription: liste, reviewed_at: new Date().toISOString(), product_id: (prod as any).id,
  }).eq("id", id);
  await sb.storage.from("etiquettes-a-verifier").remove([dep.photo_path]);
  revalidatePath("/admin/etiquettes");
}

/** Refus (photo illisible, autre produit, image sans rapport) : la photo privée est supprimée. */
export async function refuserEtiquette(fd: FormData): Promise<void> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  const id = String(fd.get("id"));
  const { data } = await sb.from("label_submissions").select("photo_path").eq("id", id).maybeSingle();
  await sb.from("label_submissions").update({
    status: "rejected", review_note: String(fd.get("note") ?? "").slice(0, 500) || null, reviewed_at: new Date().toISOString(),
  }).eq("id", id);
  if (data) await sb.storage.from("etiquettes-a-verifier").remove([(data as any).photo_path]);
  revalidatePath("/admin/etiquettes");
}
