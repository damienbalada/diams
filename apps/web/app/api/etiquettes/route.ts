import { NextResponse } from "next/server";
import { enregistrerDepot } from "@/lib/etiquettes-depot";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

/**
 * API de l'appli mobile : dépôt de la photo de l'étiquette d'un produit (formulaire multipart :
 * entity_slug, product_name, purchase_date, purchase_place, consent=on, photo). Mêmes contrôles que le
 * formulaire du site ; rien n'est publié avant la vérification humaine.
 */
export async function POST(req: Request) {
  let fd: FormData;
  try {
    fd = await req.formData();
  } catch {
    return NextResponse.json({ status: "error", message: "Envoi illisible." }, { status: 400 });
  }
  const r = await enregistrerDepot(fd);
  return NextResponse.json(r, { status: r.status === "ok" ? 200 : 400 });
}
