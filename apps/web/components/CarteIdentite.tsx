import type { Carte, Fait, Pilier, Solidite } from "@/lib/carte";
import type { OwnershipProof } from "@/lib/data";
import { CorrectionForm } from "@/components/CorrectionForm";

const ICONE: Record<string, string> = { ANI: "🐄", ENV: "🌍", PLA: "🧴", WAT: "💧", LAB: "👥", SUP: "🔗", GOV: "🏛️", TAX: "💶", GEO: "🗺️", INV: "🏦" };
const SOLIDITE: Record<Solidite, string> = {
  officielle: "Source officielle (loi, régulateur)",
  reconnue: "Organisme reconnu",
  declarative: "Déclaration publique (site de l'entreprise, presse)",
};
const SOLIDITE_PILIER: Record<Solidite, string> = {
  officielle: "sources très solides",
  reconnue: "sources solides",
  declarative: "sources déclaratives",
};
const dfr = (d: string) => d.split("-").reverse().join("/");

function Pastille({ s }: { s: Solidite }) {
  return <i className={`ci-dot ci-${s}`} aria-hidden="true" />;
}

/** Une entrée de chronologie : date, fait, source (pastille de solidité), citation à déplier. */
function Entree({ f, avecPilier, nomPilier }: { f: Fait; avecPilier?: boolean; nomPilier?: string }) {
  const p = f.preuve!;
  return (
    <li className={`ci-it ci-it-${p.solidite}`}>
      <div className="ci-date">
        {dfr(p.date)}
        {!p.dateEvenement && <span className="ci-faint"> · relevé</span>}
        {avecPilier && nomPilier && <span className="ci-faint"> · {ICONE[f.pilier]} {nomPilier}</span>}
      </div>
      <div className="ci-fait">
        {f.nom} : <strong>{f.valeur}</strong>
        {f.contexte && <span className="ci-badge" title="Donnée de contexte : ni bonne ni mauvaise en soi">contexte</span>}
        {p.conteste && <span className="ci-badge">contesté</span>}
      </div>
      <div className="ci-src">
        <Pastille s={p.solidite} /> {SOLIDITE[p.solidite]} · {p.source}
        {p.reprisDe && <span className="ci-badge">donnée de {p.reprisDe}</span>}
      </div>
      {(p.citation || p.url) && (
        <details className="ci-cit">
          <summary>Ce que dit la source</summary>
          {p.citation && <blockquote>{p.citation}</blockquote>}
          {p.url && (
            <a href={p.url} target="_blank" rel="noopener noreferrer">
              Ouvrir la source ↗
            </a>
          )}
        </details>
      )}
    </li>
  );
}

function LignePilier({ p }: { p: Pilier }) {
  const k = p.cle;
  const doc = p.faits.filter((f) => f.etat === "documente").sort((a, b) => b.preuve!.date.localeCompare(a.preuve!.date));
  const signales = p.faits.filter((f) => f.etat === "presume" || f.etat === "obligatoire_absent" || f.etat === "autre_forme");
  const vides = p.faits.filter((f) => f.etat === "aucune_info");
  const etatCle = k ? k.etat : "aucune_info";
  return (
    <details className="ci-row">
      <summary>
        <span className="ci-p">
          {ICONE[p.code]} {p.nom}
        </span>
        <span className="ci-cnt">
          {p.documentes}/{p.total}
        </span>
        <span className={`ci-v ci-${etatCle}`}>
          {k ? k.valeur : "Aucune information"}
          {k?.preuve?.reprisDe && <span className="ci-badge">{k.preuve.reprisDe}</span>}
        </span>
      </summary>
      <div className="ci-body">
        {p.solidite && <p className="ci-faint ci-small">Ce pilier repose sur des {SOLIDITE_PILIER[p.solidite]}.</p>}
        {doc.length > 0 && (
          <ol className="ci-tl">
            {doc.map((f) => (
              <Entree key={f.code} f={f} />
            ))}
          </ol>
        )}
        {signales.map((f) => (
          <div key={f.code} className={`ci-sig ci-${f.etat}`}>
            <strong>{f.nom}</strong> : {f.valeur}
            {f.obligation.length > 0 && <span className="ci-faint"> — obligation : {f.obligation.join(", ")}</span>}
            {f.note && <div className="ci-small">{f.note}</div>}
          </div>
        ))}
        {vides.length > 0 && (
          <div className="ci-vides">
            <strong>Aucune information :</strong>{" "}
            {vides.map((f, i) => (
              <span key={f.code} title={f.note ?? undefined}>
                {i > 0 && " · "}
                {f.nom}
              </span>
            ))}
            {vides.some((f) => f.note) && (
              <div className="ci-small ci-faint">
                {[...new Set(vides.map((f) => f.note).filter(Boolean))].map((n) => (
                  <div key={n!}>{n}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </details>
  );
}

export function CarteIdentite({
  carte,
  estGroupe,
  proprietaire,
  preuvesPropriete,
  memeRayon,
  marques,
}: {
  carte: Carte;
  estGroupe: boolean;
  proprietaire: { slug: string; name: string } | null;
  preuvesPropriete: OwnershipProof[];
  memeRayon: { slug: string; name: string; group: string | null }[];
  marques: { slug: string; name: string }[];
}) {
  const nomPilier = new Map(carte.piliers.map((p) => [p.code, p.nom]));
  return (
    <main className="ci">
      <a className="muted small" href="/">← rechercher une autre marque</a>
      <section className="ci-card">
        <div className="ci-head">
          <div className="ci-k">{estGroupe ? "GROUPE" : "CARTE D'IDENTITÉ"}</div>
          <h1>{carte.nom}</h1>
          {proprietaire ? (
            <div className="ci-own">
              Appartient à <a href={`/entreprise/${proprietaire.slug}`}><strong>{proprietaire.name}</strong></a>, qui reçoit l'argent de vos achats
              {carte.chaine.length > 2 && <span className="ci-faint"> (via {carte.chaine.slice(1, -1).join(" → ")})</span>}
            </div>
          ) : (
            estGroupe && marques.length > 0 && <div className="ci-own">{marques.length} marque(s) suivie(s)</div>
          )}
        </div>
        {carte.piliers.map((p) => (
          <LignePilier key={p.code} p={p} />
        ))}
        <details className="ci-row">
          <summary>
            <span className="ci-p">📜 Toutes les sources</span>
            <span className="ci-cnt">{carte.chronologie.length}</span>
            <span className="ci-v">Chronologie complète</span>
          </summary>
          <div className="ci-body">
            {carte.chronologie.length ? (
              <ol className="ci-tl">
                {carte.chronologie.map((f) => (
                  <Entree key={f.code} f={f} avecPilier nomPilier={nomPilier.get(f.pilier)} />
                ))}
              </ol>
            ) : (
              <p className="ci-faint">Aucune information documentée pour l'instant.</p>
            )}
          </div>
        </details>
        <p className="ci-foot">
          {carte.documentes} information(s) documentée(s) sur {carte.total} recherchées · aucune note, que des faits sourcés.
          La date indiquée est celle de l'événement quand elle est connue, sinon celle de notre relevé.
        </p>
      </section>

      <details className="panel ci-legend">
        <summary>Comment lire cette fiche ?</summary>
        <ul className="small">
          <li><Pastille s="officielle" /> {SOLIDITE.officielle} · <Pastille s="reconnue" /> {SOLIDITE.reconnue} · <Pastille s="declarative" /> {SOLIDITE.declarative}</li>
          <li><span className="ci-presume">Présumée</span> : exploitation animale non documentée dans un secteur où elle est la règle ; elle est présumée tant que la marque ne prouve pas le contraire.</li>
          <li><span className="ci-obligatoire_absent">Obligatoire, non publié</span> : la loi impose cette donnée et la lecture du rapport officiel confirme qu'elle n'y est pas.</li>
          <li><span className="ci-autre_forme">Publié sous une autre forme</span> : l'entreprise publie l'information, mais pas sous la forme que la loi exige (pour une partie du groupe seulement, par pays…).</li>
          <li><span className="ci-aucune_info">Aucune information</span> : rien de publié, rien d'obligatoire ; quand nous avons cherché dans une liste complète, la fiche le précise.</li>
        </ul>
      </details>

      {preuvesPropriete.length > 0 && (
        <details className="panel">
          <summary><strong>Appartenance prouvée</strong> <span className="muted small">— pourquoi {carte.nom} appartient à {preuvesPropriete[0].owner}</span></summary>
          <ul className="small">
            {preuvesPropriete.map((p) => (
              <li key={p.source_url} style={{ marginTop: 8 }}>
                {p.excerpt}{" "}
                <a className="muted" href={p.source_url} target="_blank" rel="noopener noreferrer">source ↗</a>{" "}
                <span className="muted">· relevé le {dfr(p.observed_on)}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {estGroupe && marques.length > 0 && (
        <div className="panel">
          <strong>Marques du groupe</strong>
          <div className="ci-chips">
            {marques.map((m) => (
              <a key={m.slug} className="ci-chip" href={`/entreprise/${m.slug}`}>{m.name}</a>
            ))}
          </div>
        </div>
      )}

      {memeRayon.length > 0 && (
        <div className="panel">
          <strong>Autres marques du même rayon</strong>{" "}
          <span className="muted small">— d'autres groupes, par ordre alphabétique (aucun classement) : comparez les fiches</span>
          <div className="ci-chips">
            {memeRayon.map((m) => (
              <a key={m.slug} className="ci-chip" href={`/entreprise/${m.slug}`}>
                {m.name}
                {m.group && <small className="muted"> · {m.group}</small>}
              </a>
            ))}
          </div>
        </div>
      )}

      <CorrectionForm entitySlug={carte.slug} indicators={carte.piliers.flatMap((p) => p.faits.map((f) => ({ code: f.code, name: f.nom })))} />
    </main>
  );
}
