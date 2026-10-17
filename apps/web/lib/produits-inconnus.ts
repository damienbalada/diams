import "server-only";
import { getAdminSupabase } from "./admin";

/**
 * Produits non reconnus photographiés par les lecteurs : face avant (obligatoire), dos (fabricant,
 * « fabriqué pour… ») et ingrédients (produits alimentaires). Les photos restent privées tant qu'un
 * éditeur ne les a pas traitées. Aucune donnée personnelle n'est demandée.
 */

export interface EnvoiState { status: "ok" | "error"; message?: string }

const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const PHOTOS = [["photo_face", "face"], ["photo_dos", "dos"], ["photo_ingredients", "ingredients"]] as const;

function photoValide(p: FormDataEntryValue | null): p is File {
  return p instanceof File && p.size > 0;
}

export async function enregistrerProduitInconnu(fd: FormData): Promise<EnvoiState> {
  const code = String(fd.get("code") ?? "").replace(/\D/g, "");
  const nom = String(fd.get("product_name") ?? "").trim().slice(0, 200) || null;
  const marque = String(fd.get("brand_name") ?? "").trim().slice(0, 120) || null;
  const lieu = String(fd.get("purchase_place") ?? "").trim().slice(0, 200) || null;
  const alim = fd.get("alimentaire");
  const alimentaire = alim === "oui" ? true : alim === "non" ? false : null;
  if (!/^\d{8,14}$/.test(code)) return { status: "error", message: "Code-barres illisible." };
  if (fd.get("consent") !== "on") return { status: "error", message: "Cochez l'autorisation : sans elle, les photos ne peuvent pas servir." };
  if (!photoValide(fd.get("photo_face"))) return { status: "error", message: "Ajoutez au moins la photo de la face avant du produit." };
  for (const [champ] of PHOTOS) {
    const p = fd.get(champ);
    if (!photoValide(p)) continue;
    if (!TYPES.has(p.type)) return { status: "error", message: "Format accepté : JPEG, PNG ou WebP." };
    if (p.size > 5 * 1024 * 1024) return { status: "error", message: "Photo trop lourde (5 Mo au plus)." };
  }
  const sb = getAdminSupabase();
  if (!sb) return { status: "error", message: "L'envoi de photos n'est pas configuré sur ce déploiement." };
  const dossier = `${code}/${crypto.randomUUID()}`;
  const chemins: Record<string, string | null> = { photo_face: null, photo_dos: null, photo_ingredients: null };
  for (const [champ, nomFichier] of PHOTOS) {
    const p = fd.get(champ);
    if (!photoValide(p)) continue;
    const ext = p.type === "image/png" ? "png" : p.type === "image/webp" ? "webp" : "jpg";
    const chemin = `${dossier}/${nomFichier}.${ext}`;
    const up = await sb.storage.from("produits-a-verifier").upload(chemin, p, { contentType: p.type, upsert: false });
    if (up.error) {
      const deja = Object.values(chemins).filter(Boolean) as string[];
      if (deja.length) await sb.storage.from("produits-a-verifier").remove(deja);
      return { status: "error", message: "Les photos n'ont pas pu être enregistrées. Réessayez plus tard." };
    }
    chemins[champ] = chemin;
  }
  const { error } = await sb.from("product_submissions").insert({
    code, product_name: nom, brand_name: marque, alimentaire, purchase_place: lieu, consent: true, ...chemins,
  });
  if (error) {
    await sb.storage.from("produits-a-verifier").remove(Object.values(chemins).filter(Boolean) as string[]);
    return { status: "error", message: "L'envoi n'a pas pu être enregistré. Réessayez plus tard." };
  }
  return { status: "ok" };
}
