import { getAdminSupabase } from "@/lib/admin";
import type { ProduitScanne } from "@/lib/data";

export type MotifNonReconnu = "code_inconnu" | "marque_absente" | "marque_non_renseignee";

/**
 * Relève un code-barres que l'Index ne reconnaît pas (compteur + dates), pour choisir les marques à
 * ajouter. Aucune donnée personnelle. Ne bloque jamais la réponse : une erreur est simplement ignorée.
 */
export async function noterScanNonReconnu(code: string, motif: MotifNonReconnu, produit: ProduitScanne | null): Promise<void> {
  const sb = getAdminSupabase();
  if (!sb) return;
  try {
    await sb.rpc("noter_scan_non_reconnu", {
      p_code: code, p_motif: motif, p_produit: produit?.nom ?? null, p_marques: produit?.marques ?? [], p_base: produit?.base ?? null,
    });
  } catch {
    /* le relevé est un outil éditorial : son échec ne doit pas gêner le lecteur */
  }
}

export interface ScanNonReconnu {
  code: string; motif: MotifNonReconnu; produit: string | null; marques: string[]; base: string | null;
  nombre: number; premier: string; dernier: string;
}

/** Les codes non reconnus, les plus scannés d'abord. */
export async function listerScansNonReconnus(limite = 300): Promise<ScanNonReconnu[]> {
  const sb = getAdminSupabase();
  if (!sb) return [];
  const { data, error } = await sb.from("scans_non_reconnus").select("*").order("nombre", { ascending: false }).order("dernier", { ascending: false }).limit(limite);
  if (error || !data) return [];
  return data as ScanNonReconnu[];
}

/** Regroupe par marque lue (insensible à la casse) : ce sont les marques qu'il faut ajouter. */
export function parMarque(scans: ScanNonReconnu[]): { marque: string; scans: number; codes: number; exemple: string | null }[] {
  const m = new Map<string, { marque: string; scans: number; codes: number; exemple: string | null }>();
  for (const s of scans) {
    if (s.motif !== "marque_absente") continue;
    const nom = s.marques[0] ?? "";
    const cle = nom.toLowerCase();
    const e = m.get(cle) ?? { marque: nom, scans: 0, codes: 0, exemple: s.produit };
    e.scans += s.nombre;
    e.codes += 1;
    m.set(cle, e);
  }
  return [...m.values()].sort((a, b) => b.scans - a.scans || a.marque.localeCompare(b.marque, "fr"));
}
