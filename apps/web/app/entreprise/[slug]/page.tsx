import { getScorePayload } from "@/lib/data";
import { chargerFiche } from "@/lib/fiche";
import { CarteIdentite } from "@/components/CarteIdentite";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const payload = await getScorePayload(slug).catch(() => null);
  const name = payload?.entity?.name;
  return name
    ? { title: name, description: `${name} : carte d'identité sur l'Index général des marques — les faits publiés, pilier par pilier, chacun relié à sa source et daté. Aucune note, que des faits.` }
    : { title: "Entité introuvable" };
}

export default async function CompanyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  try {
    const f = await chargerFiche(slug);
    if (!f) {
      return (
        <main>
          <a className="muted small" href="/">← retour</a>
          <div className="panel" style={{ marginTop: 12 }}>Entité introuvable : {slug}</div>
        </main>
      );
    }
    return <CarteIdentite {...f} />;
  } catch (e) {
    return (
      <main>
        <a className="muted small" href="/">← retour</a>
        <div className="panel" style={{ marginTop: 12, borderColor: "#6b2222" }}>
          <strong>Erreur de chargement.</strong>
          <p className="muted small">{(e as Error).message}</p>
        </div>
      </main>
    );
  }
}
