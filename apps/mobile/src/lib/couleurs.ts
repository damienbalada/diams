/** Palette de l'Index (mêmes valeurs que le site, contrastes conformes WCAG AA). */
export const C = {
  fond: '#f3f2fb',
  carte: '#ffffff',
  carte2: '#f0eefb',
  bord: '#e7e3f6',
  bordFort: '#d6d0ee',
  texte: '#160f2e',
  gris: '#5c5676',
  grisClair: '#6c6689',
  accent: '#5a2de0',
  surAccent: '#ffffff',
  alerte: '#b3261e',
  alerteTexte: '#a8221b',
  alerteFond: '#fff7f6',
  vigilance: '#a85400',
  vigilanceFond: '#fff3e0',
  vigilanceTexte: '#6b3a00',
} as const;

/** Teinte de chaque pilier (repère visuel, comme sur le site). */
export const TEINTE: Record<string, string> = {
  ANI: '#b4532a', ENV: '#1f8a4c', PLA: '#0e7a8a', WAT: '#2563c9', LAB: '#7a3fd0',
  SUP: '#a86a12', GOV: '#4b5a70', TAX: '#11796d', GEO: '#b8325a', INV: '#4a43c4',
};

export const SOLIDITE: Record<string, { texte: string; couleur: string }> = {
  officielle: { texte: 'Source officielle (loi, régulateur)', couleur: '#0b6b44' },
  reconnue: { texte: 'Organisme reconnu', couleur: '#2f55b0' },
  declarative: { texte: "Déclaration publique (site de l'entreprise, presse)", couleur: '#7a5a0c' },
};
