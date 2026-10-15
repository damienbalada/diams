import { redirect } from "next/navigation";

// Refonte (PLAN_REFONTE.md) : plus de note, donc plus de classement. L'index des marques,
// par secteur et par ordre alphabétique, est sur la page d'accueil.
export default function ClassementPage() {
  redirect("/#index");
}
