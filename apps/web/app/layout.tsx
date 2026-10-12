import "./globals.css";
import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: { default: "DIAMS — l'éthique des entreprises, preuves à l'appui", template: "%s · DIAMS" },
  description:
    "Une note éthique par entreprise, fondée sur des preuves officielles datées et vérifiées mot pour mot : climat, travail, gouvernance, fiscalité, droits humains.",
  openGraph: {
    title: "DIAMS — l'éthique des entreprises, preuves à l'appui",
    description: "Chaque note renvoie à sa source officielle. Quand les données manquent, on le dit.",
    locale: "fr_FR",
    type: "website",
  },
};

// Zoom laissé libre (pas de maximum-scale) pour l'accessibilité.
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <div className="container">
          <header className="row between" style={{ marginBottom: 24 }}>
            <a href="/" title="Documenté, Indépendant, Auditable, Multicritère, Sourcé">
              <strong>DIAMS</strong>
            </a>
            <span className="row" style={{ gap: 14 }}>
              <a className="muted small" href="/classement">Classement</a>
              <a className="muted small" href="/pipeline">Sources</a>
              <a className="muted small" href="/methodologie">Méthodologie</a>
            </span>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
