import { marqueAnimale, marquesDocumentees, raisonVide, resumeGroupe, type Carte, type Fait, type MarqueAnimale, type MarqueDuGroupe, type Pilier, type Solidite } from "@/lib/carte";
import type { ListeProduits, OwnershipProof, ProduitLu, ProduitScanne } from "@/lib/data";
import { logoDe } from "@/lib/logos";
import { EN_SAVOIR_PLUS, REPERES, type Signal } from "@/lib/seuils";
import { CorrectionForm } from "@/components/CorrectionForm";
import { DepotEtiquette } from "@/components/DepotEtiquette";
import type { AlternativesPilier } from "@/lib/alternatives-piliers";
import { PiliersPastilles, type PastillePilier } from "@/components/PiliersPastilles";

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

type Motif = { pilier: string; s: Signal; code?: string; qui: string };
const EMOJI = { alerte: "🔴", vigilance: "⚠️" } as const;

/**
 * Avertissement en tête de fiche, façon paquet de cigarettes : fermé par défaut (« AVERTISSEMENT 🔴 4
 * ⚠️ 1 »), ouvert au clic. Chaque motif dit qui il vise (la marque ou son groupe) et ouvre la preuve
 * dans son pilier.
 */
function Avertissement({ items }: { items: Motif[] }) {
  if (!items.length) return null;
  const tries = [...items].sort((a, b) => (a.s.niveau === "alerte" ? 0 : 1) - (b.s.niveau === "alerte" ? 0 : 1));
  const na = tries.filter((x) => x.s.niveau === "alerte").length;
  const nv = tries.length - na;
  return (
    <details className="ci-avert">
      <summary aria-label={`Avertissement : ${[na ? pl(na, "alerte", "alertes") : "", nv ? pl(nv, "vigilance", "vigilances") : ""].filter(Boolean).join(", ")}`}>
        <span className="ci-avert-t">AVERTISSEMENT</span>
        <span className="ci-avert-n">{na > 0 && <>{EMOJI.alerte} {na}</>}{na > 0 && nv > 0 && "   "}{nv > 0 && <>{EMOJI.vigilance} {nv}</>}</span>
        <Chevron />
      </summary>
      <ul>
        {tries.map((x, i) => (
          <li key={i}>
            <a href={`#pilier-${x.pilier}${x.code ? `:${x.code}` : ""}`} title={`Seuil : ${x.s.regle}`}>
              <span aria-hidden="true">{EMOJI[x.s.niveau]}</span>
              <span><strong>{x.qui}</strong> — {x.s.motif}</span>
            </a>
          </li>
        ))}
      </ul>
    </details>
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
  ANI_EXPLOITATION: "🥩", ANI_ANIMAL_FREE: "🌱", ANI_OFFRE_VEGETALE: "🥦", ANI_HUNTING_FISHING: "🎣", ANI_FUR_FREE: "🦊", ANI_BBFAW_TIER: "📊", ANI_ANGORA_MOHAIR: "🐇",
  ANI_DOWN_RDS: "🪶", ANI_EXOTIC_SKINS: "🐊", ANI_LEATHER_TRACE: "👞", ANI_SLAUGHTER: "🚚", ANI_TESTING: "🧪", ANI_WOOL_MULESING: "🐑",
  ENV_CDP_CLIMATE: "📋", ENV_GHG_INTENSITY: "🏭", ENV_GHG_TREND: "📉", ENV_GREENWASHING: "🎭", ENV_MATERIAL_CHANGE: "🧵", ENV_SBTI_VALIDATED: "🎯",
  ENV_SCOPE3_DISCLOSED: "🌐", ENV_TAXONOMY_CAPEX: "🏗️",
  PLA_POLLUTER: "🗑️", PLA_RECYCLED: "♻️", PLA_RECYCLABLE: "📦", PLA_REDUCTION: "🧴",
  WAT_CDP: "📋", ENV_CDP_FORESTS: "🌳", WAT_CONTROVERSY: "🏜️", WAT_INTENSITY: "🚰", WAT_WITHDRAWAL_INTENSITY: "💧",
  LAB_CEO_PAY_RATIO: "💰", LAB_PAY_RATIO_MAXMIN: "📏", LAB_EGAPRO_INDEX: "⚖️", LAB_GENDER_PAYGAP: "👩‍💼", LAB_LITIGATION_RATE: "🧑‍⚖️", LAB_LIVING_WAGE: "🏠",
  SUP_BHRRC_ALLEG: "📣", SUP_FTI_SCORE: "🔍", SUP_KNOWTHECHAIN: "⛓️", SUP_LIVING_WAGE: "🪙", SUP_SUPPLIER_LIST: "📃", SUP_VIGILANCE_PLAN: "🛡️",
  GOV_BCORP: "✅", GOV_BOARD_GENDER: "👩", GOV_BOARD_INDEP: "🪑", GOV_SANCTIONS: "🔨", GOV_CJIP: "📜",
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

const majuscule = (t: string) => t[0].toUpperCase() + t.slice(1);

/**
 * Un indicateur, en deux temps : d'abord le fait (icône et nom, valeur en grand, repère, source en
 * une ligne), puis, sur demande, le détail (seuil retenu, solidité, note, citation, lien).
 */
function CarteIndicateur({ f }: { f: Fait }) {
  const p = f.preuve;
  const ton = f.signal?.niveau ?? (f.etat === "documente" ? "documente" : "signale");
  // Avec un signal, la valeur et le seuil retenu disent déjà le repère.
  const repere = !f.signal && f.etat === "documente" ? REPERES[f.code] : null;
  const obligation = f.etat !== "documente" && f.obligation.length > 0 ? f.obligation.join(", ") : null;
  const savoir = f.etat === "documente" ? EN_SAVOIR_PLUS[f.code] ?? null : null;
  const aDetail = !!(p || f.note || f.signal || obligation || savoir);
  return (
    <article className={`ci-ind ci-ind-${ton}`} data-indicateur={f.code}>
      <header className="ci-ind-h">
        <span className="ci-ind-ico" aria-hidden="true">{ICONE_IND[f.code] ?? "•"}</span>
        <span className="ci-ind-nom">{f.nom}</span>
        {f.signal && <span className={`ci-tag ci-tag-${f.signal.niveau}`}>{f.signal.niveau === "alerte" ? "⚠️ Alerte" : "🟠 Vigilance"}</span>}
      </header>
      <div className="ci-ind-val">
        {majuscule(f.valeur)}
        {f.contexte && <span className="ci-badge" title="Donnée de contexte : ni bonne ni mauvaise en soi">contexte</span>}
        {p?.conteste && <span className="ci-badge">contesté</span>}
      </div>
      {repere && <div className="ci-ind-rep">{repere}</div>}
      {aDetail && (
        <details className="ci-det">
          <summary>
            <span className="ci-det-src">{p ? `${p.source} · ${dfr(p.date)}` : "Détail"}</span>
            <span className={`ci-det-btn${savoir ? " ci-det-savoir" : ""}`} aria-hidden="true" />
          </summary>
          <div className="ci-det-corps">
            {savoir && <p className="ci-savoir"><strong>En savoir plus · </strong>{savoir}</p>}
            {f.signal && <div className={`ci-ind-seuil ci-seuil-${f.signal.niveau}`}>Seuil retenu : {f.signal.regle}</div>}
            {obligation && <div className="ci-ind-txt">Obligation : {obligation}</div>}
            {f.note && <div className="ci-ind-note">{f.note}</div>}
            {p && (
              <div className="ci-ind-src">
                <Solidite s={p.solidite} />
                <span>{p.source}, {dfr(p.date)}{!p.dateEvenement && " (relevé)"}</span>
                {p.reprisDe && <span className="ci-badge">{p.reprisDe.startsWith("la filiale") ? `donnée de ${p.reprisDe}` : `donnée du groupe ${p.reprisDe}`}</span>}
              </div>
            )}
            {p?.citation && (
              <div className="ci-cit-bloc">
                <blockquote>{p.citation}</blockquote>
                {p.citation.length > 240 && (
                  <details className="ci-cit-toute">
                    <summary><span className="ci-plus-t">Lire toute la citation</span><span className="ci-moins-t">Raccourcir la citation</span></summary>
                  </details>
                )}
              </div>
            )}
            {p?.copie && <div className="ci-ind-txt ci-small ci-faint">📄 Citation vérifiée mot pour mot sur une copie enregistrée de la page : le site refuse les robots de vérification.</div>}
            {p?.url && (
              <a className="ci-det-lien" href={p.url} target="_blank" rel="noopener noreferrer">
                Ouvrir la source ↗
              </a>
            )}
          </div>
        </details>
      )}
    </article>
  );
}

/** Les indicateurs sans information, regroupés en une ligne (dépliée d'office si rien d'autre n'est documenté). */
function SansInformation({ faits, toutVide }: { faits: Fait[]; toutVide: boolean }) {
  const n = faits.length;
  return (
    <details className="ci-vides-g" open={toutVide}>
      <summary>
        <span>{toutVide ? "Rien de documenté pour l'instant" : `${n} indicateur${n > 1 ? "s" : ""} sans information`}</span>
        <span className="ci-det-btn ci-vides-btn" aria-hidden="true" />
      </summary>
      <ul className="ci-vides-l">
        {faits.map((f) => {
          const [statut, raison] = raisonVide(f);
          return (
            <li key={f.code}>
              <strong><span aria-hidden="true">{ICONE_IND[f.code] ?? "•"}</span> {f.nom}</strong>
              <span className="ci-small">{statut}. {majuscule(raison)}.{f.note ? ` ${f.note}` : ""}</span>
            </li>
          );
        })}
      </ul>
    </details>
  );
}

/** Les indicateurs d'un niveau, tous présents, même vides (décision de l'éditeur, 15/10/2026). */
function Faits({ faits, cacherPresume }: { faits: Fait[]; cacherPresume?: boolean }) {
  const fs = faits
    .filter((f) => !(cacherPresume && f.etat === "presume"))
    .sort((a, b) => rang(a) - rang(b) || (b.preuve?.date ?? "").localeCompare(a.preuve?.date ?? ""));
  const pleins = fs.filter((f) => f.etat !== "aucune_info");
  const vides = fs.filter((f) => f.etat === "aucune_info");
  return (
    <>
      {pleins.length > 0 && (
        <div className="ci-inds">
          {pleins.map((f) => (
            <CarteIndicateur key={f.code} f={f} />
          ))}
        </div>
      )}
      {vides.length > 0 && <SansInformation faits={vides} toutVide={!pleins.length} />}
    </>
  );
}

/** Alternatives du pilier : marques du même rayon, d'un autre groupe, qui remplissent un critère affiché. */
function EncartAlternatives({ a }: { a?: AlternativesPilier[string] }) {
  return (
    <section className="ci-alt">
      <div className="ci-alt-t">🔄 Alternatives dans le même secteur</div>
      {a ? (
        <>
          <p className="ci-small ci-faint">Marques d'autres groupes {a.critere}. Aucune note : c'est ce critère, et lui seul, qui les fait figurer ici.</p>
          <div className="ci-alt-l">
            {a.marques.map((m) => (
              <a key={m.slug} className={`ci-alt-m${m.second ? "" : " ci-alt-fort"}`} href={`/entreprise/${m.slug}`}>
                <Logo slug={m.slug} nom={m.nom} taille={26} />
                <span>{m.nom}{m.groupe && <span className="ci-faint"> · {m.groupe}</span>}{m.second && <span className="ci-faint"> · produits végétaux</span>}</span>
              </a>
            ))}
            {a.autres > 0 && <span className="ci-small ci-faint">et {pl(a.autres, "autre", "autres")}</span>}
          </div>
        </>
      ) : (
        <p className="ci-small ci-faint">Aucune marque du même secteur ne remplit encore le critère de ce pilier dans nos données.</p>
      )}
      <a className="ci-small ci-lien" href="#contribuer">Vous connaissez une meilleure alternative ? Proposez-la →</a>
    </section>
  );
}

/** Une section de niveau (groupe, marque, produits) dans un pilier déplié. */
function Niveau({ icone, titre, aide, children }: { icone: string; titre: React.ReactNode; aide: string; children: React.ReactNode }) {
  return (
    <section className="ci-niv-sec">
      <div className="ci-niv-t" title={aide}>
        {icone} {titre}
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

/** Nom de pilier raccourci pour une pastille (« Chaîne d'appro & droits humains » → « Chaîne d'appro »). */
function nomCourt(nom: string): string {
  return nom.replace(/\s*\(.*\)\s*$/, "").split(" & ")[0].trim();
}

/** État d'un pilier pour sa pastille : alerte, vigilance ou rien (d'après tous ses indicateurs). */
function etatPilier(p: Pilier, mg: MarquesGroupe, estMarque: boolean): "alerte" | "vigilance" | null {
  const k = p.cle;
  // Fiche d'un groupe : sans preuve propre au groupe, le pilier animal se lit d'après ses marques.
  const r = p.code === "ANI" && !estMarque && mg ? resumeGroupe(mg.marques.map(marqueAnimale)) : null;
  const niveauGroupe = !!r && (r.exploitation > 0 || r.vegetale > 0) && k?.etat !== "documente";
  // Exploitation animale : alerte quel que soit le classement BBFAW (décision de l'éditeur, 15/10/2026).
  if (p.code === "ANI" && niveauGroupe && r!.exploitation > 0) return "alerte";
  const signaux = p.faits.filter((f) => f.signal && !(niveauGroupe && f.etat === "presume")).map((f) => f.signal!.niveau);
  if (signaux.includes("alerte")) return "alerte";
  if (signaux.includes("vigilance")) return "vigilance";
  return p.faits.some((f) => f.code === "ANI_EXPLOITATION" && f.etat === "presume") && !niveauGroupe ? "vigilance" : null;
}

/** Contenu d'un pilier ouvert : niveaux groupe, marque, produits, puis alternatives. */
function CorpsPilier({ p, mg, estMarque, nom, slug, vegane = false, alternatives }: { p: Pilier; mg: MarquesGroupe; estMarque: boolean; nom: string; slug: string; vegane?: boolean; alternatives?: AlternativesPilier }) {
  const k = p.cle;
  const r = p.code === "ANI" && !estMarque && mg ? resumeGroupe(mg.marques.map(marqueAnimale)) : null;
  const niveauGroupe = !!r && (r.exploitation > 0 || r.vegetale > 0) && k?.etat !== "documente";
  const g = p.faits.filter((f) => f.niveau === "groupe");
  const m = p.faits.filter((f) => f.niveau === "marque");
  const pr = p.faits.filter((f) => f.niveau === "produit");
  return (
    <>
      <div className="ci-pan-t">
        <span aria-hidden="true">{ICONE[p.code]}</span>
        <span>{p.nom.toUpperCase()}</span>
        <span className="ci-pan-n">{p.documentes} sur {p.total} renseignés</span>
      </div>
      <div className="ci-body">
        {p.solidite && <p className="ci-faint ci-small">Ce pilier repose sur des {SOLIDITE_PILIER[p.solidite]}.</p>}
        {(g.length > 0 || (p.code === "ANI" && estMarque && mg && !vegane)) && (
          <Niveau
            icone="🏢"
            titre={estMarque ? (mg ? <>Groupe <a href={`/entreprise/${mg.groupe.slug}`}>{mg.groupe.name}</a></> : <>Groupe</>) : <>Groupe {nom}</>}
            aide={estMarque ? "ce que publie le groupe ; la marque le reprend" : "ce que publie le groupe"}
          >
            {p.code === "ANI" && estMarque && mg && !vegane && <ResumeAnimal mg={mg} slug={slug} estGroupe={false} />}
            <Faits faits={g} cacherPresume={niveauGroupe} />
          </Niveau>
        )}
        {estMarque && m.length > 0 && (
          <Niveau icone="🏷️" titre={<>Marque {nom}</>} aide="ce qui est prouvé pour la marque elle-même">
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
        <EncartAlternatives a={alternatives?.[p.code]} />
      </div>
    </>
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
  produitsLus = [],
  alternatives = {},
  scan = null,
}: {
  carte: Carte;
  estGroupe: boolean;
  proprietaire: { slug: string; name: string } | null;
  preuvesPropriete: OwnershipProof[];
  memeRayon: { slug: string; name: string; group: string | null }[];
  marques: { slug: string; name: string }[];
  marquesGroupe?: MarquesGroupe;
  estMarque?: boolean;
  produits?: ListeProduits | null;
  /** Fiches produits lues sur le site de la marque (ingrédients recopiés, statut). */
  produitsLus?: ProduitLu[];
  /** Alternatives de chaque pilier (critère affiché). */
  alternatives?: AlternativesPilier;
  /** Produit scanné (page /code/…) : il s'affiche en tête, avec la façon dont la marque a été reconnue. */
  scan?: { produit: ProduitScanne; correspondance: "exacte" | "approchee" | "proprietaire"; nomLu: string; phrase: string } | null;
}) {
  const nomPilier = new Map(carte.piliers.map((p) => [p.code, p.nom]));
  // Fiche d'un groupe : l'exploitation animale se lit d'après ses marques (comme la ligne du pilier).
  const rg = !estMarque && marquesGroupe ? resumeGroupe(marquesGroupe.marques.map(marqueAnimale)) : null;
  const qui = (niveau: string) => (niveau === "groupe" && proprietaire ? proprietaire.name : carte.nom);
  const signaux = carte.signaux.flatMap((f): Motif[] => {
    if (f.code === "ANI_EXPLOITATION" && f.etat === "presume" && rg && (rg.exploitation > 0 || rg.vegetale > 0)) return [];
    return [{ pilier: f.pilier, s: f.signal!, code: f.code, qui: qui(f.niveau) }];
  });
  if (rg && rg.exploitation > 0 && !carte.signaux.some((f) => f.code === "ANI_EXPLOITATION" && f.etat === "documente")) {
    signaux.unshift({ pilier: "ANI", qui: carte.nom, s: { niveau: "alerte", motif: `produits issus de l'exploitation animale chez ${rg.exploitation} marque${rg.exploitation > 1 ? "s" : ""} sur ${rg.total}`, regle: "un seul produit d'origine animale suffit" } });
  }
  const pastilles: PastillePilier[] = carte.piliers.map((p) => ({
    code: p.code, nom: nomCourt(p.nom), icone: ICONE[p.code] ?? "•", teinte: TEINTE[p.code] ?? "#6c3bff",
    compte: `${p.documentes}/${p.total}`, vide: p.documentes === 0, signal: etatPilier(p, marquesGroupe, estMarque),
  }));
  const panneaux = Object.fromEntries(carte.piliers.map((p) => [p.code,
    <CorpsPilier key={p.code} p={p} mg={marquesGroupe} estMarque={estMarque} nom={carte.nom} slug={carte.slug} vegane={carte.vegane} alternatives={alternatives} />]));
  const quantite = scan?.produit.quantite && /\d\s*[a-zA-Zµ]/.test(scan.produit.quantite) ? ` · ${scan.produit.quantite}` : "";
  return (
    <main className="ci">
      <a className="muted small" href="/">← rechercher une autre marque</a>
      {/* Zone 1 : identité du produit, de la marque et de son groupe ; avertissement. */}
      <section className="ci-zone ci-zone-id" aria-label="Identité et alertes">
        {scan && (
          <figure className="ci-photo">
            {scan.produit.image ? <img src={scan.produit.image} alt={`Photo du produit ${scan.produit.nom}`} /> : <span className="ci-prod-vide" aria-hidden="true">🛒</span>}
            <figcaption>
              <strong>{scan.produit.nom}{quantite}</strong>
              <span className="ci-small ci-faint"> · code {scan.produit.code} · {scan.phrase} · d'après <a className="ci-lien" href={scan.produit.lien} target="_blank" rel="noopener noreferrer">{scan.produit.base} ↗</a></span>
            </figcaption>
          </figure>
        )}
        {!scan && logoDe(carte.slug) && (
          <figure className="ci-photo ci-photo-logo">
            <img src={logoDe(carte.slug)!.src} alt={`Logo ${carte.nom}`} title={`Logo : ${logoDe(carte.slug)!.origine}`} />
          </figure>
        )}
        <div className="ci-head">
          <span className="ci-head-logo"><Logo slug={carte.slug} nom={carte.nom} taille={52} groupe={estGroupe} /></span>
          <div className="ci-head-t">
            <div className="ci-k">{estGroupe ? "GROUPE" : "MARQUE"}</div>
            <h1>{carte.nom}</h1>
            {proprietaire ? (
              <div className="ci-own">
                <a className="ci-own-g" href={`/entreprise/${proprietaire.slug}`}><Logo slug={proprietaire.slug} nom={proprietaire.name} taille={22} groupe /><strong>{proprietaire.name}</strong></a>
                <details className="ci-info">
                  <summary aria-label="À quoi sert ce groupe ?">ⓘ</summary>
                  <span className="ci-bulle">
                    {proprietaire.name} possède la marque : c'est ce groupe qui reçoit l'argent de vos achats
                    {carte.chaine.length > 2 && <> (via {carte.chaine.slice(1, -1).join(" → ")})</>}.
                  </span>
                </details>
              </div>
            ) : (
              estGroupe && marques.length > 0 && <div className="ci-own">{pl(marques.length, "marque suivie", "marques suivies")}</div>
            )}
          </div>
        </div>
        <Avertissement items={signaux} />
      </section>

      {/* Zone 2 : les piliers, en pastilles. */}
      <section className="ci-zone ci-zone-piliers" aria-labelledby="titre-piliers">
        <h2 id="titre-piliers" className="ci-zone-t">Pilier par pilier</h2>
        <PiliersPastilles pastilles={pastilles} panneaux={panneaux} />
      </section>

      {/* Zone 3 : informations complémentaires. */}
      <section className="ci-zone ci-zone-plus" aria-labelledby="titre-plus">
        <h2 id="titre-plus" className="ci-zone-k">Informations complémentaires</h2>
        <p className="ci-foot">
          {carte.documentes} information(s) documentée(s) sur {carte.total} recherchées · aucune note, que des faits sourcés.
          La date indiquée est celle de l'événement quand elle est connue, sinon celle de notre relevé.
        </p>
        <details className="panel ci-sources">
          <summary><strong>📜 Toutes les sources</strong> <span className="muted small">— chronologie complète ({carte.chronologie.length})</span></summary>
          {carte.chronologie.length ? (
            <ol className="ci-tl">
              {carte.chronologie.map((f) => (
                <Entree key={f.code} f={f} avecPilier nomPilier={nomPilier.get(f.pilier)} />
              ))}
            </ol>
          ) : (
            <p className="ci-faint">Aucune information documentée pour l'instant.</p>
          )}
        </details>

      {estGroupe && marques.length > 0 && (
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Ses marques <span className="ci-sec-n">{marques.length}</span></h2>
          <p className="muted small">Marques détenues par {carte.nom}, directement ou par ses filiales ; chacune a sa fiche.</p>
          <Vignettes items={marques} />
        </section>
      )}

      {!estMarque && produitsLus.length > 0 && (
        // Groupe qui vend sous son propre nom (Decathlon) : les fiches lues sur son site, sans les bases ouvertes.
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Ses produits</h2>
          <ProduitsLus produits={produitsLus} />
        </section>
      )}

      {estMarque && (
        <section className="panel ci-sec">
          <h2 className="ci-sec-t">Ses produits {produits && <span className="ci-sec-n">{produits.total}</span>}</h2>
          {produitsLus.length > 0 && <ProduitsLus produits={produitsLus} />}
          <DepotEtiquette slug={carte.slug} marque={carte.nom} />
          {produits ? (
            <>
              <p className="muted small">
                Les produits les plus scannés en France, d'après{" "}
                {produits.bases.map((b, i) => (
                  <span key={b.nom}>{i > 0 && (i === produits.bases.length - 1 ? " et " : ", ")}<a className="ci-lien" href={b.lien} target="_blank" rel="noopener noreferrer">{b.nom} ↗</a></span>
                ))}{" "}
                (bases collaboratives sous licence ouverte). Ils aident à reconnaître la marque en magasin ; ce ne sont pas des preuves.
              </p>
              <div className="ci-prods">
                {produits.produits.map((x) => (
                  <a key={x.code} className="ci-prod" href={x.lien} target="_blank" rel="noopener noreferrer">
                    {x.image ? <img src={x.image} alt="" loading="lazy" /> : <span className="ci-prod-vide" aria-hidden="true">🛒</span>}
                    <span>{x.nom}</span>
                  </a>
                ))}
              </div>
            </>
          ) : (
            <p className="muted small">Aucun produit de cette marque n'est encore recensé en France dans les bases ouvertes (Open Food Facts, Open Beauty Facts, Open Products Facts, Open Pet Food Facts). Les vêtements, par exemple, n'y figurent presque pas.</p>
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

      <div id="contribuer" />
      <CorrectionForm entitySlug={carte.slug} indicators={carte.piliers.flatMap((p) => p.faits.map((f) => ({ code: f.code, name: f.nom })))} />
      </section>
    </main>
  );
}


const STATUT_PRODUIT: Record<ProduitLu["statut"], [string, string]> = {
  ingredient_animal: ["ci-alerte", "Ingrédient d'origine animale"],
  aucun_ingredient_animal_declare: ["ci-aucune_info", "Aucun ingrédient animal dans la liste lue"],
  vegetal_declare: ["ci-vegetal", "Présenté comme végétal par la marque"],
  vegetal_certifie: ["ci-vegetal", "Végétal, label d'un tiers"],
};

/** Mêmes statuts pour une composition de vêtement : on parle de matières, pas d'ingrédients. */
const STATUT_MATIERE: Record<ProduitLu["statut"], [string, string]> = {
  ingredient_animal: ["ci-alerte", "Matière d'origine animale"],
  aucun_ingredient_animal_declare: ["ci-aucune_info", "Aucune matière animale dans la composition lue"],
  vegetal_declare: ["ci-vegetal", "Présenté comme sans matière animale par la marque"],
  vegetal_certifie: ["ci-vegetal", "Sans matière animale, label d'un tiers"],
};
const statutDe = (p: ProduitLu) => (p.nature === "composition" ? STATUT_MATIERE : STATUT_PRODUIT)[p.statut];
/** Vocabulaire selon la nature des fiches : ingrédients (alimentation, cosmétique) ou matières (vêtements). */
const mots = (textile: boolean) => textile
  ? { Lus: "Compositions lues", un: "une matière d'origine animale", sans: "sans matière animale", liste: "« Aucune matière animale dans la composition lue » ne vaut que pour les pièces lues : la marque peut en utiliser ailleurs (laine, cuir, soie, duvet…)." }
  : { Lus: "Ingrédients lus", un: "un ingrédient d'origine animale", sans: "sans ingrédient animal", liste: "« Aucun ingrédient animal dans la liste lue » ne prouve pas qu'un produit est végétal : certains additifs ou arômes peuvent être d'origine animale." };

/** Ingrédients (ou compositions) lus sur les fiches produits du site de la marque, recopiés et datés. */
const ORDRE_PRODUIT: Record<ProduitLu["statut"], number> = { vegetal_certifie: 0, vegetal_declare: 1, aucun_ingredient_animal_declare: 2, ingredient_animal: 3 };

function LigneProduit({ p }: { p: ProduitLu }) {
  const [cls, txt] = statutDe(p);
  return (
    <li>
      {p.origine === "etiquette" ? <span>{p.nom}</span> : <a className="ci-lien" href={p.url} target="_blank" rel="noopener noreferrer">{p.nom} ↗</a>}{" "}
      <span className={cls}>{txt}{p.animaux.length ? ` : ${p.animaux.join(", ")}` : ""}</span>
      {p.origine === "etiquette" && (
        <div className="ci-small ci-faint">
          📷 <a className="ci-lien" href={p.url} target="_blank" rel="noopener noreferrer">photo de l'étiquette</a>
          {p.achat.date || p.achat.lieu ? <> · achetée{p.achat.date ? ` le ${dfr(p.achat.date)}` : ""}{p.achat.lieu ? ` (${p.achat.lieu})` : ""}</> : null}
          {" "}· envoyée par un lecteur, liste recopiée et relue
        </div>
      )}
      {p.ingredients && <details className="ci-small"><summary>{p.origine === "etiquette" ? "Ingrédients recopiés de l'étiquette" : p.nature === "composition" ? `Composition (lue le ${dfr(p.date)})` : `Ingrédients (lus le ${dfr(p.date)})`}</summary>« {p.ingredients} »{p.douteux.length ? <> — d'origine possiblement animale, non tranché : {p.douteux.join(", ")}</> : null}</details>}
    </li>
  );
}

function ProduitsLus({ produits: tous }: { produits: ProduitLu[] }) {
  const produits = [...tous].sort((a, b) => ORDRE_PRODUIT[a.statut] - ORDRE_PRODUIT[b.statut] || a.nom.localeCompare(b.nom, "fr"));
  const sans = produits.filter((p) => p.statut !== "ingredient_animal");
  const avec = produits.filter((p) => p.statut === "ingredient_animal");
  const animaux = avec.length;
  const m = mots(produits.every((p) => p.nature === "composition"));
  if (sans.length && avec.length) {
    return (
      <div className="ci-prods-lus">
        <p className="muted small">{m.Lus} sur {pl(produits.length, "produit", "produits")} (fiches du site de la marque ou étiquettes photographiées), dont {animaux} avec {m.un}.</p>
        <div className="ci-prods-sans">
          <div className="ci-prods-sans-t">🌱 Chez cette marque, {m.sans}</div>
          <p className="ci-small ci-faint">« Végétal » : la marque le dit ou un label l'atteste. {m.liste}</p>
          <ul className="ci-prods-liste">{sans.map((p) => <LigneProduit key={p.url} p={p} />)}</ul>
        </div>
        <details className="ci-small" style={{ marginTop: 8 }}>
          <summary>{pl(avec.length, "produit", "produits")} avec {m.un}</summary>
          <ul className="ci-prods-liste">{avec.map((p) => <LigneProduit key={p.url} p={p} />)}</ul>
        </details>
      </div>
    );
  }
  return (
    <div className="ci-prods-lus">
      <p className="muted small">
        {m.Lus} sur {pl(produits.length, "fiche produit", "fiches produits")} du site de la marque{animaux ? `, dont ${animaux} avec ${m.un}` : ""}.
        {m.liste}
      </p>
      <ul className="ci-prods-liste">
        {produits.map((p) => {
          const [cls, txt] = statutDe(p);
          return (
            <li key={p.url}>
              <a className="ci-lien" href={p.url} target="_blank" rel="noopener noreferrer">{p.nom} ↗</a>{" "}
              <span className={cls}>{txt}{p.animaux.length ? ` : ${p.animaux.join(", ")}` : ""}</span>
              {p.preuveVegetale && <span className="ci-small"> · {p.preuveVegetale}</span>}
              {p.ingredients && <details className="ci-small"><summary>{p.nature === "composition" ? "Composition" : "Ingrédients"} (lu{p.nature === "composition" ? "e" : "s"} le {dfr(p.date)})</summary>« {p.ingredients} »{p.douteux.length ? <> — d'origine possiblement animale, non tranché : {p.douteux.join(", ")}</> : null}</details>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
