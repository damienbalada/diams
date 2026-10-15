import { NextResponse } from "next/server";
import { listIndex } from "@/lib/data";
import { searchEntities } from "@/lib/search";
import { logoDe } from "@/lib/logos";

export const dynamic = "force-dynamic";

/** API de l'appli mobile : recherche d'une marque ou d'un groupe par son nom (30 résultats au plus). */
export async function GET(req: Request) {
  const q = new URL(req.url).searchParams.get("q") ?? "";
  const tous = (await listIndex()).map((e) => ({ ...e, grade: null }));
  const res = searchEntities(tous, q).slice(0, 30).map((e) => ({ slug: e.slug, nom: e.name, marque: e.is_brand, groupe: e.group, logo: logoDe(e.slug)?.src ?? null }));
  return NextResponse.json({ q, resultats: res });
}
