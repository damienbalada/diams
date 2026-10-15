import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { basicAuthMatches, isAdmin, isAdminPath } from "./lib/basic-auth";

// Protection au niveau de l'app (indépendante du plan Vercel) : HTTP Basic.
//
// Aucun identifiant en dur : les mots de passe DOIVENT être définis dans
// l'environnement (Vercel → Settings → Environment Variables). S'ils manquent,
// on refuse (fail-closed) plutôt que de retomber sur une valeur publique.
//
//  - Site : SITE_USER / SITE_PASSWORD tant qu'il est privé. SITE_PUBLIC=1 l'ouvre
//    au public (lancement presse) : seul le back-office reste protégé.
//  - Back-office (/admin) : ADMIN_USER / ADMIN_PASSWORD, toujours exigés et
//    distincts de ceux du site. Les actions serveur du back-office revérifient
//    ces identifiants (une action Next.js peut être appelée depuis n'importe
//    quelle adresse : le chemin seul ne suffit pas).
const SITE_USER = process.env.SITE_USER || "diams";
const SITE_PASS = process.env.SITE_PASSWORD;
const SITE_PUBLIC = process.env.SITE_PUBLIC === "1";

const challenge = (realm: string) =>
  new NextResponse("Authentification requise.", {
    status: 401,
    headers: { "WWW-Authenticate": `Basic realm="${realm}", charset="UTF-8"` },
  });

export function middleware(req: NextRequest) {
  const auth = req.headers.get("authorization");

  if (isAdminPath(req.nextUrl.pathname)) {
    if (!process.env.ADMIN_PASSWORD) {
      return new NextResponse(
        "Back-office fermé : la variable d'environnement ADMIN_PASSWORD n'est pas définie.",
        { status: 503 },
      );
    }
    return isAdmin(auth) ? NextResponse.next() : challenge("Index des marques - administration");
  }

  if (SITE_PUBLIC) return NextResponse.next();
  if (!SITE_PASS) {
    return new NextResponse(
      "Configuration incomplète : la variable d'environnement SITE_PASSWORD n'est pas définie.",
      { status: 503 },
    );
  }
  return basicAuthMatches(auth, SITE_USER, SITE_PASS) ? NextResponse.next() : challenge("Index des marques");
}

// S'applique à tout sauf les assets statiques.
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
