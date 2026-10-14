import { getScorePayload, getOwnerGroup, getOwnershipProofs, getJournal, getMemeRayon, getMarques, getAnimalGroupe, type OwnershipProof } from "@/lib/data";
import { construireCarte } from "@/lib/carte";
import { CarteIdentite } from "@/components/CarteIdentite";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const payload = await getScorePayload(slug).catch(() => null);
  const name = payload?.entity?.name;
  return name
    ? { title: name, description: `${name} : carte d'identité DIAMS — les faits publiés, pilier par pilier, chacun relié à sa source et daté. Aucune note, que des faits.` }
    : { title: "Entité introuvable" };
}

export default async function CompanyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  try {
    const payload = await getScorePayload(slug);
    if (!payload) {
      return (
        <main>
          <a className="muted small" href="/">← retour</a>
          <div className="panel" style={{ marginTop: 12 }}>Entité introuvable : {slug}</div>
        </main>
      );
    }
    // Blocs d'information : une erreur sur l'un d'eux ne doit jamais empêcher l'affichage de la carte.
    const [journal, proprietaire, preuves, memeRayon, marques, animalGroupe] = await Promise.all([
      getJournal(slug).catch(() => []),
      getOwnerGroup(slug).catch(() => null),
      getOwnershipProofs(slug).catch(() => [] as OwnershipProof[]),
      getMemeRayon(slug).catch(() => []),
      getMarques(slug).catch(() => []),
      getAnimalGroupe(slug).catch(() => null),
    ]);
    const carte = construireCarte(payload as any, journal);
    const estGroupe = (payload.ownership_chain ?? []).length <= 1 || marques.length > 0;
    return (
      <CarteIdentite
        carte={carte}
        estGroupe={estGroupe && !proprietaire}
        proprietaire={proprietaire}
        preuvesPropriete={preuves}
        memeRayon={memeRayon}
        marques={marques}
        animalGroupe={animalGroupe}
      />
    );
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
