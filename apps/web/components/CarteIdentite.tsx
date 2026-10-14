import { marqueAnimale, marquesDocumentees, resumeGroupe, type Carte, type Fait, type MarqueAnimale, type MarqueDuGroupe, type Pilier, type Solidite } from "@/lib/carte";
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

/** Solidité de la source, écrite en toutes lettres dans une étiquette à contour (pas une simple
 *  couleur : décision de l'éditeur, 15/10/2026). */
function Solidite({ s }: { s: Solidite }) {
  return <span className={`ci-sol ci-sol-${s}`}>{SOLIDITE[s]}</span>;
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
        {f.nom} : {f.code === "ANI_EXPLOITATION" ? <strong className="ci-alerte">⚠️ {f.valeur}</strong> : <strong>{f.valeur}</strong>}
        {f.contexte && <span className="ci-badge" title="Donnée de contexte : ni bonne ni mauvaise en soi">contexte</span>}
        {p.conteste && <span className="ci-badge">contesté</span>}
      </div>
      <div className="ci-src">
        <Solidite s={p.solidite} /> {p.source}
        {p.reprisDe && <span className="ci-badge">donnée de {p.reprisDe}</span>}
        {f.niveau === "produit" && <span className="ci-badge">niveau : produits</span>}
        {f.niveau === "marque" && <span className="ci-badge">niveau : marque</span>}
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

type MarquesGroupe = { groupe: { slug: string; name: string }; marques: MarqueDuGroupe[] } | null;
const pl = (n: number, un: string, plusieurs: string) => `${n} ${n > 1 ? plusieurs : un}`;

/** Les faits d'un niveau : chronologie des faits documentés, signalements, puis ce qui manque. */
function Faits({ faits, cacherPresume }: { faits: Fait[]; cacherPresume?: boolean }) {
  const doc = faits.filter((f) => f.etat === "documente").sort((a, b) => b.preuve!.date.localeCompare(a.preuve!.date));
  const signales = faits.filter((f) => (f.etat === "presume" && !cacherPresume) || f.etat === "obligatoire_absent" || f.etat === "autre_forme");
  const vides = faits.filter((f) => f.etat === "aucune_info");
  return (
    <>
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
    </>
  );
}

/** Une section de niveau (groupe, marque, produits) dans un pilier déplié. */
function Niveau({ icone, titre, aide, children }: { icone: string; titre: React.ReactNode; aide: string; children: React.ReactNode }) {
  return (
    <section className="ci-niv-sec">
      <div className="ci-niv-t">
        {icone} {titre} <span className="ci-faint ci-small">— {aide}</span>
      </div>
      {children}
    </section>
  );
}

/** Pilier animal : l'état de chacune des marques du groupe (preuve propre à chaque marque). */
function ResumeAnimal({ mg, slug, estGroupe }: { mg: NonNullable<MarquesGroupe>; slug: string; estGroupe: boolean }) {
  const ms = mg.marques.map(marqueAnimale);
  const r = resumeGroupe(ms);
  const liste = (etat: MarqueAnimale["etat"], titre: string) => {
    const l = ms.filter((m) => m.etat === etat);
    return l.length > 0 && (
      <div className="ci-small" style={{ marginTop: 6 }}>
        <strong>{titre}</strong> :{" "}
        {l.map((m, i) => (
          <span key={m.slug}>{i > 0 && ", "}{m.slug === slug ? <strong>{m.nom}</strong> : <a href={`/entreprise/${m.slug}`}>{m.nom}</a>}{m.offreVegetale && etat !== "vegetale" ? " (produits végétaux)" : ""}</span>
        ))}
      </div>
    );
  };
  return (
    <div className="ci-small">
      {estGroupe ? "Ses" : <>Les marques de <a href={`/entreprise/${mg.groupe.slug}`}>{mg.groupe.name}</a> :</>}{" "}
      {pl(r.total, "marque suivie", "marques suivies")} ; preuve propre à chaque marque : {r.exploitation} avec exploitation animale documentée · {pl(r.vegetale, "entièrement végétale", "entièrement végétales")} · {r.nonDocumentee} non documentée{r.nonDocumentee > 1 ? "s" : ""}
      {r.offreVegetale > 0 && <> ; {pl(r.offreVegetale, "propose", "proposent")} aussi des produits 100 % végétaux</>}.
      <details className="ci-cit">
        <summary>Voir les marques</summary>
        {liste("exploitation", "Exploitation animale documentée")}
        {liste("vegetale", "Entièrement végétales")}
        {liste("non_documentee", "Non documentées")}
      </details>
    </div>
  );
}

/** Autres piliers, fiche d'un groupe : ses marques qui ont une information propre dans ce pilier. */
function ResumeMarques({ mg, pilier }: { mg: NonNullable<MarquesGroupe>; pilier: string }) {
  const docs = marquesDocumentees(mg.marques, pilier);
  if (!docs.length) return <div className="ci-vides">Aucune information propre à ses {pl(mg.marques.length, "marque suivie", "marques suivies")} : elles reprennent les données du groupe.</div>;
  return (
    <div className="ci-small">
      {pl(docs.length, "marque", "marques")} sur {mg.marques.length} {docs.length > 1 ? "ont" : "a"} une information propre dans ce pilier :{" "}
      {docs.map((m, i) => (
        <span key={m.slug}>{i > 0 && ", "}<a href={`/entreprise/${m.slug}`}>{m.nom}</a></span>
      ))}
      .
    </div>
  );
}

function LignePilier({ p, mg, estMarque, nom, slug }: { p: Pilier; mg: MarquesGroupe; estMarque: boolean; nom: string; slug: string }) {
  const k = p.cle;
  // Fiche d'un groupe : sans preuve propre au groupe, le pilier animal se lit d'après ses marques.
  const r = p.code === "ANI" && !estMarque && mg ? resumeGroupe(mg.marques.map(marqueAnimale)) : null;
  const niveauGroupe = !!r && (r.exploitation > 0 || r.vegetale > 0) && k?.etat !== "documente";
  // Exploitation animale : signalée en rouge avec ⚠️, quel que soit le classement BBFAW (décision
  // de l'éditeur, 15/10/2026) ; présumée : ⚠️ et couleur de la présomption.
  const exploitee = p.code === "ANI" && ((niveauGroupe && r!.exploitation > 0) || (k?.code === "ANI_EXPLOITATION" && k.etat === "documente"));
  const presumee = p.code === "ANI" && !exploitee && k?.code === "ANI_EXPLOITATION" && k.etat === "presume";
  const etatCle = exploitee ? "alerte" : niveauGroupe ? "documente" : k ? k.etat : "aucune_info";
  const valeurCle = niveauGroupe
    ? r!.exploitation > 0
      ? `Oui, documentée chez ${r!.exploitation} marque${r!.exploitation > 1 ? "s" : ""} sur ${r!.total}`
      : `${r!.vegetale} marque${r!.vegetale > 1 ? "s" : ""} entièrement végétale${r!.vegetale > 1 ? "s" : ""} sur ${r!.total}`
    : k ? k.valeur : "Aucune information";
  const g = p.faits.filter((f) => f.niveau === "groupe");
  const m = p.faits.filter((f) => f.niveau === "marque");
  const pr = p.faits.filter((f) => f.niveau === "produit");
  return (
    <details className="ci-row">
      <summary>
        <span className="ci-p">
          {exploitee || presumee ? "⚠️" : ICONE[p.code]} {p.nom}
        </span>
        <span className="ci-cnt">
          {p.documentes}/{p.total}
        </span>
        <span className={`ci-v ci-${etatCle}`}>
          {exploitee && "⚠️ "}
          {valeurCle}
          {!niveauGroupe && k?.preuve?.reprisDe && <span className="ci-badge">{k.preuve.reprisDe}</span>}
        </span>
      </summary>
      <div className="ci-body">
        {p.solidite && <p className="ci-faint ci-small">Ce pilier repose sur des {SOLIDITE_PILIER[p.solidite]}.</p>}
        {(g.length > 0 || (p.code === "ANI" && estMarque && mg)) && (
          <Niveau
            icone="🏢"
            titre={estMarque ? (mg ? <>Groupe · <a href={`/entreprise/${mg.groupe.slug}`}>{mg.groupe.name}</a></> : <>Groupe</>) : <>Groupe · {nom}</>}
            aide={estMarque ? "ce que publie le groupe ; la marque le reprend" : "ce que publie le groupe"}
          >
            {p.code === "ANI" && estMarque && mg && <ResumeAnimal mg={mg} slug={slug} estGroupe={false} />}
            <Faits faits={g} cacherPresume={niveauGroupe} />
          </Niveau>
        )}
        {estMarque && m.length > 0 && (
          <Niveau icone="🏷️" titre={<>Marque · {nom}</>} aide="ce qui est prouvé pour la marque elle-même">
            <Faits faits={m} />
          </Niveau>
        )}
        {!estMarque && mg && mg.marques.length > 0 && (
          <Niveau icone="🏷️" titre="Ses marques" aide="ce qui est prouvé pour chaque marque elle-même">
            {p.code === "ANI" ? <ResumeAnimal mg={mg} slug={slug} estGroupe /> : <ResumeMarques mg={mg} pilier={p.code} />}
          </Niveau>
        )}
        {pr.length > 0 && (
          <Niveau icone="🛒" titre="Produits" aide="ce qui ne vaut que pour certains produits, pas pour toute la marque">
            <Faits faits={pr} />
          </Niveau>
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
  marquesGroupe = null,
  estMarque = false,
}: {
  carte: Carte;
  estGroupe: boolean;
  proprietaire: { slug: string; name: string } | null;
  preuvesPropriete: OwnershipProof[];
  memeRayon: { slug: string; name: string; group: string | null }[];
  marques: { slug: string; name: string }[];
  marquesGroupe?: MarquesGroupe;
  estMarque?: boolean;
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
          <LignePilier key={p.code} p={p} mg={marquesGroupe} estMarque={estMarque} nom={carte.nom} slug={carte.slug} />
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
          <li>Solidité de chaque source : <Solidite s="officielle" /> <Solidite s="reconnue" /> <Solidite s="declarative" /></li>
          <li>Chaque pilier se lit à trois niveaux : 🏢 le <strong>groupe</strong> (ce qu'il publie : climat, fiscalité, lobbying… ; la marque le reprend), 🏷️ la <strong>marque</strong> (ce qui est prouvé pour elle-même : un seul produit d'origine animale suffit ; « entièrement végétale » seulement si une page officielle le dit pour toute la marque), 🛒 les <strong>produits</strong> (ce qui ne vaut que pour certains produits, sans s'étendre à la marque).</li>
          <li><span className="ci-alerte">⚠️ Exploitation animale</span> : signalée en rouge dès qu'un produit d'origine animale est documenté, même si l'entreprise est bien classée par ailleurs pour le bien-être animal (BBFAW, classement des politiques d'élevage).</li>
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
