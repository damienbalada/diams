import { marqueAnimale, marquesDocumentees, raisonVide, resumeGroupe, type Carte, type Fait, type MarqueAnimale, type MarqueDuGroupe, type Pilier, type Solidite } from "@/lib/carte";
import type { OwnershipProof, Produit } from "@/lib/data";
import { logoDe } from "@/lib/logos";
import type { Signal } from "@/lib/seuils";
import { CorrectionForm } from "@/components/CorrectionForm";

const ICONE: Record<string, string> = { ANI: "🐄", ENV: "🌍", PLA: "🧴", WAT: "💧", LAB: "👥", SUP: "🔗", GOV: "🏛️", TAX: "💶", GEO: "🗺️", INV: "🏦" };
function Chevron() {
  return (
    <span className="ci-chev" aria-hidden="true">
      <svg viewBox="0 0 12 12" width="11" height="11"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
    </span>
  );
}

/** Teinte propre à chaque pilier (repère visuel seulement : elle ne dit rien du résultat). */
const TEINTE: Record<string, string> = {
  ANI: "#b4532a", ENV: "#1f8a4c", PLA: "#0e7a8a", WAT: "#2563c9", LAB: "#7a3fd0",
  SUP: "#a86a12", GOV: "#4b5a70", TAX: "#11796d", GEO: "#b8325a", INV: "#4a43c4",
};
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

/** Alerte ou point de vigilance d'un fait, avec la règle qui le déclenche. */
function SignalFait({ s }: { s: Signal }) {
  return (
    <div className={`ci-seuil ci-seuil-${s.niveau}`}>
      {s.niveau === "alerte" ? "⚠️ Alerte" : "🟠 Vigilance"} : {s.motif}
      <span className="ci-faint"> — seuil : {s.regle}</span>
    </div>
  );
}

/** Bandeau en tête de fiche : toutes les alertes, puis les points de vigilance. */
function Bandeau({ items }: { items: { pilier: string; s: Signal }[] }) {
  const al = items.filter((x) => x.s.niveau === "alerte");
  const vi = items.filter((x) => x.s.niveau === "vigilance");
  if (!items.length) return null;
  return (
    <div className="ci-bandeaux">
      {al.length > 0 && (
        <div className="ci-bandeau ci-bandeau-alerte" role="note">
          <div className="ci-bandeau-t">⚠️ {pl(al.length, "alerte", "alertes")}</div>
          <ul>
            {al.map((x, i) => (
              <li key={i} title={`Seuil : ${x.s.regle}`}><span aria-hidden="true">{ICONE[x.pilier]}</span> {x.s.motif}</li>
            ))}
          </ul>
        </div>
      )}
      {vi.length > 0 && (
        <div className="ci-bandeau ci-bandeau-vigilance" role="note">
          <div className="ci-bandeau-t">🟠 {pl(vi.length, "point de vigilance", "points de vigilance")}</div>
          <ul>
            {vi.map((x, i) => (
              <li key={i} title={`Seuil : ${x.s.regle}`}><span aria-hidden="true">{ICONE[x.pilier]}</span> {x.s.motif}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
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
        {f.nom} : {f.signal?.niveau === "alerte" ? <strong className="ci-alerte">⚠️ {f.valeur}</strong> : f.signal ? <strong className="ci-vigilance">{f.valeur}</strong> : <strong>{f.valeur}</strong>}
        {f.contexte && <span className="ci-badge" title="Donnée de contexte : ni bonne ni mauvaise en soi">contexte</span>}
        {p.conteste && <span className="ci-badge">contesté</span>}
      </div>
      <div className="ci-src">
        <Solidite s={p.solidite} /> {p.source}
        {p.reprisDe && <span className="ci-badge">donnée de {p.reprisDe}</span>}
        {f.niveau === "produit" && <span className="ci-badge">niveau : produits</span>}
        {f.niveau === "marque" && <span className="ci-badge">niveau : marque</span>}
      </div>
      {f.signal && <SignalFait s={f.signal} />}
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

/** Logo d'un groupe ou d'une marque ; à défaut, un pictogramme neutre (jamais une initiale). */
function Logo({ slug, nom, taille, groupe }: { slug: string; nom: string; taille: number; groupe?: boolean }) {
  const l = logoDe(slug);
  return l ? (
    <img className="ci-logo" src={l.src} alt={`Logo ${nom}`} title={`Logo : ${l.origine}`} width={taille} height={taille} loading="lazy" style={{ width: taille, height: taille }} />
  ) : (
    <span className="ci-logo ci-logo-vide" style={{ width: taille, height: taille, fontSize: Math.round(taille * 0.45) }} title="Logo non trouvé" aria-hidden="true">
      {groupe ? "🏢" : "🏷️"}
    </span>
  );
}

/** Grille de vignettes (logo + nom) : marques d'un groupe. */
function Vignettes({ items, max = 24 }: { items: { slug: string; name: string }[]; max?: number }) {
  const v = (m: { slug: string; name: string }) => (
    <a key={m.slug} className="ci-vign" href={`/entreprise/${m.slug}`}>
      <Logo slug={m.slug} nom={m.name} taille={44} />
      <span>{m.name}</span>
    </a>
  );
  const tri = [...items].sort((a, b) => Number(!!logoDe(b.slug)) - Number(!!logoDe(a.slug)) || a.name.localeCompare(b.name, "fr"));
  return (
    <>
      <div className="ci-vigns">{tri.slice(0, max).map(v)}</div>
      {tri.length > max && (
        <details className="ci-plus">
          <summary>Voir les {tri.length - max} autres</summary>
          <div className="ci-vigns">{tri.slice(max).map(v)}</div>
        </details>
      )}
    </>
  );
}

type MarquesGroupe = { groupe: { slug: string; name: string }; marques: MarqueDuGroupe[] } | null;
const pl = (n: number, un: string, plusieurs: string) => `${n} ${n > 1 ? plusieurs : un}`;

/** Icône propre à chaque indicateur, pour le repérer dans son pilier (repère visuel seulement). */
const ICONE_IND: Record<string, string> = {
  ANI_EXPLOITATION: "🥩", ANI_ANIMAL_FREE: "🌱", ANI_OFFRE_VEGETALE: "🥦", ANI_FUR_FREE: "🦊", ANI_BBFAW_TIER: "📊", ANI_ANGORA_MOHAIR: "🐇",
  ANI_DOWN_RDS: "🪶", ANI_EXOTIC_SKINS: "🐊", ANI_LEATHER_TRACE: "👞", ANI_SLAUGHTER: "🚚", ANI_TESTING: "🧪", ANI_WOOL_MULESING: "🐑",
  ENV_CDP_CLIMATE: "📋", ENV_GHG_INTENSITY: "🏭", ENV_GHG_TREND: "📉", ENV_GREENWASHING: "🎭", ENV_MATERIAL_CHANGE: "🧵", ENV_SBTI_VALIDATED: "🎯",
  ENV_SCOPE3_DISCLOSED: "🌐", ENV_TAXONOMY_CAPEX: "🏗️",
  PLA_POLLUTER: "🗑️", PLA_RECYCLED: "♻️", PLA_REDUCTION: "🧴",
  WAT_CDP: "📋", WAT_CONTROVERSY: "🏜️", WAT_INTENSITY: "🚰",
  LAB_CEO_PAY_RATIO: "💰", LAB_EGAPRO_INDEX: "⚖️", LAB_GENDER_PAYGAP: "👩‍💼", LAB_LITIGATION_RATE: "🧑‍⚖️", LAB_LIVING_WAGE: "🏠",
  SUP_BHRRC_ALLEG: "📣", SUP_FTI_SCORE: "🔍", SUP_KNOWTHECHAIN: "⛓️", SUP_LIVING_WAGE: "🪙", SUP_SUPPLIER_LIST: "📃", SUP_VIGILANCE_PLAN: "🛡️",
  GOV_BCORP: "✅", GOV_BOARD_GENDER: "👩", GOV_BOARD_INDEP: "🪑", GOV_SANCTIONS: "🔨",
  TAX_CBCR_PUBLISHED: "🗺️", TAX_EFFECTIVE_RATE: "🧾", TAX_HAVEN_PRESENCE: "🏝️",
  GEO_CONFLICT_TIES: "⚔️", GEO_LOBBYING_ALIGN: "🧭", GEO_LOBBYING_SPEND: "💼", GEO_LOBBYING_TRANSP: "📒", GEO_POL_FINANCING: "🗳️", GEO_RUSSIA_EXIT: "🚪",
  INV_CONTROVERSIAL_HOLDINGS: "💣", INV_FOSSIL_FINANCING: "🛢️", INV_RESPONSIBLE_POLICY: "📜", INV_SOLIDARITY_LABEL: "🤝", INV_SUSTAINABLE_FINANCE: "🌿",
};

/** Ordre dans un pilier : alertes, vigilance, faits documentés (du plus récent), signalements, vides. */
function rang(f: Fait) {
  if (f.signal?.niveau === "alerte") return 0;
  if (f.signal?.niveau === "vigilance") return 1;
  if (f.etat === "documente") return 2;
  if (f.etat === "aucune_info") return 4;
  return 3;
}

/** Un indicateur, sous forme de carte : icône et nom, valeur en grand, source, seuil, citation. */
function CarteIndicateur({ f }: { f: Fait }) {
  const p = f.preuve;
  const vide = f.etat === "aucune_info" ? raisonVide(f) : null;
  const ton = f.signal?.niveau ?? (f.etat === "documente" ? "documente" : vide ? "vide" : "signale");
  return (
    <article className={`ci-ind ci-ind-${ton}`}>
      <header className="ci-ind-h">
        <span className="ci-ind-ico" aria-hidden="true">{ICONE_IND[f.code] ?? "•"}</span>
        <span className="ci-ind-nom">{f.nom}</span>
        {f.signal && <span className={`ci-tag ci-tag-${f.signal.niveau}`}>{f.signal.niveau === "alerte" ? "⚠️ Alerte" : "🟠 Vigilance"}</span>}
      </header>
      <div className="ci-ind-val">
        {vide ? vide[0] : f.valeur}
        {f.contexte && <span className="ci-badge" title="Donnée de contexte : ni bonne ni mauvaise en soi">contexte</span>}
        {p?.conteste && <span className="ci-badge">contesté</span>}
      </div>
      {vide && <div className="ci-ind-txt">{vide[1][0].toUpperCase() + vide[1].slice(1)}.</div>}
      {f.etat !== "documente" && f.etat !== "aucune_info" && f.obligation.length > 0 && <div className="ci-ind-txt">Obligation : {f.obligation.join(", ")}</div>}
      {f.note && <div className="ci-ind-note">{f.note}</div>}
      {p && (
        <div className="ci-ind-src">
          <span>{dfr(p.date)}{!p.dateEvenement && " (relevé)"}</span>
          <Solidite s={p.solidite} />
          <span>{p.source}</span>
          {p.reprisDe && <span className="ci-badge">donnée de {p.reprisDe}</span>}
        </div>
      )}
      {f.signal && <div className={`ci-ind-seuil ci-seuil-${f.signal.niveau}`}>Seuil : {f.signal.regle}</div>}
      {p && (p.citation || p.url) && (
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
    </article>
  );
}

/** Les indicateurs d'un niveau, tous affichés, même vides (décision de l'éditeur, 15/10/2026). */
function Faits({ faits, cacherPresume }: { faits: Fait[]; cacherPresume?: boolean }) {
  const fs = faits
    .filter((f) => !(cacherPresume && f.etat === "presume"))
    .sort((a, b) => rang(a) - rang(b) || (b.preuve?.date ?? "").localeCompare(a.preuve?.date ?? ""));
  return (
    <div className="ci-inds">
      {fs.map((f) => (
        <CarteIndicateur key={f.code} f={f} />
      ))}
    </div>
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
  const sig = niveauGroupe ? null : k?.signal ?? null;
  const alerte = exploitee || sig?.niveau === "alerte";
  const vigilance = !alerte && (presumee || sig?.niveau === "vigilance");
  const etatCle = alerte ? "alerte" : vigilance && sig ? "vigilance" : niveauGroupe ? "documente" : k ? k.etat : "aucune_info";
  const valeurCle = niveauGroupe
    ? r!.exploitation > 0
      ? `Produits issus de l'exploitation animale chez ${r!.exploitation} marque${r!.exploitation > 1 ? "s" : ""} sur ${r!.total}`
      : `${r!.vegetale} marque${r!.vegetale > 1 ? "s" : ""} entièrement végétale${r!.vegetale > 1 ? "s" : ""} sur ${r!.total}`
    : k ? (sig && k.valeur === "Documenté" ? sig.motif[0].toUpperCase() + sig.motif.slice(1) : k.valeur) : "Aucune information";
  const g = p.faits.filter((f) => f.niveau === "groupe");
  const m = p.faits.filter((f) => f.niveau === "marque");
  const pr = p.faits.filter((f) => f.niveau === "produit");
  return (
    <details className="ci-row" style={{ "--pil": TEINTE[p.code] ?? "#6c3bff" } as React.CSSProperties}>
      <summary>
        <span className="ci-p">
          <span className={`ci-ico${alerte ? " ci-ico-alerte" : vigilance ? " ci-ico-vigilance" : ""}`} aria-hidden="true">{ICONE[p.code]}</span>
          {p.nom}
        </span>
        <span className="ci-cnt">
          {p.documentes}/{p.total}
          <Chevron />
        </span>
        <span className={`ci-v ci-${etatCle}`}>
          {alerte ? "⚠️ " : vigilance && sig ? "🟠 " : ""}
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
  produits = null,
}: {
  carte: Carte;
  estGroupe: boolean;
  proprietaire: { slug: string; name: string } | null;
  preuvesPropriete: OwnershipProof[];
  memeRayon: { slug: string; name: string; group: string | null }[];
  marques: { slug: string; name: string }[];
  marquesGroupe?: MarquesGroupe;
  estMarque?: boolean;
  produits?: { total: number; produits: Produit[]; lien: string } | null;
}) {
  const nomPilier = new Map(carte.piliers.map((p) => [p.code, p.nom]));
  // Fiche d'un groupe : l'exploitation animale se lit d'après ses marques (comme la ligne du pilier).
  const rg = !estMarque && marquesGroupe ? resumeGroupe(marquesGroupe.marques.map(marqueAnimale)) : null;
  const signaux = carte.signaux.flatMap((f): { pilier: string; s: Signal }[] => {
    if (f.code === "ANI_EXPLOITATION" && f.etat === "presume" && rg && (rg.exploitation > 0 || rg.vegetale > 0)) return [];
    return [{ pilier: f.pilier, s: f.signal! }];
  });
  if (rg && rg.exploitation > 0 && !carte.signaux.some((f) => f.code === "ANI_EXPLOITATION" && f.etat === "documente")) {
    signaux.unshift({ pilier: "ANI", s: { niveau: "alerte", motif: `produits issus de l'exploitation animale chez ${rg.exploitation} marque${rg.exploitation > 1 ? "s" : ""} sur ${rg.total}`, regle: "un seul produit d'origine animale suffit" } });
  }
  return (
    <main className="ci">
      <a className="muted small" href="/">← rechercher une autre marque</a>
      <section className="ci-card">
        <div className="ci-head">
          <Logo slug={carte.slug} nom={carte.nom} taille={72} groupe={estGroupe} />
          <div className="ci-head-t">
          <div className="ci-k">{estGroupe ? "GROUPE" : "CARTE D'IDENTITÉ"}</div>
          <h1>{carte.nom}</h1>
          {proprietaire ? (
            <div className="ci-own">
              Appartient à <a className="ci-own-g" href={`/entreprise/${proprietaire.slug}`}><Logo slug={proprietaire.slug} nom={proprietaire.name} taille={22} groupe /><strong>{proprietaire.name}</strong></a>, qui reçoit l'argent de vos achats
              {carte.chaine.length > 2 && <span className="ci-faint"> (via {carte.chaine.slice(1, -1).join(" → ")})</span>}
            </div>
          ) : (
            estGroupe && marques.length > 0 && <div className="ci-own">{pl(marques.length, "marque suivie", "marques suivies")}</div>
          )}
          </div>
        </div>
        <Bandeau items={signaux} />
        {carte.piliers.map((p) => (
          <LignePilier key={p.code} p={p} mg={marquesGroupe} estMarque={estMarque} nom={carte.nom} slug={carte.slug} />
        ))}
        <details className="ci-row">
          <summary>
            <span className="ci-p"><span className="ci-ico" aria-hidden="true">📜</span>Toutes les sources</span>
            <span className="ci-cnt">{carte.chronologie.length}<Chevron /></span>
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

      {estGroupe && marques.length > 0 && (
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Ses marques <span className="ci-sec-n">{marques.length}</span></h2>
          <p className="muted small">Marques détenues par {carte.nom}, directement ou par ses filiales ; chacune a sa fiche.</p>
          <Vignettes items={marques} />
        </section>
      )}

      {estMarque && (
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Ses produits {produits && <span className="ci-sec-n">{produits.total}</span>}</h2>
          {produits ? (
            <>
              <p className="muted small">
                Les produits les plus scannés en France, d'après <a className="ci-lien" href={produits.lien} target="_blank" rel="noopener noreferrer">Open Food Facts ↗</a> (base collaborative sous licence ouverte). Ils aident à reconnaître la marque en magasin ; ce ne sont pas des preuves.
              </p>
              <div className="ci-prods">
                {produits.produits.map((x) => (
                  <a key={x.code} className="ci-prod" href={`https://fr.openfoodfacts.org/produit/${x.code}`} target="_blank" rel="noopener noreferrer">
                    {x.image ? <img src={x.image} alt="" loading="lazy" /> : <span className="ci-prod-vide" aria-hidden="true">🛒</span>}
                    <span>{x.nom}</span>
                  </a>
                ))}
              </div>
            </>
          ) : (
            <p className="muted small">Pas encore de liste de produits pour cette marque : elle n'existe pour l'instant que pour l'alimentation et les boissons, d'après Open Food Facts.</p>
          )}
        </section>
      )}

      <details className="panel ci-legend">
        <summary>Comment lire cette fiche ?</summary>
        <ul className="small">
          <li>Solidité de chaque source : <Solidite s="officielle" /> <Solidite s="reconnue" /> <Solidite s="declarative" /></li>
          <li>Chaque pilier se lit à trois niveaux : 🏢 le <strong>groupe</strong> (ce qu'il publie : climat, fiscalité, lobbying… ; la marque le reprend), 🏷️ la <strong>marque</strong> (ce qui est prouvé pour elle-même : un seul produit d'origine animale suffit ; « entièrement végétale » seulement si une page officielle le dit pour toute la marque), 🛒 les <strong>produits</strong> (ce qui ne vaut que pour certains produits, sans s'étendre à la marque).</li>
          <li><span className="ci-alerte">⚠️ Exploitation animale</span> : signalée en rouge dès qu'un produit d'origine animale est documenté, même si l'entreprise est bien classée par ailleurs pour le bien-être animal (BBFAW, classement des politiques d'élevage).</li>
          <li><span className="ci-alerte">⚠️ Alerte</span> et <span className="ci-vigilance">🟠 point de vigilance</span> : le fait franchit un seuil fixé pour chaque indicateur, à partir d'une référence qu'on peut citer (loi, directive, moyenne publiée du classement) ou, à défaut, d'un choix éditorial de l'Index annoncé comme tel. La règle s'affiche à côté de chaque signal ; la liste complète est dans la <a href="/methodologie#seuils">méthodologie</a>.</li>
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

      {memeRayon.length > 0 && (
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Autres marques du même secteur</h2>
          <p className="muted small">D'autres groupes, par ordre alphabétique (aucun classement) : comparez les fiches.</p>
          <Vignettes items={memeRayon.map((m) => ({ slug: m.slug, name: m.group ? `${m.name} · ${m.group}` : m.name }))} />
        </section>
      )}

      <CorrectionForm entitySlug={carte.slug} indicators={carte.piliers.flatMap((p) => p.faits.map((f) => ({ code: f.code, name: f.nom })))} />
    </main>
  );
}
