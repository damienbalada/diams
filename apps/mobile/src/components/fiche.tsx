import { Image } from 'expo-image';
import * as WebBrowser from 'expo-web-browser';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Logo } from '@/components/logo';
import type { Fait, Fiche as TFiche, Pilier } from '@/lib/api';
import { C, SOLIDITE, TEINTE } from '@/lib/couleurs';

const NIVEAU: Record<string, string> = { groupe: 'Groupe', marque: 'Marque', produit: 'Produits' };
const dfr = (d: string) => d.split('-').reverse().join('/');
const ouvrir = (url: string) => WebBrowser.openBrowserAsync(url);
/** Quantité affichée seulement si elle porte une unité (« 250 g », « 1,5 L ») : « 8 » seul ne dit rien. */
const quantite = (q: string | null) => (q && /\d\s*[a-zA-Zµ]/.test(q) ? ` · ${q}` : '');

/** La fiche d'une marque ou d'un groupe : produit scanné, alertes, piliers dépliables. */
export function Fiche({ fiche, onMarque }: { fiche: TFiche; onMarque: (slug: string) => void }) {
  const alertes = fiche.alertes.filter((a) => a.niveau === 'alerte');
  const vigilance = fiche.alertes.filter((a) => a.niveau === 'vigilance');
  return (
    <View style={s.pile}>
      {fiche.produit && (
        <View style={s.produit} accessibilityLabel={`Produit scanné : ${fiche.produit.nom}`}>
          {fiche.produit.image ? (
            <Image source={{ uri: fiche.produit.image }} style={s.photo} contentFit="contain" accessible={false} />
          ) : (
            <View style={[s.photo, s.centre]}><Text style={{ fontSize: 28 }}>🛒</Text></View>
          )}
          <View style={s.flex}>
            <Text style={s.surtitre}>PRODUIT SCANNÉ</Text>
            <Text style={s.produitNom}>{fiche.produit.nom}{quantite(fiche.produit.quantite)}</Text>
            <Text style={s.petit}>{fiche.produit.phrase}</Text>
            <Text style={s.lien} onPress={() => ouvrir(fiche.produit!.lien)} accessibilityRole="link">
              D'après {fiche.produit.base}
            </Text>
          </View>
        </View>
      )}

      <View style={s.entete}>
        <Logo src={fiche.logo} taille={64} groupe={!fiche.proprietaire} />
        <View style={s.flex}>
          <Text style={s.surtitre}>{fiche.proprietaire ? "CARTE D'IDENTITÉ" : 'GROUPE'}</Text>
          <Text style={s.titre} accessibilityRole="header">{fiche.nom}</Text>
          {fiche.proprietaire && (
            <Text style={s.proprio}>
              Appartient à{' '}
              <Text style={s.proprioNom} onPress={() => onMarque(fiche.proprietaire!.slug)} accessibilityRole="link">
                {fiche.proprietaire.nom}
              </Text>
              , qui reçoit l'argent de vos achats
            </Text>
          )}
        </View>
      </View>

      {alertes.length > 0 && (
        <View style={s.bandeauAlerte} accessibilityRole="summary">
          <Text style={s.bandeauTitreAlerte}>⚠️ {alertes.length} alerte{alertes.length > 1 ? 's' : ''}</Text>
          {alertes.map((a, i) => (
            <Text key={i} style={s.bandeauLigneAlerte}>{a.icone} {a.motif}</Text>
          ))}
        </View>
      )}
      {vigilance.length > 0 && (
        <View style={s.bandeauVigilance}>
          <Text style={s.bandeauTitreVigilance}>🟠 {vigilance.length} point{vigilance.length > 1 ? 's' : ''} de vigilance</Text>
          {vigilance.map((a, i) => (
            <Text key={i} style={s.bandeauLigneVigilance}>{a.icone} {a.motif}</Text>
          ))}
        </View>
      )}

      <Text style={s.section} accessibilityRole="header">Pilier par pilier</Text>
      <View style={s.carteListe}>
        {fiche.piliers.map((p, i) => (
          <LignePilier key={p.code} p={p} dernier={i === fiche.piliers.length - 1} />
        ))}
      </View>
      <Text style={s.pied}>
        {fiche.renseignes} informations documentées sur {fiche.total} recherchées · aucune note, que des faits sourcés.
      </Text>
    </View>
  );
}

function LignePilier({ p, dernier }: { p: Pilier; dernier: boolean }) {
  const [ouvert, setOuvert] = useState(false);
  const teinte = TEINTE[p.code] ?? C.accent;
  const signal = p.cle?.signal;
  const couleurValeur = signal === 'alerte' ? C.alerteTexte : signal === 'vigilance' ? C.vigilance : p.cle && p.cle.etat !== 'aucune_info' ? C.texte : C.gris;
  const groupes = (['groupe', 'marque', 'produit'] as const)
    .map((n) => ({ n, faits: p.faits.filter((f) => f.niveau === n) }))
    .filter((g) => g.faits.length);
  return (
    <View style={[s.pilier, !dernier && s.separateur, ouvert && { borderLeftColor: teinte, borderLeftWidth: 4 }]}>
      <Pressable
        onPress={() => setOuvert(!ouvert)}
        accessibilityRole="button"
        accessibilityState={{ expanded: ouvert }}
        accessibilityLabel={`${p.nom}, ${p.renseignes} sur ${p.total} renseignés. ${p.cle?.valeur ?? 'Aucune information'}`}
        style={({ pressed }) => [s.pilierTete, pressed && { opacity: 0.6 }]}>
        <View style={[s.pastille, { backgroundColor: teinte + '22' }, signal === 'alerte' && { borderColor: C.alerte, borderWidth: 2 }, signal === 'vigilance' && { borderColor: '#d97a00', borderWidth: 2 }]}>
          <Text style={{ fontSize: 19 }}>{p.icone}</Text>
        </View>
        <View style={s.flex}>
          <View style={s.ligne}>
            <Text style={[s.pilierNom, { color: teinte }]}>{p.nom.toUpperCase()}</Text>
            <Text style={s.compteur}>{p.renseignes} sur {p.total} {ouvert ? '▲' : '▼'}</Text>
          </View>
          {p.cle && p.cle.etat !== 'aucune_info' && <Text style={s.cleNom}>{p.cle.nom}</Text>}
          <Text style={[s.cleValeur, { color: couleurValeur }]}>
            {signal === 'alerte' ? '⚠️ ' : signal === 'vigilance' ? '🟠 ' : ''}
            {p.cle?.valeur ?? 'Aucune information'}
          </Text>
        </View>
      </Pressable>
      {ouvert && (
        <View style={s.corps}>
          {groupes.map((g) => (
            <View key={g.n} style={s.pile8}>
              <Text style={s.niveau}>{NIVEAU[g.n]}</Text>
              {g.faits.map((f) => <CarteFait key={f.code} f={f} teinte={teinte} />)}
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

function CarteFait({ f, teinte }: { f: Fait; teinte: string }) {
  const [citation, setCitation] = useState(false);
  const vide = f.etat === 'aucune_info';
  const fond = f.signal?.niveau === 'alerte' ? C.alerteFond : f.signal?.niveau === 'vigilance' ? '#fffaf2' : vide ? C.carte2 : C.carte;
  const bordGauche = f.signal?.niveau === 'alerte' ? C.alerte : f.signal?.niveau === 'vigilance' ? '#d97a00' : vide ? C.bordFort : teinte;
  return (
    <View style={[s.fait, { backgroundColor: fond, borderLeftColor: bordGauche }]}>
      <View style={s.ligne}>
        <Text style={[s.faitNom, s.flex]}>{f.nom.toUpperCase()}</Text>
        {f.signal && (
          <Text style={[s.etiquette, f.signal.niveau === 'alerte' ? s.etiquetteAlerte : s.etiquetteVigilance]}>
            {f.signal.niveau === 'alerte' ? '⚠️ Alerte' : '🟠 Vigilance'}
          </Text>
        )}
      </View>
      <Text style={[s.faitValeur, vide && { color: C.gris, fontSize: 16 }, f.signal?.niveau === 'alerte' && { color: C.alerteTexte }, f.signal?.niveau === 'vigilance' && { color: C.vigilance }]}>
        {f.valeur}
      </Text>
      {f.raison && <Text style={s.petit}>{f.raison[0].toUpperCase() + f.raison.slice(1)}.</Text>}
      {f.repere && <Text style={s.petit}>{f.repere}</Text>}
      {f.note && <Text style={s.note}>{f.note}</Text>}
      {f.preuve && (
        <View style={s.source}>
          <Text style={s.petit}>{dfr(f.preuve.date)}</Text>
          <Text style={[s.solidite, { color: SOLIDITE[f.preuve.solidite]?.couleur, borderColor: SOLIDITE[f.preuve.solidite]?.couleur }]}>
            {SOLIDITE[f.preuve.solidite]?.texte}
          </Text>
          <Text style={s.petit}>{f.preuve.source}{f.preuve.reprisDe ? ` · donnée du groupe ${f.preuve.reprisDe}` : ''}</Text>
        </View>
      )}
      {f.signal && <Text style={[s.petit, { fontWeight: '600' }]}>Seuil : {f.signal.regle}</Text>}
      {f.preuve && (f.preuve.citation || f.preuve.url) && (
        <View>
          <Pressable onPress={() => setCitation(!citation)} accessibilityRole="button" accessibilityState={{ expanded: citation }} hitSlop={8} style={s.bouton44}>
            <Text style={s.lien}>{citation ? 'Masquer la source' : 'Ce que dit la source'}</Text>
          </Pressable>
          {citation && (
            <View style={s.citation}>
              {f.preuve.citation && <Text style={s.citationTexte}>{f.preuve.citation}</Text>}
              {f.preuve.url && (
                <Text style={s.lien} onPress={() => ouvrir(f.preuve!.url!)} accessibilityRole="link">Ouvrir la source ↗</Text>
              )}
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  pile: { gap: 14 },
  pile8: { gap: 8 },
  flex: { flex: 1, minWidth: 0 },
  centre: { alignItems: 'center', justifyContent: 'center' },
  ligne: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  produit: { flexDirection: 'row', gap: 14, alignItems: 'center', backgroundColor: C.carte, borderRadius: 18, padding: 14, borderWidth: 1, borderColor: C.bord },
  photo: { width: 72, height: 72, borderRadius: 12, backgroundColor: '#fff', borderWidth: 1, borderColor: C.bord },
  surtitre: { fontSize: 12, fontWeight: '800', letterSpacing: 0.6, color: C.gris },
  produitNom: { fontSize: 17, fontWeight: '700', color: C.texte, marginTop: 2 },
  entete: { flexDirection: 'row', gap: 14, alignItems: 'center' },
  titre: { fontSize: 30, fontWeight: '800', color: C.texte },
  proprio: { fontSize: 15, lineHeight: 21, color: C.texte },
  proprioNom: { fontWeight: '800', textDecorationLine: 'underline' },
  bandeauAlerte: { backgroundColor: C.alerte, borderRadius: 16, padding: 16, gap: 6 },
  bandeauTitreAlerte: { color: '#fff', fontSize: 18, fontWeight: '800' },
  bandeauLigneAlerte: { color: '#fff', fontSize: 15, lineHeight: 21, fontWeight: '600' },
  bandeauVigilance: { backgroundColor: C.vigilanceFond, borderRadius: 16, padding: 16, gap: 6, borderWidth: 1, borderColor: '#f2c48a' },
  bandeauTitreVigilance: { color: C.vigilanceTexte, fontSize: 17, fontWeight: '800' },
  bandeauLigneVigilance: { color: C.vigilanceTexte, fontSize: 15, lineHeight: 21, fontWeight: '600' },
  section: { fontSize: 20, fontWeight: '800', color: C.texte, marginTop: 4 },
  carteListe: { backgroundColor: C.carte, borderRadius: 18, overflow: 'hidden', borderWidth: 1, borderColor: C.bord },
  pilier: { borderLeftWidth: 0 },
  separateur: { borderBottomWidth: 1, borderBottomColor: C.bord },
  pilierTete: { flexDirection: 'row', gap: 12, padding: 14, minHeight: 64 },
  pastille: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center' },
  pilierNom: { flex: 1, fontSize: 12.5, fontWeight: '800', letterSpacing: 0.4 },
  compteur: { fontSize: 12.5, color: C.gris },
  cleNom: { fontSize: 13, color: C.gris, marginTop: 2 },
  cleValeur: { fontSize: 16, lineHeight: 22, fontWeight: '700', marginTop: 2 },
  corps: { paddingHorizontal: 14, paddingBottom: 14, gap: 14 },
  niveau: { fontSize: 13, fontWeight: '800', color: C.gris, textTransform: 'uppercase', letterSpacing: 0.5 },
  fait: { borderRadius: 14, padding: 14, gap: 6, borderWidth: 1, borderColor: C.bord, borderLeftWidth: 4 },
  faitNom: { fontSize: 12, fontWeight: '800', color: C.gris, letterSpacing: 0.3 },
  faitValeur: { fontSize: 18, lineHeight: 24, fontWeight: '800', color: C.texte },
  etiquette: { fontSize: 12, fontWeight: '800', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, overflow: 'hidden' },
  etiquetteAlerte: { backgroundColor: C.alerte, color: '#fff' },
  etiquetteVigilance: { backgroundColor: '#ffe2b8', color: C.vigilanceTexte },
  petit: { fontSize: 13, lineHeight: 18, color: C.gris },
  note: { fontSize: 12.5, lineHeight: 17, color: C.grisClair },
  source: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, alignItems: 'center' },
  solidite: { fontSize: 12, fontWeight: '700', borderWidth: 1, borderRadius: 999, paddingHorizontal: 8, paddingVertical: 1 },
  lien: { fontSize: 15, fontWeight: '600', color: C.accent },
  bouton44: { minHeight: 44, justifyContent: 'center' },
  citation: { backgroundColor: C.carte2, borderRadius: 10, padding: 10, gap: 8 },
  citationTexte: { fontSize: 13.5, lineHeight: 19, color: C.texte },
  pied: { fontSize: 13, lineHeight: 18, color: C.gris },
});
