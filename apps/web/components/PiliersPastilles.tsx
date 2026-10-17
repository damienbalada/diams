"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";

export interface PastillePilier {
  code: string;
  nom: string;
  icone: string;
  teinte: string;
  compte: string;
  vide: boolean;
  signal: "alerte" | "vigilance" | null;
}

const EMOJI = { alerte: "🔴", vigilance: "⚠️" } as const;

/**
 * Piliers en pastilles : les renseignées d'abord, puis les vides (estompées). Un clic déplie le pilier
 * juste sous la ligne de sa pastille ; un second clic le replie. Un lien « #pilier-GEO » (ou
 * « #pilier-GEO:GEO_RUSSIA_EXIT », depuis l'avertissement) ouvre le pilier et déplie la preuve visée.
 * Les panneaux sont rendus par le serveur et passés tels quels.
 */
export function PiliersPastilles({ pastilles, panneaux }: { pastilles: PastillePilier[]; panneaux: Record<string, React.ReactNode> }) {
  const [choix, setChoix] = useState<string | null>(null);
  // Chaque lien suivi relance le défilement, même vers le pilier déjà ouvert.
  const [demande, setDemande] = useState(0);
  // Lignes mesurées tout replié : une fois le panneau inséré, les pastilles suivantes descendent.
  const [lignes, setLignes] = useState<Record<string, number>>({});
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const panneau = useRef<HTMLDivElement | null>(null);
  const viser = useRef<string | null>(null);
  const ordre = [...pastilles].sort((a, b) => Number(a.vide) - Number(b.vide));

  useLayoutEffect(() => {
    const mesurer = () => {
      if (choix) return;
      const m: Record<string, number> = {};
      for (const p of ordre) m[p.code] = refs.current[p.code]?.offsetTop ?? 0;
      setLignes((v) => (JSON.stringify(v) === JSON.stringify(m) ? v : m));
    };
    mesurer();
    window.addEventListener("resize", mesurer);
    return () => window.removeEventListener("resize", mesurer);
  });

  // Ouverture depuis l'adresse (#pilier-CODE[:INDICATEUR]) : au chargement et à chaque lien suivi.
  useEffect(() => {
    const lire = () => {
      const m = /^#pilier-([A-Z]+)(?::([A-Z0-9_]+))?$/.exec(window.location.hash);
      if (!m || !pastilles.some((p) => p.code === m[1])) return;
      viser.current = m[2] ?? "";
      setChoix(m[1]);
      setDemande((n) => n + 1);
    };
    // Un lien déjà suivi ne change plus l'adresse : on intercepte aussi le clic lui-même.
    const clic = (e: MouseEvent) => {
      const a = (e.target as HTMLElement | null)?.closest?.('a[href^="#pilier-"]');
      if (!a) return;
      e.preventDefault();
      history.replaceState(null, "", a.getAttribute("href"));
      lire();
    };
    lire();
    window.addEventListener("hashchange", lire);
    document.addEventListener("click", clic);
    return () => {
      window.removeEventListener("hashchange", lire);
      document.removeEventListener("click", clic);
    };
  }, [pastilles]);

  // Le pilier ouvert depuis un lien : l'indicateur visé est déplié et amené à l'écran.
  useEffect(() => {
    if (!choix || viser.current === null || !panneau.current) return;
    const code = viser.current;
    viser.current = null;
    const cible = code ? panneau.current.querySelector<HTMLElement>(`[data-indicateur="${code}"]`) : null;
    if (cible) cible.querySelector("details")?.setAttribute("open", "");
    (cible ?? panneau.current).scrollIntoView({ behavior: "smooth", block: "start" });
  }, [choix, demande]);

  const rangChoisi = choix ? lignes[choix] : undefined;
  // Dernière pastille de la ligne de la pastille choisie.
  const apres = !choix ? null : [...ordre].reverse().find((p) => rangChoisi !== undefined && lignes[p.code] === rangChoisi)?.code ?? choix;
  const teinte = pastilles.find((p) => p.code === choix)?.teinte ?? "var(--accent)";

  return (
    <div className="ci-pasts" role="tablist" aria-label="Piliers">
      {ordre.map((p) => {
        const actif = choix === p.code;
        return [
          <button
            key={p.code}
            ref={(el) => { refs.current[p.code] = el; }}
            type="button"
            role="tab"
            aria-selected={actif}
            aria-controls={actif ? `panneau-${p.code}` : undefined}
            className={`ci-past${p.vide ? " ci-past-vide" : ""}${actif ? " ci-past-actif" : ""}`}
            style={{ "--pil": p.teinte } as React.CSSProperties}
            onClick={() => {
              setChoix(actif ? null : p.code);
              if (window.location.hash.startsWith("#pilier-")) history.replaceState(null, "", window.location.pathname + window.location.search);
            }}
            aria-label={`${p.nom} : ${p.compte} renseignés${p.signal === "alerte" ? ", alerte" : p.signal === "vigilance" ? ", point de vigilance" : ""}`}
          >
            <span aria-hidden="true">{p.icone}</span>
            <span className="ci-past-nom">{p.nom}</span>
            {p.signal && <span aria-hidden="true" className="ci-past-sig">{EMOJI[p.signal]}</span>}
            <span className="ci-past-cpt">{p.compte}</span>
          </button>,
          apres === p.code && choix && (
            <div key="panneau" id={`panneau-${choix}`} ref={panneau} role="tabpanel" className="ci-pan" style={{ "--pil": teinte } as React.CSSProperties}>
              {panneaux[choix]}
            </div>
          ),
        ];
      })}
      {!choix && <p className="ci-small ci-faint ci-pasts-aide">Cliquez sur un pilier pour lire le détail.</p>}
    </div>
  );
}
