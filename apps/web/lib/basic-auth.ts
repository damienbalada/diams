/**
 * Authentification HTTP Basic, partagée par le middleware (site, back-office)
 * et les actions serveur du back-office. Logique pure, sans dépendance Next :
 * testable et utilisable en Edge comme en Node.
 *
 *  - site : SITE_USER / SITE_PASSWORD, sauf si SITE_PUBLIC=1 (site ouvert au
 *    public : seul le back-office reste protégé) ;
 *  - back-office (/admin) : ADMIN_USER / ADMIN_PASSWORD, toujours exigés, et
 *    distincts de ceux du site. Sans ADMIN_PASSWORD, le back-office est fermé.
 */

/** Comparaison à temps constant (évite de fuiter le secret par timing). */
export function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

/** Vrai si l'en-tête Authorization porte exactement ces identifiants. */
export function basicAuthMatches(header: string | null | undefined, user: string, pass: string | undefined): boolean {
  if (!pass || !header?.startsWith("Basic ")) return false;
  try {
    const decoded = atob(header.slice(6));
    const idx = decoded.indexOf(":");
    if (idx < 0) return false;
    return safeEqual(decoded.slice(0, idx), user) && safeEqual(decoded.slice(idx + 1), pass);
  } catch {
    return false; // en-tête malformé
  }
}

export const isAdminPath = (path: string) => path === "/admin" || path.startsWith("/admin/");

export function adminCredentials(env: Record<string, string | undefined> = process.env) {
  return { user: env.ADMIN_USER || "admin", pass: env.ADMIN_PASSWORD };
}

/** Le visiteur est-il administrateur ? (identifiants du back-office) */
export function isAdmin(header: string | null | undefined, env: Record<string, string | undefined> = process.env): boolean {
  const { user, pass } = adminCredentials(env);
  return basicAuthMatches(header, user, pass);
}
