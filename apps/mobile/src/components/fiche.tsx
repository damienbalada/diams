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
  // D'abord ce qui est documenté (alertes en tête), puis, repliés en bas, les indicateurs sans information.
  const rang = (f: Fait) => (f.signal?.niveau === 'alerte' ? 0 : f.signal?.niveau === 'vigilance' ? 1 : 2);
  const pleins = p.faits.filter((f) => f.etat !== 'aucune_info').sort((a, b) => rang(a) - rang(b));
  const vides = p.faits.filter((f) => f.etat === 'aucune_info');
  // Le niveau (groupe, marque, produits) n'est précisé que s'il y en a plusieurs.
  const plusieursNiveaux = new Set(pleins.map((f) => f.niveau)).size > 1;
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
          {/* Ouvert, le résumé disparaît : le premier indicateur, juste dessous, le dit déjà. */}
          {!ouvert && p.cle && p.cle.etat !== 'aucune_info' && <Text style={s.cleNom}>{p.cle.nom}</Text>}
          {!ouvert && (
            <Text style={[s.cleValeur, { color: couleurValeur }]}>
              {signal === 'alerte' ? '⚠️ ' : signal === 'vigilance' ? '🟠 ' : ''}
              {p.cle?.valeur ?? 'Aucune information'}
            </Text>
          )}
        </View>
      </Pressable>
      {ouvert && (
        <View style={s.corps}>
          {pleins.map((f) => <CarteFait key={f.code} f={f} teinte={teinte} niveau={plusieursNiveaux ? NIVEAU[f.niveau] : null} />)}
          {vides.length > 0 && <SansInformation faits={vides} toutVide={!pleins.length} />}
        </View>
      )}
    </View>
  );
}

const majuscule = (t: string) => t[0].toUpperCase() + t.slice(1);

/**
 * Un indicateur documenté, en deux temps : d'abord le fait (nom, valeur, repère), puis, sur demande,
 * le détail (raison, note, seuil, solidité, citation de la source).
 */
function CarteFait({ f, teinte, niveau }: { f: Fait; teinte: string; niveau: string | null }) {
  const [details, setDetails] = useState(false);
  const [toute, setToute] = useState(false);
  const sig = f.signal?.niveau;
  const fond = sig === 'alerte' ? C.alerteFond : sig === 'vigilance' ? '#fffaf2' : C.carte;
  const bordGauche = sig === 'alerte' ? C.alerte : sig === 'vigilance' ? '#d97a00' : teinte;
  // Avec un signal, la valeur dit déjà le repère (« il faudrait 4,2 % ») : il passe dans le détail.
  const repereVisible = f.repere && !f.signal ? f.repere : null;
  const aDetail = !!(f.preuve || f.raison || f.note || f.signal || (f.repere && !repereVisible));
  const sol = f.preuve ? SOLIDITE[f.preuve.solidite] : null;
  return (
    <View style={[s.fait, { backgroundColor: fond, borderLeftColor: bordGauche }]}>
      <View style={s.ligne}>
        <Text style={[s.faitNom, s.flex]}>{f.nom}{niveau ? ` · ${niveau.toLowerCase()}` : ''}</Text>
        {f.signal && (
          <Text style={[s.etiquette, sig === 'alerte' ? s.etiquetteAlerte : s.etiquetteVigilance]}>
            {sig === 'alerte' ? '⚠️ Alerte' : '🟠 Vigilance'}
          </Text>
        )}
      </View>
      <Text style={[s.faitValeur, sig === 'alerte' && { color: C.alerteTexte }, sig === 'vigilance' && { color: C.vigilance }]}>{majuscule(f.valeur)}</Text>
      {repereVisible && <Text style={s.repere}>{repereVisible}</Text>}

      {aDetail && (
        <Pressable
          onPress={() => setDetails(!details)}
          accessibilityRole="button"
          accessibilityState={{ expanded: details }}
          accessibilityLabel={details ? 'Masquer le détail' : `Détail et source : ${f.preuve?.source ?? f.nom}`}
          style={({ pressed }) => [s.basFait, pressed && { opacity: 0.6 }]}>
          <Text style={[s.sourceCourte, s.flex]} numberOfLines={1}>
            {f.preuve ? `${f.preuve.source} · ${dfr(f.preuve.date)}` : 'Détail'}
          </Text>
          <Text style={s.lienPetit}>{details ? 'Moins ▲' : 'Détail ▼'}</Text>
        </Pressable>
      )}

      {details && (
        <View style={s.details}>
          {f.raison && <Text style={s.detailTexte}>{majuscule(f.raison)}.</Text>}
          {/* Avec un signal, le seuil retenu dit déjà le repère. */}
          {f.repere && !repereVisible && !f.signal && <Text style={s.detailTexte}>{f.repere}</Text>}
          {f.signal && <Text style={s.detailTexte}><Text style={s.gras}>Seuil retenu : </Text>{f.signal.regle}</Text>}
          {f.note && <Text style={s.note}>{f.note}</Text>}
          {f.preuve && (
            <View style={s.source}>
              {sol && <Text style={[s.solidite, { color: sol.couleur, borderColor: sol.couleur }]}>{sol.texte}</Text>}
              <Text style={s.petit}>
                {f.preuve.source}, {dfr(f.preuve.date)}{f.preuve.reprisDe ? ` · donnée du groupe ${f.preuve.reprisDe}` : ''}
              </Text>
            </View>
          )}
          {f.preuve?.citation && (
            <View>
              <Text style={s.citationTexte} numberOfLines={toute ? undefined : 4}>« {f.preuve.citation} »</Text>
              {f.preuve.citation.length > 180 && (
                <Pressable onPress={() => setToute(!toute)} accessibilityRole="button" accessibilityState={{ expanded: toute }} hitSlop={8} style={s.bouton44}>
                  <Text style={s.lienPetit}>{toute ? 'Raccourcir la citation' : 'Lire toute la citation'}</Text>
                </Pressable>
              )}
            </View>
          )}
          {f.preuve?.url && (
            <Pressable onPress={() => ouvrir(f.preuve!.url!)} accessibilityRole="link" hitSlop={8} style={s.bouton44}>
              <Text style={s.lien}>Ouvrir la source ↗</Text>
            </Pressable>
          )}
        </View>
      )}
    </View>
  );
}

/** Les indicateurs sans information, repliés en une ligne (dépliés d'office si le pilier n'a rien d'autre). */
function SansInformation({ faits, toutVide }: { faits: Fait[]; toutVide: boolean }) {
  const [ouvert, setOuvert] = useState(toutVide);
  const n = faits.length;
  return (
    <View style={s.vides}>
      <Pressable
        onPress={() => setOuvert(!ouvert)}
        accessibilityRole="button"
        accessibilityState={{ expanded: ouvert }}
        style={({ pressed }) => [s.videsTete, pressed && { opacity: 0.6 }]}>
        <Text style={[s.videsTitre, s.flex]}>
          {toutVide ? 'Rien de documenté pour l’instant' : `${n} indicateur${n > 1 ? 's' : ''} sans information`}
        </Text>
        <Text style={s.lienPetit}>{ouvert ? 'Masquer ▲' : 'Pourquoi ▼'}</Text>
      </Pressable>
      {ouvert &&
        faits.map((f) => (
          <View key={f.code} style={s.videLigne}>
            <Text style={s.videNom}>{f.nom}</Text>
            <Text style={s.petit}>
              {f.valeur !== 'Aucune information' ? `${f.valeur}. ` : ''}
              {f.raison ? `${majuscule(f.raison)}.` : ''}
              {f.note ? ` ${f.note}` : ''}
            </Text>
          </View>
        ))}
    </View>
  );
}

const s = StyleSheet.create({
  pile: { gap: 14 },
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
  corps: { paddingHorizontal: 14, paddingBottom: 16, paddingTop: 2, gap: 12 },
  fait: { borderRadius: 14, paddingHorizontal: 14, paddingTop: 14, paddingBottom: 4, gap: 6, borderWidth: 1, borderColor: C.bord, borderLeftWidth: 4 },
  faitNom: { fontSize: 14, fontWeight: '600', color: C.gris },
  faitValeur: { fontSize: 19, lineHeight: 25, fontWeight: '800', color: C.texte },
  repere: { fontSize: 14, lineHeight: 20, color: C.texte },
  basFait: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 44, borderTopWidth: 1, borderTopColor: C.bord, marginTop: 6 },
  sourceCourte: { fontSize: 13, color: C.gris },
  lienPetit: { fontSize: 14, fontWeight: '700', color: C.accent },
  details: { gap: 10, paddingBottom: 10 },
  detailTexte: { fontSize: 14, lineHeight: 20, color: C.texte },
  gras: { fontWeight: '700' },
  vides: { borderRadius: 14, backgroundColor: C.carte2, paddingHorizontal: 14 },
  videsTete: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 48 },
  videsTitre: { fontSize: 15, fontWeight: '600', color: C.gris },
  videLigne: { paddingVertical: 10, borderTopWidth: 1, borderTopColor: C.bord, gap: 2 },
  videNom: { fontSize: 14, fontWeight: '700', color: C.texte },
  etiquette: { fontSize: 12, fontWeight: '800', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, overflow: 'hidden' },
  etiquetteAlerte: { backgroundColor: C.alerte, color: '#fff' },
  etiquetteVigilance: { backgroundColor: '#ffe2b8', color: C.vigilanceTexte },
  petit: { fontSize: 13, lineHeight: 18, color: C.gris },
  note: { fontSize: 12.5, lineHeight: 17, color: C.grisClair },
  source: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, alignItems: 'center' },
  solidite: { fontSize: 12, fontWeight: '700', borderWidth: 1, borderRadius: 999, paddingHorizontal: 8, paddingVertical: 1 },
  lien: { fontSize: 15, fontWeight: '600', color: C.accent },
  bouton44: { minHeight: 44, justifyContent: 'center' },
  citationTexte: { fontSize: 14, lineHeight: 20, color: C.texte, fontStyle: 'italic', borderLeftWidth: 3, borderLeftColor: C.bordFort, paddingLeft: 10 },
  pied: { fontSize: 13, lineHeight: 18, color: C.gris },
});
