import "./globals.css";
import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: { default: "Index général des marques — l'éthique des entreprises, preuves à l'appui", template: "%s · Index général des marques" },
  description:
    "La carte d'identité des marques : des faits publiés, datés et vérifiés mot pour mot dans les sources officielles — climat, travail, gouvernance, fiscalité, droits humains, animaux. Aucune note.",
  openGraph: {
    title: "Index général des marques — l'éthique des entreprises, preuves à l'appui",
    description: "Chaque fait renvoie à sa source officielle. Quand les données manquent, on le dit.",
    locale: "fr_FR",
    type: "website",
  },
};

// Zoom laissé libre (pas de maximum-scale) pour l'accessibilité. Thème clair uniquement : le
// navigateur ne doit pas assombrir la page de lui-même (mode sombre forcé de Chrome, Samsung…).
export const viewport: Viewport = { width: "device-width", initialScale: 1, colorScheme: "only light", themeColor: "#f3f2fb" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <a className="aller-contenu" href="#contenu">Aller au contenu</a>
        <div className="container">
          <header className="row between wrap" style={{ marginBottom: 24, rowGap: 8 }}>
            <a href="/">
              <strong>Index général des marques</strong>
            </a>
            <nav className="row" style={{ gap: 14 }} aria-label="Navigation principale">
              <a className="muted small" href="/marques">Marques</a>
              <a className="muted small" href="/pipeline">Sources</a>
              <a className="muted small" href="/methodologie">Méthodologie</a>
            </nav>
          </header>
          <div id="contenu" tabIndex={-1}>{children}</div>
        </div>
      </body>
    </html>
  );
}
