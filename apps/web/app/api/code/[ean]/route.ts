import { NextResponse } from "next/server";
import { getProduitParCode, listeNomsEntites, type ProduitScanne } from "@/lib/data";
import { phraseRapprochement } from "@/lib/codebarre-texte";
import { avecGenre, codeValide, rapprocher } from "@/lib/codebarre";
import { chargerFiche } from "@/lib/fiche";
import { ficheEnJson } from "@/lib/fiche-json";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

/**
 * API de l'appli mobile : code-barres → produit → marque → fiche, en JSON.
 * Réponses : 200 { trouve: true, fiche } ; 200 { trouve: false, raison, produit? } ; 400 code invalide.
 */
export async function GET(_req: Request, { params }: { params: Promise<{ ean: string }> }) {
  const ean = (await params).ean.replace(/\D/g, "");
  if (!codeValide(ean)) return NextResponse.json({ trouve: false, raison: "Ce numéro n'est pas un code-barres : il faut 8 à 14 chiffres." }, { status: 400 });
  let produit: ProduitScanne | null;
  try {
    produit = await getProduitParCode(ean);
  } catch {
    return NextResponse.json({ trouve: false, code: ean, indisponible: true, raison: "Open Food Facts ne répond pas pour l'instant. Réessayez dans quelques minutes." }, { status: 503 });
  }
  if (!produit) {
    return NextResponse.json({ trouve: false, code: ean, raison: "Ce code n'est pas encore dans Open Food Facts ni Open Beauty Facts : nous ne savons pas quelle marque le vend." });
  }
  const entites = await listeNomsEntites();
  const r = avecGenre(rapprocher(produit.marques, entites, { nomProduit: produit.nom, proprietaire: produit.proprietaire }), entites);
  if (!r) {
    return NextResponse.json({
      trouve: false, code: ean, produit,
      raison: produit.marques.length
        ? `Le produit « ${produit.nom} » porte la marque « ${produit.marques.join(", ")} », qui n'est pas encore dans l'Index.`
        : `Le produit « ${produit.nom} » est connu, mais sa marque n'est pas renseignée dans ${produit.base}.`,
    });
  }
  const f = await chargerFiche(r.slug);
  if (!f) return NextResponse.json({ trouve: false, code: ean, produit, raison: "La fiche de cette marque n'a pas pu être chargée." });
  return NextResponse.json({ trouve: true, fiche: ficheEnJson(r.slug, f.carte, f.proprietaire, { produit, correspondance: r.correspondance, nomLu: r.nomLu, phrase: phraseRapprochement(r, produit.base) }) });
}
