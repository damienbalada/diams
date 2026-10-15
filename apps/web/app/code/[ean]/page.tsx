import { redirect } from "next/navigation";
import { getProduitParCode, listeNomsEntites, type ProduitScanne } from "@/lib/data";
import { phraseRapprochement } from "@/lib/codebarre-texte";
import { avecGenre, codeValide, rapprocher } from "@/lib/codebarre";
import { chargerFiche } from "@/lib/fiche";
import { CarteIdentite } from "@/components/CarteIdentite";

export const dynamic = "force-dynamic";
export const maxDuration = 60;
export const metadata = { title: "Produit scanné" };

/** Fiche d'un produit par son code-barres : produit → marque inscrite → fiche de la marque. */
export default async function CodeProduitPage({ params, searchParams }: { params: Promise<{ ean: string }>; searchParams: Promise<{ c?: string }> }) {
  let { ean } = await params;
  // Formulaire de /code : /code/aller?c=…
  if (ean === "aller") {
    const { c } = await searchParams;
    redirect(`/code/${encodeURIComponent((c ?? "").replace(/\D/g, ""))}`);
  }
  ean = ean.replace(/\D/g, "");
  if (!codeValide(ean)) return <Inconnu code={ean} raison="Ce numéro n'est pas un code-barres : il faut 8 à 14 chiffres." />;
  let produit: ProduitScanne | null;
  try {
    produit = await getProduitParCode(ean);
  } catch {
    return <Inconnu code={ean} raison="Open Food Facts ne répond pas pour l'instant. Réessayez dans quelques minutes." />;
  }
  if (!produit) return <Inconnu code={ean} raison="Ce code n'est pas encore dans Open Food Facts ni Open Beauty Facts : nous ne savons pas quelle marque le vend." />;
  const entites = await listeNomsEntites();
  const r = avecGenre(rapprocher(produit.marques, entites, { nomProduit: produit.nom, proprietaire: produit.proprietaire }), entites);
  if (!r) {
    return (
      <Inconnu
        code={ean}
        raison={produit.marques.length
          ? `Le produit « ${produit.nom} » porte la marque « ${produit.marques.join(", ")} », qui n'est pas encore dans l'Index.`
          : `Le produit « ${produit.nom} » est connu, mais sa marque n'est pas renseignée dans ${produit.base}.`}
      />
    );
  }
  const f = await chargerFiche(r.slug);
  if (!f) return <Inconnu code={ean} raison="La fiche de cette marque n'a pas pu être chargée." />;
  return <CarteIdentite {...f} scan={{ produit, correspondance: r.correspondance, nomLu: r.nomLu, phrase: phraseRapprochement(r, produit.base) }} />;
}

function Inconnu({ code, raison }: { code: string; raison: string }) {
  return (
    <main className="fiche-stack">
      <a className="muted small" href="/code">← autre code-barres</a>
      <section className="panel">
        <h1 style={{ margin: "0 0 8px" }}>Ce produit n'est pas encore dans l'Index</h1>
        <p style={{ margin: "0 0 8px" }}>{raison}</p>
        <p className="muted small" style={{ margin: "0 0 12px" }}>Code lu : {code || "aucun"}</p>
        <p className="small" style={{ margin: 0 }}>
          <a className="ci-lien" href="/">Chercher la marque par son nom</a>
        </p>
      </section>
    </main>
  );
}
