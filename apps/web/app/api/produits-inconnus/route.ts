import { NextResponse } from "next/server";
import { enregistrerProduitInconnu } from "@/lib/produits-inconnus";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

/**
 * API de l'appli mobile : photos d'un produit non reconnu (formulaire multipart : code, photo_face,
 * photo_dos, photo_ingredients, product_name, brand_name, alimentaire=oui|non, purchase_place, consent=on).
 * Rien n'est publié : un éditeur identifie la marque et son propriétaire à partir des photos.
 */
export async function POST(req: Request) {
  let fd: FormData;
  try {
    fd = await req.formData();
  } catch {
    return NextResponse.json({ status: "error", message: "Envoi illisible." }, { status: 400 });
  }
  const r = await enregistrerProduitInconnu(fd);
  return NextResponse.json(r, { status: r.status === "ok" ? 200 : 400 });
}
