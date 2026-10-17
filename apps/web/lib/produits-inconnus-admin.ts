"use server";

import { revalidatePath } from "next/cache";
import { getAdminSupabase, requireAdmin } from "./admin";

/** Traitement, par un éditeur, des photos de produits non reconnus envoyées depuis l'appli. */

export interface ProduitInconnu {
  id: string; code: string; produit: string | null; marque: string | null; alimentaire: boolean | null; lieu: string | null;
  depose: string; photos: { nom: string; url: string }[]; scans: number;
}

/** Envois en attente, avec des liens temporaires (1 h) vers les photos privées et le nombre de scans du code. */
export async function listerProduitsInconnus(): Promise<ProduitInconnu[]> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  const { data, error } = await sb.from("product_submissions").select("*").eq("status", "pending").order("created_at").limit(100);
  if (error) throw new Error(error.message);
  const codes = [...new Set((data ?? []).map((r: any) => r.code))];
  const { data: sc } = codes.length ? await sb.from("scans_non_reconnus").select("code, nombre").in("code", codes) : { data: [] as any[] };
  const nb = new Map((sc ?? []).map((s: any) => [s.code, s.nombre]));
  return Promise.all((data ?? []).map(async (r: any) => {
    const photos: { nom: string; url: string }[] = [];
    for (const [champ, nom] of [["photo_face", "Face avant"], ["photo_dos", "Dos (fabricant)"], ["photo_ingredients", "Ingrédients"]] as const) {
      if (!r[champ]) continue;
      const s = await sb.storage.from("produits-a-verifier").createSignedUrl(r[champ], 3600);
      if (s.data?.signedUrl) photos.push({ nom, url: s.data.signedUrl });
    }
    return {
      id: r.id, code: r.code, produit: r.product_name, marque: r.brand_name, alimentaire: r.alimentaire, lieu: r.purchase_place,
      depose: r.created_at, photos, scans: Number(nb.get(r.code) ?? 0),
    };
  }));
}

/**
 * Traité : la marque et son propriétaire ont été identifiés et ajoutés par un lot (preuve citée), ou la
 * marque était déjà dans l'Index. La note dit ce qui a été fait ; les photos privées sont gardées.
 */
export async function marquerTraite(fd: FormData): Promise<void> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  await sb.from("product_submissions").update({
    status: "traite", review_note: String(fd.get("note") ?? "").slice(0, 500) || null, reviewed_at: new Date().toISOString(),
  }).eq("id", String(fd.get("id")));
  revalidatePath("/admin/produits-inconnus");
}

/** Refus (photo illisible, sans rapport, données personnelles visibles) : les photos privées sont supprimées. */
export async function refuserProduitInconnu(fd: FormData): Promise<void> {
  await requireAdmin();
  const sb = getAdminSupabase();
  if (!sb) throw new Error("SUPABASE_SERVICE_ROLE_KEY manquante.");
  const id = String(fd.get("id"));
  const { data } = await sb.from("product_submissions").select("photo_face, photo_dos, photo_ingredients").eq("id", id).maybeSingle();
  await sb.from("product_submissions").update({
    status: "rejected", review_note: String(fd.get("note") ?? "").slice(0, 500) || null, reviewed_at: new Date().toISOString(),
  }).eq("id", id);
  const chemins = data ? [(data as any).photo_face, (data as any).photo_dos, (data as any).photo_ingredients].filter(Boolean) : [];
  if (chemins.length) await sb.storage.from("produits-a-verifier").remove(chemins);
  revalidatePath("/admin/produits-inconnus");
}
