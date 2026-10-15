import type { Rapprochement } from "./codebarre";

/** Comment la marque a été reconnue, en une phrase (page web et appli). */
export function phraseRapprochement(r: Rapprochement, base: string): string {
  const quoi = r.groupe ? "Groupe" : "Marque";
  if (r.correspondance === "exacte") return `${quoi} inscrit${r.groupe ? "" : "e"} sur le produit : « ${r.nomLu} »`;
  if (r.correspondance === "approchee") return `${quoi} reconnu${r.groupe ? "" : "e"} d'après le nom inscrit sur le produit : « ${r.nomLu} » (rapprochement approché, à vérifier)`;
  return r.marqueNonSuivie
    ? `La marque « ${r.marqueNonSuivie} » n'est pas encore dans l'Index ; voici la fiche de « ${r.nomLu} », indiqué comme son propriétaire par ${base} (base collaborative, lien non vérifié)`
    : `Fiche du propriétaire indiqué par ${base} : « ${r.nomLu} » (base collaborative, lien non vérifié)`;
}
