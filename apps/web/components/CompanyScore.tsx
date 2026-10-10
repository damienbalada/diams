import { computeScore, type DimensionResult, type ScoreResult } from "@/lib/scoring";
import type { Alternative, ScorePayload } from "@/lib/data";
import { CorrectionForm } from "@/components/CorrectionForm";
import { Tip } from "@/components/Tip";

// Explication de chaque tier de source (fiabilité de la preuve, pas jugement).
const tierExplain: Record<string, string> = {
  regulatory: "Source réglementaire (obligation légale, régulateur, justice) — fiabilité maximale.",
  audited_ngo: "ONG auditée / référentiel reconnu — fiabilité élevée.",
  press: "Presse ou source publique — fiabilité moyenne, à recouper.",
  crowd: "Contribution / source militante — fiabilité faible, traitée comme signalement.",
};

const gradeColor: Record<string, string> = {
  A: "var(--a)", B: "var(--b)", C: "var(--c)", D: "var(--d)", E: "var(--e)",
};
const pct = (x: number) => `${Math.round(x * 100)}%`;

// Date ISO -> "JJ/MM/AAAA" (affichage FR).
const frDate = (iso?: string | null) => {
  if (!iso) return null;
  const [y, m, d] = iso.split("-");
  return d ? `${d}/${m}/${y}` : `${m}/${y}`;
};
// Une preuve est "ancienne" au-delà de 3 ans (décote totale à 5 ans).
const STALE_BEFORE = new Date(Date.now() - 3 * 365 * 24 * 3600 * 1000)
  .toISOString()
  .slice(0, 10);

// Raison du plafond d'un pilier (gate), par dimension.
const capReason: Record<string, string> = {
  ANI: "exploitation animale",
  PLA: "pollueur plastique majeur",
  GEO: "lobbying climat désaligné",
};

export function CompanyScore({
  payload,
  group = null,
  alternatives = [],
}: {
  payload: ScorePayload;
  group?: { slug: string; name: string; result: ScoreResult } | null;
  alternatives?: Alternative[];
}) {
  // Pondération fixe : profil renvoyé par la base (défaut « Équilibré »).
  const result = computeScore(payload);
  const chain = payload.ownership_chain ?? [];
  const minConf = payload.params?.min_confidence_to_publish ?? 0.3;

  // Comparaison marque ↔ groupe propriétaire (deux notes indépendantes depuis
  // v0.5) : piliers notés des deux côtés qui divergent nettement (≥ 20 points).
  // Ceux où la marque fait bien mieux que son groupe (≥ 30 points) déclenchent
  // une alerte « circuit de l'argent ».
  const groupDims = new Map((group?.result.dimensions ?? []).map((d) => [d.dimension_code, d]));
  const divergences = group
    ? result.dimensions
        .map((d) => ({ d, g: groupDims.get(d.dimension_code) }))
        .filter((x) => x.g && x.d.rated && x.g.rated && Math.abs(x.d.score - x.g!.score) >= 0.2)
        .map((x) => ({
          code: x.d.dimension_code,
          name: x.d.name,
          markGrade: x.d.grade,
          groupGrade: x.g!.grade,
          diff: x.d.score - x.g!.score,
        }))
    : [];
  const betterThanGroup = divergences.filter((x) => x.diff >= 0.3);
  // code indicateur -> nom lisible (fourni par compute_score_input)
  const indicatorNames = new Map(
    payload.applicableIndicators.map((i) => [i.code, i.name ?? i.code]),
  );

  // Piliers NON PERTINENTS pour ce secteur (aucun indicateur applicable) :
  // à distinguer d'un pilier applicable mais sans donnée (lui, noté 0).
  const applicableDims = new Set(payload.applicableIndicators.map((i) => i.dimension_code));
  const notApplicable = (payload.dimensions ?? []).filter((d) => !applicableDims.has(d.code));

  return (
    <main className="fiche-stack">
      <a className="muted small" href="/">← toutes les entreprises</a>

      {/* En-tête : note ET fiabilité, séparées */}
      <div className="panel">
        <div className="row between wrap">
          <div>
            <h1 style={{ marginBottom: 2 }}>{payload.entity.name}</h1>
            <div className="muted small">
              {chain.length > 1 ? chain.join("  →  ") : "Groupe"}
            </div>
            {result.last_observed && (
              <div className="muted small" style={{ marginTop: 2 }}>
                Dernière mise à jour · {frDate(result.last_observed)}
              </div>
            )}
          </div>
          <div className="row" style={{ gap: 20 }}>
            {/* Sous le seuil de fiabilité, aucune lettre (Règle 5) : une note qui
                repose sur trop peu de preuves ne doit pas se lire comme un verdict. */}
            <div style={{ textAlign: "center" }}>
              {result.publishable ? (
                <>
                  <div className={`grade grade-${result.grade}`}>{result.grade}</div>
                  <div className="muted small" style={{ marginTop: 4 }}>Note · {pct(result.score)}</div>
                </>
              ) : (
                <>
                  <div className="grade grade-none" title="Pas de note publiée : fiabilité sous le seuil.">?</div>
                  <div className="muted small" style={{ marginTop: 4 }}>Pas de note</div>
                </>
              )}
            </div>
            <div style={{ minWidth: 160 }}>
              <div className="small">
                Fiabilité
                <Tip label="Comment lire la fiabilité ?">
                  La fiabilité mesure la <strong>complétude et la fraîcheur des preuves</strong>, pas la
                  qualité de l'entreprise. Une donnée manquante la fait toujours baisser. Elle ne compte
                  0 dans la <strong>note</strong> que si sa publication est <strong>obligatoire</strong> pour
                  cette entité (index Égapro, CSRD, devoir de vigilance…) : ne pas publier ce que la loi
                  impose est un choix. Sous {pct(minConf)} de fiabilité, aucune note n'est affichée :
                  « on ne sait pas encore », pas « c'est mauvais ».
                </Tip>
              </div>
              <div className="meter" style={{ margin: "4px 0" }}>
                <span style={{ width: pct(result.confidence) }} />
              </div>
              <div className="muted small">
                {pct(result.confidence)} {result.publishable ? "" : `· données insuffisantes (seuil ${pct(minConf)})`}
              </div>
            </div>
          </div>
        </div>

        {/* Méta-scores (seulement quand la note est publiée) */}
        {result.publishable && result.groups.some((g) => g.rated) && (
          <div className="row wrap" style={{ marginTop: 14, gap: 10 }}>
            {result.groups.filter((g) => g.rated).map((g) => (
              <span key={g.code} className="badge" style={{ borderColor: gradeColor[g.grade], color: gradeColor[g.grade] }}>
                {g.name} : {g.grade} ({pct(g.score)})
              </span>
            ))}
          </div>
        )}

      </div>

      {/* Encart marque ↔ groupe propriétaire */}
      {group && (
        <div className="panel" style={{ borderColor: "#3a4256" }}>
          <div className="row between wrap" style={{ gap: 8 }}>
            <div>
              <strong>
                🏭 Groupe propriétaire : <a href={`/entreprise/${group.slug}`} style={{ textDecoration: "underline" }}>{group.name}</a>
              </strong>
              <div className="muted small">À qui va l'argent quand vous achetez cette marque.</div>
            </div>
            {group.result.publishable ? (
              <span className="badge" style={{ borderColor: gradeColor[group.result.grade], color: gradeColor[group.result.grade] }}>
                Note du groupe : {group.result.grade} ({pct(group.result.score)})
              </span>
            ) : (
              <span className="badge">Groupe : données insuffisantes ({pct(group.result.confidence)})</span>
            )}
          </div>

          <div className="muted small" style={{ marginTop: 10 }}>
            Cette marque est notée sur <strong>ses propres preuves</strong>. Le groupe {group.name} a sa propre
            fiche : sa fiscalité, sa gouvernance ou son lobbying s'y lisent, et c'est lui qui reçoit l'argent.
          </div>

          {divergences.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <div className="muted small" style={{ marginBottom: 4 }}>Écarts marque ↔ groupe :</div>
              {divergences.map((x) => (
                <div className="row between" key={x.code} style={{ padding: "5px 0", borderTop: "1px solid var(--border)" }}>
                  <span className="small">{x.name}</span>
                  <span className="row" style={{ gap: 6 }}>
                    <span className={`grade sm grade-${x.markGrade}`} style={{ width: 22, height: 22, fontSize: 11, borderRadius: 6 }}>{x.markGrade}</span>
                    <span className="muted small">marque</span>
                    <span className="muted">→</span>
                    <span className={`grade sm grade-${x.groupGrade}`} style={{ width: 22, height: 22, fontSize: 11, borderRadius: 6 }}>{x.groupGrade}</span>
                    <span className="muted small">groupe</span>
                  </span>
                </div>
              ))}
            </div>
          )}

          {betterThanGroup.length > 0 && (
            <span className="badge warn" style={{ marginTop: 12, display: "inline-block", whiteSpace: "normal", lineHeight: 1.4 }}>
              ⚠️ Cette marque est nettement mieux notée que son groupe sur : {betterThanGroup.map((x) => x.name).join(", ")}.
              Votre achat bénéficie tout de même au groupe {group.name}.
            </span>
          )}
        </div>
      )}

      {/* Détail par pilier */}
      {result.dimensions.map((d) => (
        <DimensionPanel key={d.dimension_code} d={d} names={indicatorNames} />
      ))}

      {/* Mieux notées dans le même secteur */}
      {alternatives.length > 0 && <Alternatives items={alternatives} />}

      {/* Boucle de contribution : signaler une erreur / une donnée manquante */}
      <CorrectionForm
        entitySlug={payload.entity.slug}
        indicators={payload.applicableIndicators.map((i) => ({
          code: i.code,
          name: i.name ?? i.code,
        }))}
      />

      {/* Piliers non pertinents pour le secteur (exclus du calcul, pas pénalisés) */}
      {notApplicable.length > 0 && (
        <div className="panel" style={{ borderStyle: "dashed" }}>
          <div className="muted small">
            <strong>Non applicable à ce secteur</strong> — exclu du calcul (ni bonus, ni malus) :{" "}
            {notApplicable.map((d) => d.name).join(", ")}.
          </div>
        </div>
      )}

      <p className="muted small" style={{ marginTop: 8 }}>
        Pondération : <strong>{payload.profile.name}</strong>. Méthodologie publique et versionnée.
      </p>
    </main>
  );
}

/**
 * Alternatives mieux notées du même secteur. Deux règles d'affichage tiennent la
 * promesse de neutralité :
 *  - la **fiabilité de l'alternative** est montrée, pas seulement sa note : une
 *    meilleure note mal documentée n'est pas un meilleur choix démontré ;
 *  - une alternative du **même groupe propriétaire** est signalée, parce que
 *    changer de marque n'y change pas le destinataire de l'argent.
 */
function Alternatives({ items }: { items: Alternative[] }) {
  return (
    <section className="panel">
      <h2 style={{ margin: "0 0 2px", fontSize: 17 }}>Mieux notées dans le même secteur</h2>
      <p className="muted small" style={{ margin: "0 0 12px" }}>
        Comparaison à périmètre égal (même secteur, mêmes indicateurs applicables).
        Les entités sous le seuil de fiabilité sont écartées : une absence de données
        n'est pas une vertu.
      </p>
      <div className="alt-list">
        {items.map((a) => (
          <a key={a.slug} className="alt-row" href={`/entreprise/${a.slug}`}>
            <span className={`grade sm grade-${a.grade}`}>{a.grade}</span>
            <span className="alt-main">
              <span className="alt-name">{a.name}</span>
              <small className="muted">
                {pct(a.score)} · fiabilité {pct(a.confidence)}
                {a.same_group && " · même groupe propriétaire"}
              </small>
            </span>
            <span className="alt-delta">+{Math.round(a.delta * 100)} pts</span>
          </a>
        ))}
      </div>
    </section>
  );
}

function DimensionPanel({ d, names }: { d: DimensionResult; names: Map<string, string> }) {
  // On affiche TOUS les indicateurs applicables (couverts ET manquants) pour
  // rendre la note lisible. Un gate documenté reste affiché avec sa source
  // (traçabilité) ; un gate manquant n'est pas listé comme « compté 0 » : il
  // applique un plafond par défaut, pas un 0.
  const covered = d.indicators.filter((i) => i.covered);
  const missing = d.indicators.filter((i) => !i.covered && !i.is_gate);
  const missingMandatory = missing.filter((i) => i.mandatory).length;
  return (
    <details className="pillar-card">
      <summary>
        {d.rated ? (
          <div className={`grade sm grade-${d.grade}`}>{d.grade}</div>
        ) : (
          <div className="grade sm grade-none" title="Pilier non noté : aucune preuve ni publication obligatoire.">—</div>
        )}
        <div className="pillar-name">
          {d.name}
          <small>
            fiabilité {pct(d.confidence)} · {d.covered_indicators}/{d.applicable_indicators} indicateurs
            <Tip label="Fiabilité de ce pilier">
              {d.covered_indicators} indicateur(s) documenté(s) sur {d.applicable_indicators} applicables.
              Tout manquant fait baisser la <strong>fiabilité</strong>. Dans la <strong>note</strong>, seuls
              les manquants dont la publication est obligatoire comptent 0
              {missingMandatory > 0 ? ` (ici : ${missingMandatory})` : " (ici : aucun)"} ; les autres en sont
              exclus. Note et fiabilité restent deux mesures distinctes.
            </Tip>
          </small>
        </div>
        <span className="chev" aria-hidden="true">›</span>
      </summary>

      <div className="pillar-body">
      {d.rated ? (
        <div className="row" style={{ margin: "2px 0 2px" }}>
          <div className="bar">
            <span style={{ width: pct(d.score), background: gradeColor[d.grade] }} />
          </div>
          <span className="small" style={{ width: 40, textAlign: "right" }}>{pct(d.score)}</span>
        </div>
      ) : (
        <p className="muted small" style={{ margin: "2px 0 6px" }}>
          Non noté : aucune preuve, et aucune publication obligatoire pour cette entité sur ce pilier.
          Il n'entre pas dans la note globale, mais baisse la fiabilité.
        </p>
      )}

      {d.capped_by_gate && (
        <span className="badge cap">⛔ Plafonné à {pct(d.ceiling ?? 0)} — {capReason[d.dimension_code] ?? "cause structurelle"}</span>
      )}

        <div style={{ marginTop: 8 }}>
          {covered.map((i) => (
            <div className="evidence" key={i.indicator_code}>
              <div className="row between wrap" style={{ gap: 6 }}>
                <span className="small" title={i.indicator_code}>
                  {names.get(i.indicator_code) ?? i.indicator_code}
                </span>
                <span className="row" style={{ gap: 6 }}>
                  {i.is_gate && <span className="badge cap" title="Indicateur-plafond : sa valeur borne la note du pilier, il n'entre pas dans la moyenne.">plafond du pilier</span>}
                  {i.capped_by_greenwashing &&<span className="badge warn">engagement plafonné</span>}
                  {i.floored_by_low_tier && <span className="badge warn">source faible</span>}
                  {i.unscored_controversy && <span className="badge warn" title="Source unique non corroborée : signalée mais exclue du calcul de la note.">controverse · hors note</span>}
                  <span className="badge">{i.nature}</span>
                  {i.display_only ? (
                    <span className="muted small">—</span>
                  ) : (
                    <strong className="small">{pct(i.value ?? 0)}</strong>
                  )}
                </span>
              </div>
              <div className="muted small" style={{ marginTop: 3 }}>
                {i.source_url ? (
                  <a href={i.source_url} target="_blank" rel="noreferrer" style={{ textDecoration: "underline" }}>
                    <span className={`tier-${i.tier}`} title={tierExplain[i.tier ?? ""] ?? ""}>{i.source_code}</span> ↗
                  </a>
                ) : (
                  <span className={`tier-${i.tier}`} title={tierExplain[i.tier ?? ""] ?? ""}>{i.source_code}</span>
                )}
                <Tip label="Fiabilité de cette source">
                  {tierExplain[i.tier ?? ""] ?? "Fiabilité de la source selon son type."}
                </Tip>
                {" · "}{frDate(i.observed_on) ?? i.observed_on}
                {i.observed_on && i.observed_on < STALE_BEFORE && (
                  <span className="badge warn" style={{ marginLeft: 6 }} title="Preuve de plus de 3 ans — à rafraîchir (décote totale à 5 ans).">donnée ancienne</span>
                )}
              </div>
            </div>
          ))}

          {missing.map((i) => (
            <div className="evidence missing" key={i.indicator_code}>
              <div className="row between wrap" style={{ gap: 6 }}>
                <span className="small muted" title={i.indicator_code}>
                  {names.get(i.indicator_code) ?? i.indicator_code}
                </span>
                {i.mandatory ? (
                  <span className="badge warn">obligatoire · manquant</span>
                ) : (
                  <span className="badge">donnée manquante</span>
                )}
              </div>
              <div className="muted small" style={{ marginTop: 3 }}>
                {i.mandatory ? (
                  <>
                    Publication obligatoire ({(i.mandatory_regimes ?? []).join(", ")}). Aucune preuve versée
                    dans DIAMS à ce jour : comptée 0 dans la note tant qu'elle manque — que l'entreprise n'ait
                    pas publié, ou que la collecte reste à faire. Ne pas publier ce que la loi impose n'est pas récompensé.
                  </>
                ) : (
                  <>
                    Aucune preuve publiée, et pas d'obligation légale de publier pour cette entité :
                    n'entre pas dans la note, mais baisse la fiabilité.
                  </>
                )}
              </div>
            </div>
          ))}

          {covered.length === 0 && missing.length === 0 && (
            <p className="muted small">Aucun indicateur applicable à ce pilier.</p>
          )}
        </div>
      </div>
    </details>
  );
}
