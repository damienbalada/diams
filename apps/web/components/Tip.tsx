"use client";

import { useState, type ReactNode } from "react";

/**
 * Infobulle accessible et mobile-friendly. Le bouton « i » révèle une
 * explication rendue **en flux normal** (pas de positionnement absolu) : elle
 * n'est donc jamais rognée par un conteneur `overflow: hidden` (les cartes de
 * pilier), et s'ouvre au clic comme au tap. `stopPropagation` évite d'ouvrir
 * le `<details>` parent quand l'infobulle est dans un résumé de pilier.
 */
export function Tip({ children, label = "Explication" }: { children: ReactNode; label?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="tip">
      <button
        type="button"
        className="tip-btn"
        aria-label={label}
        aria-expanded={open}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen((o) => !o);
        }}
      >
        i
      </button>
      {open && (
        <span className="tip-pop" role="note">
          {children}
        </span>
      )}
    </span>
  );
}
