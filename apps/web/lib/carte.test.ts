// Tests de la carte d'identité (logique pure).
// Lancer : node --test --experimental-strip-types apps/web/lib/carte.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { construireCarte, resumeGroupe, valeurCourte, type IndicateurEntree, type PreuveEntree } from "./carte.ts";

const dims = [{ code: "ANI", name: "Bien-être animal" }, { code: "LAB", name: "Travail" }, { code: "ENV", name: "Environnement" }];
const ind = (code: string, dim: string, extra: Partial<IndicateurEntree> = {}): IndicateurEntree =>
  ({ code, name: code, dimension_code: dim, unit: null, ...extra });
const preuve = (code: string, extra: Partial<PreuveEntree> = {}): PreuveEntree => ({
  indicator_code: code, tier: "regulatory", value_numeric: null, observed_on: "2026-03-01", specificity: 0,
  source_url: "https://exemple.fr", source_name: "Source", excerpt: "« … »", ...extra,
});

test("exploitation animale non documentée : présumée, jamais « aucune information »", () => {
  const c = construireCarte({ entity: { slug: "m", name: "M" }, applicableIndicators: [ind("ANI_EXPLOITATION", "ANI")], evidence: [], dimensions: dims });
  assert.equal(c.piliers[0].faits[0].etat, "presume");
  assert.equal(c.piliers[0].cle?.code, "ANI_EXPLOITATION");
});

test("obligation sans lecture du rapport : pas de rouge ; après lecture : obligatoire absent", () => {
  const p = { entity: { slug: "g", name: "G" }, dimensions: dims, evidence: [],
    applicableIndicators: [ind("LAB_GENDER_PAYGAP", "LAB", { mandatory: true, mandatory_regimes: ["CSRD"] })] };
  assert.equal(construireCarte(p).piliers[0].faits[0].etat, "aucune_info");
  const lu = construireCarte(p, [{ indicator_code: "LAB_GENDER_PAYGAP", outcome: "absence_confirmee", detail: "lu", checked_on: "2026-10-15" }]);
  assert.equal(lu.piliers[0].faits[0].etat, "obligatoire_absent");
  assert.equal(lu.piliers[0].cle?.etat, "obligatoire_absent");
  const autre = construireCarte(p, [{ indicator_code: "LAB_GENDER_PAYGAP", outcome: "autre_forme", detail: "par zone", checked_on: "2026-10-15" }]);
  assert.equal(autre.piliers[0].faits[0].etat, "autre_forme");
});

test("la preuve propre à l'entité passe devant celle du groupe ; la valeur garde l'échelle de la source", () => {
  const c = construireCarte({ entity: { slug: "m", name: "M" }, dimensions: dims, applicableIndicators: [ind("LAB_EGAPRO_INDEX", "LAB", { unit: "score/100" })],
    evidence: [preuve("LAB_EGAPRO_INDEX", { value_numeric: "92.0", specificity: -1, inherited_from: "Groupe" }),
               preuve("LAB_EGAPRO_INDEX", { value_numeric: 88, specificity: 0, observed_on: "2025-03-01" })] });
  const f = c.piliers[0].faits[0];
  assert.equal(f.valeur, "Index Égapro : 88/100");
  assert.equal(f.preuve?.reprisDe, null);
});

test("aucune information : la recherche faite est rapportée", () => {
  const c = construireCarte({ entity: { slug: "g", name: "G" }, dimensions: dims, evidence: [],
    applicableIndicators: [ind("ENV_CDP_CLIMATE", "ENV")] },
    [{ indicator_code: "ENV_CDP_CLIMATE", outcome: "non_trouvee", detail: "Cherché, non trouvé : absente de la liste publique complète des notes CDP 2025", checked_on: "2026-10-15" }]);
  assert.match(c.piliers[0].faits[0].note ?? "", /liste publique CDP/);
});

test("solidité d'un pilier : d'après les seules sources utilisées", () => {
  const c = construireCarte({ entity: { slug: "g", name: "G" }, dimensions: dims,
    applicableIndicators: [ind("ENV_CDP_CLIMATE", "ENV"), ind("ENV_GHG_TREND", "ENV", { unit: "%/an" }), ind("ENV_X", "ENV")],
    evidence: [preuve("ENV_CDP_CLIMATE", { tier: "audited_ngo", excerpt: "climat — note A." }), preuve("ENV_GHG_TREND", { value_numeric: -7.3 })] });
  assert.equal(c.piliers[0].solidite, "reconnue");
  assert.equal(c.piliers[0].documentes, 2);
  assert.equal(c.piliers[0].total, 3);
  assert.equal(c.piliers[0].cle?.code, "ENV_GHG_TREND");
});

test("valeurs courtes", () => {
  assert.equal(valeurCourte("ANI_EXPLOITATION", null, preuve("x", { excerpt: "… — recours à l'exploitation animale (lait)." })), "Vend des produits issus de l'exploitation animale : lait");
  assert.equal(valeurCourte("LAB_GENDER_PAYGAP", "%", preuve("x", { value_numeric: -8 })), "8 % en faveur des femmes");
  assert.equal(valeurCourte("ENV_GHG_TREND", "%/an", preuve("x", { value_numeric: -7.3 })), "Émissions en baisse de 7,3 % par an");
});

test("animal à trois niveaux : niveau des faits et résumé du groupe", () => {
  const c = construireCarte({ entity: { slug: "m", name: "M" }, dimensions: dims,
    applicableIndicators: [ind("ANI_EXPLOITATION", "ANI"), ind("ANI_OFFRE_VEGETALE", "ANI")],
    evidence: [preuve("ANI_OFFRE_VEGETALE", { excerpt: "« Big Chocodark Vegan »" })] }, [], { estMarque: true });
  const fs = c.piliers[0].faits;
  assert.equal(fs.find((f) => f.code === "ANI_EXPLOITATION")?.niveau, "marque");
  assert.equal(fs.find((f) => f.code === "ANI_EXPLOITATION")?.etat, "presume");
  assert.equal(fs.find((f) => f.code === "ANI_OFFRE_VEGETALE")?.niveau, "produit");
  // Un produit végétal ne rend pas la marque végétale : le fait clé reste l'exploitation présumée.
  assert.equal(c.piliers[0].cle?.code, "ANI_EXPLOITATION");
  const r = resumeGroupe([
    { slug: "a", nom: "A", etat: "exploitation", offreVegetale: true },
    { slug: "b", nom: "B", etat: "vegetale", offreVegetale: true },
    { slug: "c", nom: "C", etat: "non_documentee", offreVegetale: false },
  ]);
  assert.deepEqual(r, { total: 3, exploitation: 1, vegetale: 1, nonDocumentee: 1, offreVegetale: 1 });
});

test("trois niveaux pour tout le site : groupe repris, marque propre, produits", () => {
  const c = construireCarte({ entity: { slug: "m", name: "M" }, dimensions: dims, ownership_chain: ["M", "G"],
    applicableIndicators: [ind("ENV_CDP_CLIMATE", "ENV", { group_level: true }), ind("SUP_FTI_SCORE", "SUP"), ind("ENV_SBTI_VALIDATED", "ENV", { group_level: true }), ind("INV_SOLIDARITY_LABEL", "INV")],
    evidence: [preuve("ENV_CDP_CLIMATE", { excerpt: "note A", inherited_from: "G" }), preuve("SUP_FTI_SCORE", { value_numeric: 40 })] });
  const n = (code: string) => c.piliers.flatMap((p) => p.faits).find((f) => f.code === code)?.niveau;
  assert.equal(n("ENV_CDP_CLIMATE"), "groupe");      // repris du groupe
  assert.equal(n("SUP_FTI_SCORE"), "marque");        // preuve propre à la marque
  assert.equal(n("ENV_SBTI_VALIDATED"), "groupe");   // vide, indicateur publié par le groupe
  assert.equal(n("INV_SOLIDARITY_LABEL"), "produit");
  // Fiche d'un groupe : tout ce qui n'est pas « produit » est de niveau groupe.
  const g = construireCarte({ entity: { slug: "g", name: "G" }, dimensions: dims,
    applicableIndicators: [ind("SUP_FTI_SCORE", "SUP")], evidence: [preuve("SUP_FTI_SCORE", { value_numeric: 40 })] }, [], { estMarque: false });
  assert.equal(g.piliers[0].faits[0].niveau, "groupe");
});

test("raison d'un indicateur vide : signalement, dispense, obligation, classement externe, rien d'obligatoire", async () => {
  const { raisonVide: rv } = await import("./carte.ts");
  const raisonVide = (f: any) => rv(f).join(" · ");
  assert.match(raisonVide({ code: "GOV_SANCTIONS", obligation: [], exemption: null }), /Rien trouvé/);
  assert.match(raisonVide({ code: "ENV_SCOPE3_DISCLOSED", obligation: [], exemption: "Déclarée non matérielle" }), /pas d'obligation : Déclarée non matérielle/);
  assert.match(raisonVide({ code: "SUP_VIGILANCE_PLAN", obligation: ["Loi vigilance"], exemption: null }), /obligatoire \(Loi vigilance\)/);
  assert.match(raisonVide({ code: "SUP_FTI_SCORE", obligation: [], exemption: null }), /Non évalué/);
  assert.match(raisonVide({ code: "PLA_RECYCLED", obligation: [], exemption: null }), /aucune obligation légale/);
});

test("sanctions et Russie : le fait lui-même, pas « Documenté »", () => {
  const s = valeurCourte("GOV_SANCTIONS", "controverse", preuve("x", { excerpt: "Autorité de la concurrence, décision n° 23-D-15 du 29/12/2023 : « … » ; « Cofigeo : 566 000 euros » — entente ; amende de 0,566 M€ (sanction)" }));
  assert.equal(s, "Sanctionné par l'Autorité de la concurrence (2023) : amende de 0,566 M€");
  const c = valeurCourte("GOV_SANCTIONS", "controverse", preuve("x", { excerpt: "CNIL (Commission nationale de l'informatique et des libertés), actualité du 03/09/2025 : « … » — amende de 150 millions d’euros" }));
  assert.equal(c, "Sanctionné par la CNIL (2025) : amende de 150 millions d’euros");
  assert.equal(valeurCourte("GEO_RUSSIA_EXIT", "status", preuve("x", { excerpt: "KSE Institute, base « Leave Russia » : « Storck » — activité poursuivie en Russie" })), "Russie : activité poursuivie");
});

test("matières animales et tests : interdiction, exigence et objectif ne se confondent pas", () => {
  const v = (code: string, excerpt: string) => valeurCourte(code, "policy", preuve(code, { excerpt }));
  assert.equal(v("ANI_DOWN_RDS", "« does not accept the use of virgin down or feathers in our products »"), "Duvet et plumes neufs exclus (seulement recyclés)");
  assert.equal(v("ANI_DOWN_RDS", "objectifs à l'horizon 2026 : « … certifiés Responsible Down standard (RDS) … »"), "Objectif de duvet recyclé ou certifié (norme RDS, sans plumage à vif)");
  assert.equal(v("ANI_WOOL_MULESING", "« All virgin sheep wool must be certified in accordance with the Responsible Wool Standard (RWS) »"), "Laine neuve certifiée sans mulesing (norme RWS) exigée");
  assert.equal(v("ANI_EXOTIC_SKINS", "« does not accept the use of exotic skins or skins from wild animals »"), "Peaux exotiques exclues");
  assert.equal(v("ANI_EXOTIC_SKINS", "« le pôle ne commercialise que des peaux exotiques dont la provenance est … auditée »"), "Peaux exotiques : approvisionnement certifié ou audité (pas d'interdiction)");
  assert.equal(v("ANI_LEATHER_TRACE", "« en 2025, l’ensemble des tanneries … et 83 % étaient certifiées LWG »"), "83 % des tanneries du groupe certifiées par le Leather Working Group");
  assert.equal(v("ANI_TESTING", "Annuaire des marques approuvées Leaping Bunny de Cruelty Free International : « … »"), "Certifiée sans tests sur les animaux (Leaping Bunny)");
  assert.equal(v("ANI_TESTING", "« mettre fin aux tests sur animaux pour les produits finis dès 1989 »"), "Arrêt des tests sur les animaux déclaré (sans certification du groupe)");
});

test("sanction en dollars australiens : devise écrite en clair", () => {
  const s = valeurCourte("GOV_SANCTIONS", "controverse", preuve("x", { excerpt: "Cour fédérale d'Australie, jugement du 12/08/2022 : « … » — amende civile ; amende de 60 MA$ (sévérité 0,5)." }));
  assert.equal(s, "Sanctionné par la Cour fédérale d'Australie (2022) : amende de 60 M$ australiens");
});

test("allégation trompeuse : article devant la SEC et le Bureau de la concurrence", () => {
  const v = (excerpt: string) => valeurCourte("ENV_GREENWASHING", "controverse", preuve("x", { excerpt }));
  assert.equal(v("SEC (autorité américaine des marchés financiers), communiqué 2024-122 du 10/09/2024 : « … » — amende civile de 1,5 M$ pour …"), "Allégations écologiques trompeuses relevées par la SEC (2024) : amende de 1,5 M$");
  assert.equal(v("Bureau de la concurrence du Canada, communiqué du 06/01/2022 (en anglais) : « … »"), "Allégations écologiques trompeuses relevées par le Bureau de la concurrence du Canada (2022)");
});

test("matières animales : politique sans certification et double interdiction", () => {
  const v = (code: string, excerpt: string) => valeurCourte(code, "policy", preuve(code, { excerpt }));
  assert.equal(v("ANI_WOOL_MULESING", "« refusing to procure Merino wool … mulesing » — politique publiée, sans certification de la laine exigée."), "Laine issue du mulesing refusée (politique, sans certification)");
  assert.equal(v("ANI_ANGORA_MOHAIR", "« Mohair (Angora goat hair), Angora (Angora rabbit hair) » — angora et mohair exclus."), "Angora et mohair exclus");
  assert.equal(v("ANI_DOWN_RDS", "« … are RDS (Responsible Down Standard) certified as of the end of December 2019 » — ateliers certifiés RDS."), "Duvet certifié (norme RDS) exigé");
});

test("duvet : politique sans certification", () => {
  const s = valeurCourte("ANI_DOWN_RDS", "policy", preuve("x", { excerpt: "« Suppliers must not supply down harvested from live birds … » — politique publiée, sans certification du duvet exigée." }));
  assert.equal(s, "Plumage à vif exclu (politique, sans certification)");
});

test("sanction partagée entre deux filiales : le total n'est pas sous-estimé", () => {
  const s = valeurCourte("GOV_SANCTIONS", "controverse", preuve("x", { excerpt: "Cour fédérale d'Australie, ordonnance du 26/07/2023 : « … » — amende de 10 MA$ pour chacune des deux filiales (sévérité 0,5)." }));
  assert.equal(s, "Sanctionné par la Cour fédérale d'Australie (2023) : amende de 10 M$ australiens pour chacune de deux filiales");
});
