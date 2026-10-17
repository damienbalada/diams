// Analyse d'une liste d'ingrédients (étiquette recopiée) : ingrédients d'origine animale certaine,
// hors mentions de traces et de « sans … », et ingrédients d'origine possiblement animale (signalés,
// jamais conclusifs). Même dictionnaire que pipeline/outils_collecte/ingredients.py (17/10/2026) ; les
// limites de mot tiennent compte des lettres accentuées (« œufs »).

const D = "(?<!\\p{L})"; // début de mot
const F = "(?!\\p{L})";  // fin de mot

const ANIMAL = [
  "lait(?! (?:de |d['’] ?)(?:coco|soja|riz|amandes?|avoine|noisettes?|cajou|[ée]peautre|ch[èe]vre v[ée]g))(?!s? v[ée]g[ée]ta)",
  "lactos[ée]rum", "lactose", "petit-lait", "babeurre",
  "cr[èe]me(?! de (?:marrons?|coco|riz|soja|balsamique))(?! glacée végétale)",
  "beurre(?! de (?:cacao|karit[ée]|cacahu[èe]tes?|arachide|amande|noix|coco|cajou))",
  "fromages?", "cas[ée]ine?s?", "cas[ée]inates?", "prot[ée]ines? de lait", "mati[èe]re grasse laiti[èe]re", "yaourt",
  `œufs?${F}`, `oeufs?${F}`, "jaunes? d.[œo]e?ufs?", "blancs? d.[œo]e?ufs?", "ovoproduits?",
  "g[ée]latine", `miel${F}`, "cire d.abeille", "gel[ée]e royale",
  "viandes?", `porc${F}`, "b[œo]e?uf", `veau${F}`, "poulet", "dinde", "volaille", "canard", "agneau", "jambon", "lardons?",
  "bacon", "saucisses?", "chorizo", `gras de${F}`, "saindoux", "graisse (?:animale|de (?:porc|canard|b[œo]e?uf|oie))", "suif",
  "poissons?", "anchois", `thon${F}`, "saumon", "sardines?", "maquereaux?", "crevettes?", "moules?", "crustac[ée]s",
  "carmin", "cochenille", `E ?120${F}`, "gomme[- ]laque", `E ?904${F}`, `E ?901${F}`, `E ?441${F}`, "lanoline", "collag[èe]ne", "pr[ée]sure",
];
const ANIMAL_RE = new RegExp(`${D}(?:${ANIMAL.join("|")})`, "giu");
const DOUTEUX_RE = new RegExp(`${D}(?:vitamine D3?|ar[ôo]mes? naturels?|ar[ôo]mes?${F}|E ?542|E ?631|E ?627|E ?920|L-cyst[ée]ine|ac[ée]ides gras|mono- et diglyc[ée]rides|E ?471|st[ée]arate)`, "giu");
const SANS_RE = new RegExp(`${D}sans (?:lait|lactose|[œo]e?ufs?|g[ée]latine|viande|ingr[ée]dients? d.origine animale)${F}`, "giu");
const TRACES_RE = /(?:peut contenir|traces? (?:éventuelles? )?de|contient (?:des )?traces|fabriqué dans un atelier)[^.]*\.?/giu;

export type StatutProduit = "ingredient_animal" | "aucun_ingredient_animal_declare" | "vegetal_declare" | "vegetal_certifie";

const cle = (s: string) => s.replace(/œ/g, "oe").normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[sx]+$/, "");

/** Ingrédients animaux (une forme par ingrédient), ingrédients douteux et statut, d'après la liste lue. */
export function analyserIngredients(liste: string): { animaux: string[]; douteux: string[]; statut: StatutProduit } {
  const propre = liste.replace(TRACES_RE, " ").replace(SANS_RE, " ");
  const formes = new Map<string, string>();
  for (const m of propre.matchAll(ANIMAL_RE)) {
    const f = m[0].toLowerCase();
    if (!formes.has(cle(f))) formes.set(cle(f), f);
  }
  const douteux = [...new Set([...propre.matchAll(DOUTEUX_RE)].map((m) => m[0].toLowerCase()))].sort();
  const animaux = [...formes.values()].sort();
  return { animaux, douteux, statut: animaux.length ? "ingredient_animal" : "aucun_ingredient_animal_declare" };
}
