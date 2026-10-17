import { NextResponse } from "next/server";
import { chargerFiche } from "@/lib/fiche";
import { ficheEnJson } from "@/lib/fiche-json";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

/** API de l'appli mobile : la fiche d'une marque ou d'un groupe, en JSON. */
export async function GET(_req: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const f = await chargerFiche(slug);
  if (!f) return NextResponse.json({ trouve: false, raison: "Fiche introuvable." }, { status: 404 });
  return NextResponse.json({ trouve: true, fiche: ficheEnJson(slug, f.carte, f.proprietaire, null, { estMarque: f.estMarque, produitsLus: f.produitsLus, alternatives: f.alternatives }) });
}
