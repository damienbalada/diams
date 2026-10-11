// Tests de l'authentification HTTP Basic (logique pure).
// Lancer : node --test --experimental-strip-types apps/web/lib/basic-auth.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { basicAuthMatches, isAdmin, isAdminPath } from "./basic-auth.ts";

const header = (u: string, p: string) => `Basic ${btoa(`${u}:${p}`)}`;

test("basic auth — identifiants exacts seulement", () => {
  assert.equal(basicAuthMatches(header("diams", "s3cret"), "diams", "s3cret"), true);
  assert.equal(basicAuthMatches(header("diams", "s3cre"), "diams", "s3cret"), false);
  assert.equal(basicAuthMatches(header("diams", "a:b"), "diams", "a:b"), true); // « : » dans le mot de passe
  assert.equal(basicAuthMatches("Basic %%%", "diams", "s3cret"), false);         // en-tête malformé
  assert.equal(basicAuthMatches(header("diams", ""), "diams", undefined), false); // pas de mot de passe défini
});

test("back-office — identifiants distincts de ceux du site, fermé sans mot de passe", () => {
  const env = { ADMIN_PASSWORD: "adm1n", SITE_PASSWORD: "site" };
  assert.equal(isAdmin(header("admin", "adm1n"), env), true);
  assert.equal(isAdmin(header("diams", "site"), env), false);
  assert.equal(isAdmin(header("admin", "adm1n"), {}), false);
  assert.equal(isAdminPath("/admin/revue"), true);
  assert.equal(isAdminPath("/administratif"), false);
});
