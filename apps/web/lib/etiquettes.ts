"use server";

import { revalidatePath } from "next/cache";
import { getAdminSupabase, requireAdmin } from "./admin";
import { analyserIngredients } from "./ingredients";
import { aujourdhui, enregistrerDepot, type DepotState } from "./etiquettes-depot";

/** Étiquettes photographiées par la communauté : dépôt (public), vérification (administration). */

/** Dépôt d'une photo d'étiquette depuis la fiche d'une marque. Aucune donnée personnelle demandée. */
export async function deposerEtiquette(_prev: DepotState, fd: FormData): Promise<DepotState> {
  return enregistrerDepot(fd);
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
