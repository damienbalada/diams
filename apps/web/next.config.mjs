/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // API de l'appli mobile : lisible depuis l'aperçu web de l'appli (autre adresse). Lecture seule ;
  // le mot de passe du site reste exigé tant qu'il est privé (en-tête Authorization autorisé).
  async headers() {
    return [
      {
        // Logos : affichables par l'aperçu web de l'appli (images publiques des marques).
        source: "/logos/:chemin*",
        headers: [{ key: "Access-Control-Allow-Origin", value: "*" }],
      },
      {
        source: "/api/:chemin*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          { key: "Access-Control-Allow-Methods", value: "GET, OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Authorization, Accept" },
        ],
      },
    ];
  },
};
export default nextConfig;
