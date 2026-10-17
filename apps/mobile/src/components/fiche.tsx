import { Image } from 'expo-image';
import { router } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { useEffect, useRef, useState } from 'react';
import { Animated, Modal, PanResponder, Pressable, StyleSheet, Text, View } from 'react-native';

import { MARGE_BOUTON } from '@/components/bouton-scanner';
import { Logo } from '@/components/logo';
import type { Fait, Fiche as TFiche, NiveauSignal, Pilier, ProduitLu } from '@/lib/api';
import { C, SOLIDITE, TEINTE } from '@/lib/couleurs';
import { lire } from '@/lib/stockage';

/** Réglage d'affichage de la fiche : pastilles par pilier (essai, par défaut) ou liste dépliable. */
export const CLE_AFFICHAGE = 'index.affichage';
/** Réglage de l'en-tête de fiche (essai) : A bandeaux, B photo en bandeau, C étiquettes, E onglets. */
export const CLE_ENTETE = 'index.entete';
export type VarianteEnTete = 'A' | 'B' | 'C' | 'E';

const NIVEAU: Record<string, string> = { groupe: 'Groupe', marque: 'Marque', produit: 'Produits' };
const dfr = (d: string) => d.split('-').reverse().join('/');
const ouvrir = (url: string) => WebBrowser.openBrowserAsync(url);
/** Signal d'un pilier ou d'un motif, en emoji : point rouge pour une alerte, attention orange pour une vigilance. */
const EMOJI: Record<NiveauSignal, string> = { alerte: '🔴', vigilance: '⚠️' };
const pluriel = (n: number, un: string, plusieurs: string) => `${n} ${n > 1 ? plusieurs : un}`;
/** Quantité affichée seulement si elle porte une unité (« 250 g », « 1,5 L ») : « 8 » seul ne dit rien. */
const quantite = (q: string | null) => {
  const v = (q ?? '').replace(/\s+[e℮]$/i, '').trim();
  return /\d\s*[a-zA-Zµ]/.test(v) ? ` · ${v}` : '';
};

/** Titre de l'écran d'une fiche : « Nutella · 400 g » pour un produit scanné, sinon le nom de la marque. */
export const titreFiche = (fiche: TFiche) =>
  fiche.produit ? `${fiche.produit.nom}${quantite(fiche.produit.quantite)}` : fiche.nom;

/**
 * Photo du produit en grand. Elle se ferme d'un balayage dans n'importe quelle direction (la photo suit
 * le doigt et le fond s'éclaircit avec la distance), par le bouton retour d'Android ou, au lecteur
 * d'écran, par le geste d'échappement.
 */
function PhotoGrande({ uri, visible, fermer }: { uri: string; visible: boolean; fermer: () => void }) {
  const [pos] = useState(() => new Animated.ValueXY({ x: 0, y: 0 }));
  // Distance au point de départ, quelle que soit la direction : elle règle l'opacité du fond.
  const [ecart] = useState(() => new Animated.Value(0));
  // Balayage assez long ou assez vif : la photo part dans la direction du geste et se ferme ; sinon elle revient.
  const conclure = (dx: number, dy: number, vx: number, vy: number) => {
    const d = Math.hypot(dx, dy);
    if (d > 90 || Math.hypot(vx, vy) > 0.8) {
      const k = 900 / Math.max(d, 1);
      Animated.parallel([
        Animated.timing(pos, { toValue: { x: dx * k, y: dy * k }, duration: 160, useNativeDriver: false }),
        Animated.timing(ecart, { toValue: 400, duration: 160, useNativeDriver: false }),
      ]).start(() => {
        fermer();
        pos.setValue({ x: 0, y: 0 });
        ecart.setValue(0);
      });
    } else {
      Animated.parallel([
        Animated.spring(pos, { toValue: { x: 0, y: 0 }, useNativeDriver: false }),
        Animated.spring(ecart, { toValue: 0, useNativeDriver: false }),
      ]).start();
    }
  };
  const [geste] = useState(() =>
    PanResponder.create({
      onMoveShouldSetPanResponder: (_e, g) => Math.hypot(g.dx, g.dy) > 6,
      onStartShouldSetPanResponder: () => true,
      onPanResponderMove: (_e, g) => {
        pos.setValue({ x: g.dx, y: g.dy });
        ecart.setValue(Math.hypot(g.dx, g.dy));
      },
      // Le geste garde la main jusqu'au bout ; s'il est malgré tout interrompu, on conclut de la même façon.
      onPanResponderTerminationRequest: () => false,
      onPanResponderRelease: (_e, g) => conclure(g.dx, g.dy, g.vx, g.vy),
      onPanResponderTerminate: (_e, g) => conclure(g.dx, g.dy, g.vx, g.vy),
    }),
  );
  const fond = ecart.interpolate({ inputRange: [0, 400], outputRange: ['rgba(10,6,24,0.92)', 'rgba(10,6,24,0.25)'], extrapolate: 'clamp' });
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={fermer}>
      <Animated.View
        style={[s.voile, { backgroundColor: fond }]}
        accessibilityViewIsModal
        accessibilityLabel="Photo du produit en grand ; balayez dans n'importe quelle direction pour la fermer"
        onAccessibilityEscape={fermer}
        {...geste.panHandlers}>
        <Animated.View style={[s.photoGrande, { transform: pos.getTranslateTransform() }]}>
          <Image source={{ uri }} style={{ flex: 1 }} contentFit="contain" />
        </Animated.View>
      </Animated.View>
    </Modal>
  );
}

/**
 * En-tête de fiche : photo du produit scanné (agrandie au toucher), logo et nom de la marque, logo et
 * nom du groupe propriétaire. Compact : la base produit est citée en bas de la fiche.
 */
function EnTete({ fiche, onMarque, medaillon = false, bandeau = false }: { fiche: TFiche; onMarque: (slug: string) => void; medaillon?: boolean; bandeau?: boolean }) {
  const [grand, setGrand] = useState(false);
  const pr = fiche.produit;
  // Fiche d'une marque ou d'un groupe (sans produit scanné) : son logo en bandeau, à la place de la photo.
  if (bandeau && !pr && fiche.logo) {
    return (
      <View style={{ gap: 8 }}>
        <View style={[s.bandeauPhoto, s.centre]} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
          <Logo src={fiche.logo} taille={140} marge={10} groupe={!fiche.proprietaire} />
        </View>
        <MarqueEtGroupe fiche={fiche} onMarque={onMarque} />
      </View>
    );
  }
  if (bandeau && pr?.image) {
    return (
      <View style={{ gap: 8 }}>
        <Pressable onPress={() => setGrand(true)} accessibilityRole="imagebutton" accessibilityLabel={`Photo du produit ${pr.nom}, l'agrandir`} style={s.bandeauPhoto}>
          <Image source={{ uri: pr.image }} style={s.bandeauImage} contentFit="contain" />
          <Text style={s.loupe}>🔍 agrandir</Text>
        </Pressable>
        <MarqueEtGroupe fiche={fiche} onMarque={onMarque} />
        <PhotoGrande uri={pr.image} visible={grand} fermer={() => setGrand(false)} />
      </View>
    );
  }
  return (
    <View style={s.enTete}>
      {pr ? (
        <Pressable onPress={() => pr.image && setGrand(true)} accessibilityRole="imagebutton" accessibilityLabel={`Photo du produit ${pr.nom}, l'agrandir`} disabled={!pr.image}>
          {pr.image ? (
            <Image source={{ uri: pr.image }} style={s.photo} contentFit="contain" />
          ) : (
            <View style={[s.photo, s.centre]}><Text style={{ fontSize: 28 }}>🛒</Text></View>
          )}
          {medaillon && <View style={s.medaillon}><Logo src={fiche.logo} taille={26} /></View>}
        </Pressable>
      ) : (
        <Logo src={fiche.logo} taille={64} groupe={!fiche.proprietaire} />
      )}
      <View style={[s.flex, { gap: 4 }]}>
        {pr && !medaillon && <Text style={s.produitNom} numberOfLines={2}>{pr.nom}{quantite(pr.quantite)}</Text>}
        <View style={s.ligne}>
          {pr && !medaillon && <Logo src={fiche.logo} taille={24} />}
          <Text style={[s.titre, pr && s.titrePetit]} accessibilityRole="header" numberOfLines={2}>
            {fiche.nom}
            {pr && medaillon && quantite(pr.quantite) ? <Text style={s.petit}>{quantite(pr.quantite)}</Text> : null}
          </Text>
        </View>
        {fiche.proprietaire ? (
          <Pressable onPress={() => onMarque(fiche.proprietaire!.slug)} accessibilityRole="link" style={s.ligne}>
            <Logo src={fiche.proprietaire.logo} taille={20} groupe />
            <Text style={[s.proprio, s.flex]}>
              <Text style={s.proprioNom}>{fiche.proprietaire.nom}</Text>
              <Text style={s.petit}> · reçoit l'argent de vos achats</Text>
            </Text>
          </Pressable>
        ) : (
          <Text style={s.petit}>Groupe</Text>
        )}
      </View>
      {pr?.image && (
        <PhotoGrande uri={pr.image} visible={grand} fermer={() => setGrand(false)} />
      )}
    </View>
  );
}

/**
 * Marque (grand logo avec marge) et, à sa droite sur la même ligne, le groupe propriétaire (logo, nom, lien
 * vers sa fiche) ; « reçoit l'argent de vos achats » en infobulle (ⓘ). Passe à la ligne si les noms sont longs.
 */
function MarqueEtGroupe({ fiche, onMarque }: { fiche: TFiche; onMarque: (slug: string) => void }) {
  const [info, setInfo] = useState(false);
  const proprietaire = fiche.proprietaire;
  return (
    <View style={{ gap: 6 }}>
      <View style={s.marqueGroupe}>
        <Logo src={fiche.logo} taille={52} marge={6} />
        <View style={{ flex: 1, gap: 4 }}>
          <Text style={s.marqueB} accessibilityRole="header" numberOfLines={1}>{fiche.nom}</Text>
          {proprietaire && (
            <View style={[s.ligne, { gap: 6 }]}>
              <Pressable onPress={() => onMarque(proprietaire.slug)} accessibilityRole="link" accessibilityLabel={`Groupe ${proprietaire.nom}, ouvrir sa fiche`} style={[s.ligne, { gap: 6, flexShrink: 1 }]}>
                <Logo src={proprietaire.logo} taille={22} marge={2} groupe />
                <Text style={s.groupeB} numberOfLines={1}>{proprietaire.nom}</Text>
              </Pressable>
              <Pressable onPress={() => setInfo(!info)} accessibilityRole="button" accessibilityLabel="À quoi sert ce groupe ?" accessibilityState={{ expanded: info }} hitSlop={12} style={s.info}>
                <Text style={s.infoTexte}>ⓘ</Text>
              </Pressable>
            </View>
          )}
        </View>
      </View>
      {proprietaire && info && (
        <View style={s.bulle} accessibilityLiveRegion="polite">
          <Text style={s.bulleTexte}>{proprietaire.nom} possède la marque : c'est ce groupe qui reçoit l'argent de vos achats.</Text>
        </View>
      )}
    </View>
  );
}

/** Intitulé court d'un indicateur pour une étiquette (« Bien-être animal (classement BBFAW) » → « Bien-être animal »). */
const court = (t: string) => {
  const c = t.replace(/\s*\(.*\)\s*/, '').trim();
  return c.length > 30 ? c.slice(0, 29) + '…' : c;
};

/** Verdict court d'une alerte pour une étiquette (le motif complet reste dans le pilier). */
function verdict(a: TFiche['alertes'][number]): string {
  const m = a.motif;
  const note = m.match(/note ([A-F][+-]?)/)?.[1];
  switch (a.code) {
    case 'ANI_EXPLOITATION': return 'Exploitation animale';
    case 'ANI_BBFAW_TIER': return 'Bien-être animal : mal noté';
    case 'GEO_RUSSIA_EXIT': return 'Toujours en Russie';
    case 'GEO_CONFLICT_TIES': return 'Liens avec un conflit';
    case 'ENV_GHG_TREND': return /hausse/.test(m) ? 'Émissions en hausse' : 'Émissions : baisse trop lente';
    case 'ENV_CDP_CLIMATE': return /aucune réponse/.test(m) ? 'CDP climat : pas de réponse' : `CDP climat : ${note ?? 'note basse'}`;
    case 'WAT_CDP': return /aucune réponse/.test(m) ? 'CDP eau : pas de réponse' : `CDP eau : ${note ?? 'note basse'}`;
    case 'ENV_CDP_FORESTS': return /aucune réponse/.test(m) ? 'CDP forêts : pas de réponse' : `CDP forêts : ${note ?? 'note basse'}`;
    case 'ENV_SBTI_VALIDATED': return 'Objectif climat retiré';
    case 'ENV_GREENWASHING': return 'Écoblanchiment sanctionné';
    case 'PLA_POLLUTER': return 'Gros pollueur plastique';
    case 'PLA_REDUCTION': return 'Plastique neuf en hausse';
    case 'LAB_EGAPRO_INDEX': return `Égapro ${m.match(/(\d+)\/100/)?.[1] ?? ''}/100`.replace(' /100', ' bas');
    case 'LAB_GENDER_PAYGAP': return 'Écart de salaire F-H';
    case 'LAB_CEO_PAY_RATIO': return 'Écart de rémunération';
    case 'GOV_SANCTIONS': return 'Sanction';
    case 'GOV_BOARD_GENDER': case 'GOV_EXEC_GENDER': return 'Peu de femmes dirigeantes';
    case 'GOV_BOARD_INDEP': return 'Conseil peu indépendant';
    case 'TAX_EFFECTIVE_RATE': return 'Impôt faible';
    case 'SUP_FTI_SCORE': case 'SUP_KNOWTHECHAIN': case 'SUP_LIVING_WAGE': return 'Chaîne d\'approvisionnement';
    case 'WAT_CONTROVERSY': return 'Infraction sur l\'eau';
    default: return court(a.nom ?? m);
  }
}

/** En-tête C : chaque alerte ou point de vigilance en étiquette ; un toucher ouvre le pilier concerné. */
function EtiquettesAlertes({ alertes, ouvrirPilier }: { alertes: TFiche['alertes']; ouvrirPilier?: (code: string) => void }) {
  if (!alertes.length) return null;
  return (
    <View style={s.etiquettes}>
      {alertes.map((a, i) => {
        const al = a.niveau === 'alerte';
        return (
          <Pressable
            key={i}
            onPress={() => ouvrirPilier?.(a.pilier)}
            accessibilityRole="button"
            accessibilityLabel={`${al ? 'Alerte' : 'Point de vigilance'} : ${a.motif}`}
            style={({ pressed }) => [s.etiq, al ? s.etiqAlerte : s.etiqVigilance, pressed && { opacity: 0.6 }]}>
            <Text style={[s.etiqTexte, { color: al ? '#8f1f19' : C.vigilanceTexte }]} numberOfLines={1}>
              {al ? '⚠️' : '🟠'} {verdict(a)}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

/**
 * En-têtes B et E : une ligne « ⚠️ 2 alertes · 🟠 2 vigilances ». Toucher une entrée l'ouvre comme un
 * onglet de classeur (bordé de rouge ou d'orange) collé au panneau des motifs ; chaque motif ouvre son pilier.
 */
function Compteurs({ alertes, vigilance, ouvrirPilier }: { alertes: TFiche['alertes']; vigilance: TFiche['alertes']; ouvrirPilier?: (code: string) => void }) {
  const [ouvert, setOuvert] = useState<'alerte' | 'vigilance' | null>(null);
  if (!alertes.length && !vigilance.length) return null;
  const liste = ouvert === 'alerte' ? alertes : ouvert === 'vigilance' ? vigilance : [];
  const couleur = ouvert === 'alerte' ? C.alerte : '#d97a00';
  const onglet = (cle: 'alerte' | 'vigilance', n: number) => {
    if (!n) return null;
    const al = cle === 'alerte';
    const actif = ouvert === cle;
    const c = al ? C.alerte : '#d97a00';
    return (
      <Pressable
        onPress={() => setOuvert(actif ? null : cle)}
        accessibilityRole="tab"
        accessibilityState={{ selected: actif }}
        accessibilityLabel={`${n} ${al ? 'alerte' : 'point de vigilance'}${n > 1 ? 's' : ''}`}
        style={({ pressed }) => [s.onglet, { backgroundColor: c, borderColor: c }, !actif && s.ongletFerme, pressed && { opacity: 0.8 }]}>
        <Text style={[s.ongletTexte, { color: '#fff' }]}>
          {al ? '⚠️' : '🟠'} {n} {al ? `alerte${n > 1 ? 's' : ''}` : `vigilance${n > 1 ? 's' : ''}`} {actif ? '▲' : '▼'}
        </Text>
      </Pressable>
    );
  };
  return (
    <View>
      <View style={s.onglets} accessibilityRole="tablist">
        {onglet('alerte', alertes.length)}
        {onglet('vigilance', vigilance.length)}
      </View>
      {liste.length > 0 && (
        <View style={[s.classeur, { borderColor: couleur, borderTopLeftRadius: ouvert === 'alerte' || !alertes.length ? 0 : 12 }]}>
          {liste.map((a, i) => (
            <Pressable key={i} onPress={() => ouvrirPilier?.(a.pilier)} accessibilityRole="button" style={({ pressed }) => [s.ligneAlerte, i === liste.length - 1 && { borderBottomWidth: 0 }, pressed && { opacity: 0.6 }]}>
              <Text style={s.ligneAlerteTexte}>{a.icone} {a.motif}</Text>
            </Pressable>
          ))}
        </View>
      )}
    </View>
  );
}

type Motif = TFiche['alertes'][number] & { qui: string };

/** Qui est visé par un motif : la marque, ou le groupe propriétaire quand la donnée est celle du groupe. */
function motifsDe(fiche: TFiche): Motif[] {
  const niveauDe = (code?: string) => fiche.piliers.flatMap((p) => p.faits).find((f) => f.code === code)?.niveau;
  return fiche.alertes
    .map((a) => ({ ...a, qui: niveauDe(a.code) === 'groupe' && fiche.proprietaire ? fiche.proprietaire.nom : fiche.nom }))
    .sort((a, b) => (a.niveau === 'alerte' ? 0 : 1) - (b.niveau === 'alerte' ? 0 : 1));
}

/**
 * En-tête B : encadré noir façon avertissement de paquet, fermé par défaut (« ⚠️ Avertissement · 4 alertes,
 * 1 vigilance »). Ouvert, il lit chaque motif (« Mars — poursuit ses activités en Russie ») ; chaque ligne
 * ouvre la preuve dans son pilier.
 */
function Avertissement({ motifs, ouvrirMotif }: { motifs: Motif[]; ouvrirMotif: (m: Motif) => void }) {
  const [ouvert, setOuvert] = useState(false);
  if (!motifs.length) return null;
  const na = motifs.filter((m) => m.niveau === 'alerte').length;
  const nv = motifs.length - na;
  const compte = [na ? pluriel(na, 'alerte', 'alertes') : '', nv ? pluriel(nv, 'vigilance', 'vigilances') : ''].filter(Boolean).join(', ');
  return (
    <View style={s.avert}>
      <Pressable onPress={() => setOuvert(!ouvert)} accessibilityRole="button" accessibilityState={{ expanded: ouvert }} accessibilityLabel={`Avertissement : ${compte}`} style={({ pressed }) => [s.avertTete, pressed && { opacity: 0.7 }]}>
        <Text style={s.avertTitre}>AVERTISSEMENT</Text>
        <Text style={s.avertCompte}>{na ? `${EMOJI.alerte} ${na}` : ''}{na && nv ? '   ' : ''}{nv ? `${EMOJI.vigilance} ${nv}` : ''}</Text>
        <Text style={s.avertFleche}>{ouvert ? '▲' : '▼'}</Text>
      </Pressable>
      {ouvert && motifs.map((m, i) => (
        <Pressable key={i} onPress={() => ouvrirMotif(m)} accessibilityRole="button" accessibilityHint="Ouvre la preuve dans le pilier" style={({ pressed }) => [s.avertLigne, pressed && { opacity: 0.6 }]}>
          <Text style={s.avertEmoji}>{EMOJI[m.niveau]}</Text>
          <Text style={s.avertTexte}>
            <Text style={{ fontWeight: '800' }}>{m.qui}</Text> — {m.motif}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

/** La fiche d'une marque ou d'un groupe : en-tête, alertes, piliers. */
export function Fiche({ fiche, onMarque, defiler }: {
  fiche: TFiche; onMarque: (slug: string) => void;
  /** Fait défiler l'écran jusqu'à cette hauteur (en points depuis le haut de la fiche). */
  defiler?: (y: number) => void;
}) {
  const [liste, setListe] = useState(false);
  const [variante, setVariante] = useState<VarianteEnTete>('B');
  const [choix, setChoix] = useState<string | null>(null);
  const [deplie, setDeplie] = useState<string | null>(null);
  // Hauteurs mesurées pour amener le pilier ouvert à l'écran : bloc des pastilles, puis panneau dedans.
  const yZone = useRef(0);
  const yPastilles = useRef(0);
  const yPanneau = useRef<number | null>(null);
  const aDefiler = useRef(false);
  useEffect(() => {
    lire(CLE_AFFICHAGE).then((v) => setListe(v === 'liste'));
    lire(CLE_ENTETE).then((v) => setVariante(v === 'A' || v === 'C' || v === 'E' ? v : 'B'));
  }, []);
  const alertes = fiche.alertes.filter((a) => a.niveau === 'alerte');
  const vigilance = fiche.alertes.filter((a) => a.niveau === 'vigilance');
  const motifs = motifsDe(fiche);
  // Depuis l'en-tête : ouvre la pastille du pilier concerné (affichage en pastilles seulement), avec
  // l'indicateur visé déplié sur sa preuve, et l'amène à l'écran.
  const allerA = (y: number) => defiler?.(y);
  const ouvrirPilier = liste ? undefined : (code: string, codeFait?: string) => {
    setDeplie(codeFait ?? null);
    if (choix === code && yPanneau.current !== null) allerA(yZone.current + yPastilles.current + yPanneau.current);
    else aDefiler.current = true;
    setChoix(code);
  };
  const surPanneau = (y: number) => {
    yPanneau.current = y;
    if (aDefiler.current) {
      aDefiler.current = false;
      allerA(yZone.current + yPastilles.current + y);
    }
  };
  const ouvrirMotif = (m: Motif) => ouvrirPilier?.(m.pilier, m.code);
  return (
    <View>
      {/* Zone 1 : identité du produit et de son propriétaire, alertes. */}
      <View style={s.zoneIdentite}>
      <EnTete
        fiche={fiche}
        onMarque={onMarque}
        medaillon={variante === 'C'}
        bandeau={variante === 'B'}
      />
      {variante === 'C' && <EtiquettesAlertes alertes={fiche.alertes} ouvrirPilier={ouvrirPilier} />}
      {variante === 'B' && <Avertissement motifs={motifs} ouvrirMotif={ouvrirMotif} />}
      {variante === 'E' && <Compteurs alertes={alertes} vigilance={vigilance} ouvrirPilier={ouvrirPilier} />}

      {variante === 'A' && alertes.length > 0 && (
        <View style={s.bandeauAlerte} accessibilityRole="summary">
          <Text style={s.bandeauTitreAlerte}>⚠️ {alertes.length} alerte{alertes.length > 1 ? 's' : ''}</Text>
          {alertes.map((a, i) => (
            <Text key={i} style={s.bandeauLigneAlerte}>{a.icone} {a.motif}</Text>
          ))}
        </View>
      )}
      {variante === 'A' && vigilance.length > 0 && (
        <View style={s.bandeauVigilance}>
          <Text style={s.bandeauTitreVigilance}>🟠 {vigilance.length} point{vigilance.length > 1 ? 's' : ''} de vigilance</Text>
          {vigilance.map((a, i) => (
            <Text key={i} style={s.bandeauLigneVigilance}>{a.icone} {a.motif}</Text>
          ))}
        </View>
      )}

      </View>

      {/* Zone 2 : les piliers, sur un bandeau blanc pleine largeur. */}
      <View style={s.zonePiliers} onLayout={(e) => (yZone.current = e.nativeEvent.layout.y)}>
      <Text style={s.section} accessibilityRole="header">Pilier par pilier</Text>
      {liste ? (
        <View style={s.carteListe}>
          {fiche.piliers.map((p, i) => (
            <LignePilier key={p.code} p={p} dernier={i === fiche.piliers.length - 1} />
          ))}
        </View>
      ) : (
        <View onLayout={(e) => (yPastilles.current = e.nativeEvent.layout.y)}>
          <Pastilles fiche={fiche} choix={choix} setChoix={(c) => { setDeplie(null); setChoix(c); }} deplie={deplie} surPanneau={surPanneau} />
        </View>
      )}
      </View>

      {/* Zone 3 : informations complémentaires (couverture, origine du produit, produits lus). */}
      <View style={s.zoneComplements}>
      <Text style={s.zoneTitre} accessibilityRole="header">Informations complémentaires</Text>
      <Text style={s.pied}>
        {fiche.renseignes} informations documentées sur {fiche.total} recherchées · aucune note, que des faits sourcés.
      </Text>
      {fiche.produit && (
        <Text style={s.pied}>
          Produit : {fiche.produit.nom}{quantite(fiche.produit.quantite)}. {fiche.produit.phrase}{' '}
          <Text style={s.lienPied} onPress={() => ouvrir(fiche.produit!.lien)} accessibilityRole="link">D'après {fiche.produit.base} ↗</Text>
        </Text>
      )}

      {fiche.estMarque && liste && (
        <>
          <Text style={s.section} accessibilityRole="header">Ses produits</Text>
          {fiche.produitsLus && fiche.produitsLus.length > 0 ? (
            <ProduitsLus produits={fiche.produitsLus} />
          ) : (
            <Text style={s.petit}>Aucun produit lu pour l'instant : ni fiche du site de la marque, ni étiquette envoyée.</Text>
          )}
          <Pressable
            onPress={() => router.push({ pathname: '/etiquette/[slug]', params: { slug: fiche.slug, nom: fiche.nom } })}
            accessibilityRole="button"
            style={({ pressed }) => [s.boutonEtiquette, pressed && { opacity: 0.7 }]}>
            <Text style={s.boutonEtiquetteTexte}>📷 Ajouter l'étiquette d'un produit {fiche.nom}</Text>
          </Pressable>
        </>
      )}
      </View>
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
      {ouvert && <CorpsPilier p={p} teinte={teinte} pleins={pleins} vides={vides} plusieursNiveaux={plusieursNiveaux} />}
    </View>
  );
}

const majuscule = (t: string) => t[0].toUpperCase() + t.slice(1);

/** Ce qu'on lit en dépliant un pilier : faits documentés, indicateurs sans information, alternatives. */
function CorpsPilier({ p, teinte, pleins, vides, plusieursNiveaux, deplie }: { p: Pilier; teinte: string; pleins: Fait[]; vides: Fait[]; plusieursNiveaux: boolean; deplie?: string | null }) {
  return (
    <View style={s.corps}>
      {pleins.map((f) => <CarteFait key={f.code} f={f} teinte={teinte} niveau={plusieursNiveaux ? NIVEAU[f.niveau] : null} deplie={deplie === f.code} />)}
      {vides.length > 0 && <SansInformation faits={vides} toutVide={!pleins.length} />}
      <Alternatives p={p} teinte={teinte} />
    </View>
  );
}

/** Faits d'un pilier, triés comme dans la liste : alertes, vigilance, puis le reste ; vides à part. */
function trierFaits(p: Pilier) {
  const rang = (f: Fait) => (f.signal?.niveau === 'alerte' ? 0 : f.signal?.niveau === 'vigilance' ? 1 : 2);
  const pleins = p.faits.filter((f) => f.etat !== 'aucune_info').sort((a, b) => rang(a) - rang(b));
  const vides = p.faits.filter((f) => f.etat === 'aucune_info');
  return { pleins, vides, plusieursNiveaux: new Set(pleins.map((f) => f.niveau)).size > 1 };
}

/**
 * Fiche en pastilles : une pastille par pilier (icône, nom, état, nombre renseigné). Un appui déplie le
 * pilier juste sous la ligne de sa pastille ; un second appui le replie. Les produits ont leur pastille.
 * Les pastilles renseignées viennent d'abord, puis les pastilles sans information, estompées.
 */
function Pastilles({ fiche, choix, setChoix, deplie, surPanneau }: {
  fiche: TFiche; choix: string | null; setChoix: (c: string | null) => void;
  /** Indicateur à montrer déplié sur sa preuve (venu d'un motif d'alerte). */
  deplie?: string | null;
  /** Position du panneau ouvert dans le bloc des pastilles, pour le faire défiler à l'écran. */
  surPanneau?: (y: number) => void;
}) {
  // Position de chaque pastille, pour insérer le panneau après la dernière pastille de la même ligne.
  const [places, setPlaces] = useState<Record<string, { x: number; y: number; l: number }>>({});
  const p = fiche.piliers.find((x) => x.code === choix) ?? null;
  const teinte = choix === 'PRODUITS' ? '#2f7a3b' : p ? TEINTE[p.code] ?? C.accent : C.accent;
  const produits = fiche.estMarque ? fiche.produitsLus ?? [] : null;
  // Ordre d'affichage : les pastilles renseignées, puis les vides (ordre des piliers conservé dans chaque groupe).
  const ordre = [...fiche.piliers.map((x) => ({ code: x.code, vide: x.renseignes === 0 })), ...(produits ? [{ code: 'PRODUITS', vide: !produits.length }] : [])]
    .sort((a, b) => Number(a.vide) - Number(b.vide));
  const codes = ordre.map((o) => o.code);
  const ici = choix ? places[choix] : undefined;
  // Dernière pastille de la ligne de la pastille choisie (à défaut de mesure : la pastille elle-même).
  const apres = !choix ? null : ici ? [...codes].reverse().find((c) => places[c] && Math.abs(places[c].y - ici.y) < 4) ?? choix : choix;
  const mesurer = (code: string) => (e: { nativeEvent: { layout: { x: number; y: number; width: number } } }) => {
    // Lignes mesurées tout replié : une fois le panneau inséré, les pastilles suivantes descendent
    // sous lui, et ces positions-là ne disent plus quelle était la ligne d'origine.
    if (choix) return;
    const { x, y, width } = e.nativeEvent.layout;
    setPlaces((m) => (m[code] && m[code].x === x && m[code].y === y && m[code].l === width ? m : { ...m, [code]: { x, y, l: width } }));
  };

  const panneau = () => (
    <View key="panneau" style={s.panneauLigne} onLayout={(e) => surPanneau?.(e.nativeEvent.layout.y)}>
      {p && (() => {
        const { pleins, vides, plusieursNiveaux } = trierFaits(p);
        return (
          <View style={[s.panneau, { borderColor: teinte }]}>
            <View style={[s.ligne, { paddingHorizontal: 14 }]}>
              <Text style={{ fontSize: 20 }}>{p.icone}</Text>
              <Text style={[s.pilierNom, { color: teinte }]}>{p.nom.toUpperCase()}</Text>
            </View>
            <CorpsPilier p={p} teinte={teinte} pleins={pleins} vides={vides} plusieursNiveaux={plusieursNiveaux} deplie={deplie} />
          </View>
        );
      })()}
      {choix === 'PRODUITS' && (
        <View style={[s.panneau, { borderColor: teinte, padding: 14, gap: 12 }]}>
          {produits && produits.length > 0 ? (
            <ProduitsLus produits={produits} />
          ) : (
            <Text style={s.petit}>Aucun produit lu pour l'instant : ni fiche du site de la marque, ni étiquette envoyée.</Text>
          )}
          <Pressable
            onPress={() => router.push({ pathname: '/etiquette/[slug]', params: { slug: fiche.slug, nom: fiche.nom } })}
            accessibilityRole="button"
            style={({ pressed }) => [s.boutonEtiquette, pressed && { opacity: 0.7 }]}>
            <Text style={s.boutonEtiquetteTexte}>📷 Ajouter l'étiquette d'un produit {fiche.nom}</Text>
          </Pressable>
        </View>
      )}
    </View>
  );

  const pastilles = fiche.piliers.map((x) => {
    const t = TEINTE[x.code] ?? C.accent;
    // Point d'alerte ou de vigilance : d'après tous les indicateurs du pilier, pas seulement le premier.
    const sigs = x.faits.map((f) => f.signal?.niveau);
    const sig = sigs.includes('alerte') ? 'alerte' : sigs.includes('vigilance') ? 'vigilance' : null;
    const actif = choix === x.code;
    const vide = x.renseignes === 0;
    return (
      <Pressable
        key={x.code}
        onLayout={mesurer(x.code)}
        onPress={() => setChoix(actif ? null : x.code)}
        accessibilityRole="tab"
        accessibilityState={{ selected: actif }}
        accessibilityLabel={`${x.nom} : ${x.renseignes} sur ${x.total} renseignés${sig === 'alerte' ? ', alerte' : sig === 'vigilance' ? ', point de vigilance' : ''}`}
        style={({ pressed }) => [
          s.pastilleChip,
          { borderColor: actif ? t : C.bord, backgroundColor: actif ? t + '1f' : C.carte },
          vide && !actif && s.pastilleVide,
          pressed && { opacity: 0.6 },
        ]}>
        <Text style={{ fontSize: 16 }}>{x.icone}</Text>
        <Text style={[s.pastilleNom, { color: actif ? t : C.texte }]} numberOfLines={1}>{nomCourt(x.nom)}</Text>
        {sig && <Text style={s.pastilleSignal}>{EMOJI[sig]}</Text>}
        <Text style={s.pastilleCompte}>{x.renseignes}/{x.total}</Text>
      </Pressable>
    );
  });
  if (produits) {
    const actif = choix === 'PRODUITS';
    pastilles.push(
      <Pressable
        key="PRODUITS"
        onLayout={mesurer('PRODUITS')}
        onPress={() => setChoix(actif ? null : 'PRODUITS')}
        accessibilityRole="tab"
        accessibilityState={{ selected: actif }}
        accessibilityLabel={`Ingrédients des produits de la marque : ${produits.length} produit${produits.length > 1 ? 's' : ''} lus`}
        style={({ pressed }) => [s.pastilleChip, { borderColor: actif ? '#2f7a3b' : C.bord, backgroundColor: actif ? '#f1f9f2' : C.carte }, !produits.length && !actif && s.pastilleVide, pressed && { opacity: 0.6 }]}>
        <Text style={{ fontSize: 16 }}>🧾</Text>
        <Text style={[s.pastilleNom, { color: actif ? '#2f7a3b' : C.texte }]}>Ingrédients</Text>
        <Text style={s.pastilleCompte}>{produits.length}</Text>
      </Pressable>,
    );
  }
  // Le panneau prend toute la largeur juste après la dernière pastille de la ligne choisie.
  const triees = codes.map((c) => pastilles.find((el) => el.key === c)!);
  const contenu = apres ? triees.flatMap((el) => (el.key === apres ? [el, panneau()] : [el])) : triees;

  return (
    <View style={{ gap: 12 }}>
      <View style={s.pastilles} accessibilityRole="tablist">{contenu}</View>
      {!choix && <Text style={s.petit}>Touchez une pastille pour lire le détail du pilier.</Text>}
    </View>
  );
}

/** Nom de pilier raccourci pour une pastille (« Chaîne d'appro & droits humains » → « Chaîne d'appro »). */
function nomCourt(nom: string): string {
  const court = nom.replace(/\s*\(.*\)\s*/, '').split(/ & | et /)[0];
  return court.length > 22 ? court.slice(0, 21) + '…' : court;
}

/** Alternatives du pilier : marques du même secteur, d'un autre groupe, qui remplissent un critère affiché. */
function Alternatives({ p, teinte }: { p: Pilier; teinte: string }) {
  const a = p.alternatives;
  return (
    <View style={[s.alt, { borderColor: teinte + '66' }]}>
      <Text style={s.altTitre}>🔄 Alternatives dans le même secteur</Text>
      {a ? (
        <>
          <Text style={s.petit}>Marques d'autres groupes {a.critere}. Aucune note : c'est ce critère, et lui seul, qui les fait figurer ici.</Text>
          <View style={s.altListe}>
            {a.marques.map((m) => (
              <Pressable
                key={m.slug}
                onPress={() => router.push(`/fiche/${m.slug}`)}
                accessibilityRole="link"
                style={({ pressed }) => [s.altMarque, !m.second && s.altFort, pressed && { opacity: 0.6 }]}>
                <Logo src={m.logo} taille={26} />
                <Text style={s.altNom} numberOfLines={1}>
                  {m.nom}
                  {m.groupe ? <Text style={s.petit}> · {m.groupe}</Text> : null}
                  {m.second ? <Text style={s.petit}> · produits végétaux</Text> : null}
                </Text>
              </Pressable>
            ))}
            {a.autres > 0 && <Text style={s.petit}>et {a.autres} autre{a.autres > 1 ? 's' : ''}</Text>}
          </View>
        </>
      ) : (
        <Text style={s.petit}>Aucune marque du même secteur ne remplit encore le critère de ce pilier dans nos données.</Text>
      )}
    </View>
  );
}

const STATUT_PRODUIT: Record<ProduitLu['statut'], { texte: string; couleur: string }> = {
  ingredient_animal: { texte: "Ingrédient d'origine animale", couleur: C.alerteTexte },
  aucun_ingredient_animal_declare: { texte: 'Aucun ingrédient animal dans la liste lue', couleur: C.gris },
  vegetal_declare: { texte: 'Présenté comme végétal par la marque', couleur: '#2f7a3b' },
  vegetal_certifie: { texte: "Végétal, label d'un tiers", couleur: '#2f7a3b' },
};
const ORDRE: Record<ProduitLu['statut'], number> = { vegetal_certifie: 0, vegetal_declare: 1, aucun_ingredient_animal_declare: 2, ingredient_animal: 3 };

/** Produits lus (fiches du site de la marque, étiquettes photographiées) : ceux sans ingrédient animal d'abord. */
function ProduitsLus({ produits }: { produits: ProduitLu[] }) {
  const [voirAnimaux, setVoirAnimaux] = useState(false);
  const tries = [...produits].sort((a, b) => ORDRE[a.statut] - ORDRE[b.statut] || a.nom.localeCompare(b.nom, 'fr'));
  const sans = tries.filter((x) => x.statut !== 'ingredient_animal');
  const avec = tries.filter((x) => x.statut === 'ingredient_animal');
  return (
    <View style={{ gap: 10 }}>
      <Text style={s.petit}>
        Ingrédients lus sur {produits.length} produit{produits.length > 1 ? 's' : ''} (fiches du site de la marque ou étiquettes photographiées), dont {avec.length} avec un ingrédient d'origine animale.
      </Text>
      {sans.length > 0 && (
        <View style={s.sans}>
          <Text style={s.sansTitre}>🌱 Chez cette marque, sans ingrédient animal</Text>
          <Text style={s.petit}>« Végétal » : la marque le dit ou un label l'atteste. « Aucun ingrédient animal dans la liste lue » ne prouve pas qu'un produit est végétal.</Text>
          {sans.map((x) => <LigneProduit key={x.url} p={x} />)}
        </View>
      )}
      {avec.length > 0 && (
        <View style={s.vides}>
          <Pressable onPress={() => setVoirAnimaux(!voirAnimaux)} accessibilityRole="button" accessibilityState={{ expanded: voirAnimaux }} style={({ pressed }) => [s.videsTete, pressed && { opacity: 0.6 }]}>
            <Text style={[s.videsTitre, s.flex]}>{avec.length} produit{avec.length > 1 ? 's' : ''} avec un ingrédient d'origine animale</Text>
            <Text style={s.lienPetit}>{voirAnimaux ? 'Masquer ▲' : 'Voir ▼'}</Text>
          </Pressable>
          {voirAnimaux && avec.map((x) => <LigneProduit key={x.url} p={x} />)}
        </View>
      )}
    </View>
  );
}

function LigneProduit({ p }: { p: ProduitLu }) {
  const [ingr, setIngr] = useState(false);
  const st = STATUT_PRODUIT[p.statut];
  return (
    <View style={s.produitLu}>
      <Text style={s.produitLuNom}>{p.nom}</Text>
      <Text style={[s.produitLuStatut, { color: st.couleur }]}>{st.texte}{p.animaux.length ? ` : ${p.animaux.join(', ')}` : ''}</Text>
      {p.origine === 'etiquette' && (
        <Text style={s.petit}>
          📷 Étiquette envoyée par un lecteur, liste recopiée et relue
          {p.achat.date ? ` · achetée le ${dfr(p.achat.date)}` : ''}{p.achat.lieu ? ` (${p.achat.lieu})` : ''}
        </Text>
      )}
      <View style={s.ligne}>
        {p.ingredients && (
          <Pressable onPress={() => setIngr(!ingr)} accessibilityRole="button" accessibilityState={{ expanded: ingr }} hitSlop={8} style={s.bouton44}>
            <Text style={s.lienPetit}>{ingr ? 'Masquer les ingrédients ▲' : 'Ingrédients ▼'}</Text>
          </Pressable>
        )}
        <Pressable onPress={() => ouvrir(p.url)} accessibilityRole="link" hitSlop={8} style={s.bouton44}>
          <Text style={s.lienPetit}>{p.origine === 'etiquette' ? 'Photo ↗' : 'Fiche ↗'}</Text>
        </Pressable>
      </View>
      {ingr && p.ingredients && (
        <Text style={s.citationTexte}>
          « {p.ingredients} »{p.douteux.length ? ` — d'origine possiblement animale, non tranché : ${p.douteux.join(', ')}` : ''}
        </Text>
      )}
    </View>
  );
}

/**
 * Un indicateur documenté, en deux temps : d'abord le fait (nom, valeur, repère), puis, sur demande,
 * le détail (raison, note, seuil, solidité, citation de la source).
 */
function CarteFait({ f, teinte, niveau, deplie = false }: { f: Fait; teinte: string; niveau: string | null; deplie?: boolean }) {
  const [details, setDetails] = useState(deplie);
  // Un motif d'alerte qui désigne cet indicateur le déplie, même si le pilier était déjà ouvert.
  const [demande, setDemande] = useState(deplie);
  if (deplie !== demande) {
    setDemande(deplie);
    if (deplie) setDetails(true);
  }
  const [toute, setToute] = useState(false);
  const sig = f.signal?.niveau;
  const fond = sig === 'alerte' ? C.alerteFond : sig === 'vigilance' ? '#fffaf2' : C.carte;
  // Avec un signal, la valeur dit déjà le repère (« il faudrait 4,2 % ») : il passe dans le détail.
  const repereVisible = f.repere && !f.signal ? f.repere : null;
  const aDetail = !!(f.preuve || f.raison || f.note || f.signal || f.enSavoirPlus || (f.repere && !repereVisible));
  const sol = f.preuve ? SOLIDITE[f.preuve.solidite] : null;
  return (
    <View style={[s.fait, { backgroundColor: fond }]}>
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
          <Text style={s.lienPetit}>{details ? 'Moins ▲' : f.enSavoirPlus ? 'En savoir plus ▼' : 'Détail ▼'}</Text>
        </Pressable>
      )}

      {details && (
        <View style={s.details}>
          {f.enSavoirPlus && (
            <Text style={s.savoir}><Text style={s.gras}>En savoir plus · </Text>{f.enSavoirPlus}</Text>
          )}
          {f.raison && <Text style={s.detailTexte}>{majuscule(f.raison)}.</Text>}
          {/* Avec un signal, le seuil retenu dit déjà le repère. */}
          {f.repere && !repereVisible && !f.signal && <Text style={s.detailTexte}>{f.repere}</Text>}
          {f.signal && <Text style={s.detailTexte}><Text style={s.gras}>Seuil retenu : </Text>{f.signal.regle}</Text>}
          {f.note && <Text style={s.note}>{f.note}</Text>}
          {f.preuve && (
            <View style={s.source}>
              {sol && <Text style={[s.solidite, { color: sol.couleur, borderColor: sol.couleur }]}>{sol.texte}</Text>}
              <Text style={s.petit}>
                {f.preuve.source}, {dfr(f.preuve.date)}{f.preuve.reprisDe ? ` · ${f.preuve.reprisDe.startsWith('la filiale') ? 'donnée de' : 'donnée du groupe'} ${f.preuve.reprisDe}` : ''}
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
  // Trois zones : identité et alertes (sur le fond), piliers (bandeau blanc), compléments (bandeau grisé).
  // Les bandeaux débordent de la marge de l'écran (16) pour aller d'un bord à l'autre.
  zoneIdentite: { gap: 14, paddingBottom: 20 },
  zonePiliers: { gap: 12, marginHorizontal: -16, paddingHorizontal: 16, paddingTop: 16, paddingBottom: 22, backgroundColor: C.carte, borderTopWidth: 1, borderBottomWidth: 1, borderColor: C.bord },
  // Le bandeau grisé descend jusqu'en bas de l'écran, sous la marge réservée au bouton scanner.
  zoneComplements: { gap: 10, marginHorizontal: -16, paddingHorizontal: 16, paddingTop: 16, marginBottom: -MARGE_BOUTON, paddingBottom: MARGE_BOUTON + 16, backgroundColor: '#e9e6f3' },
  zoneTitre: { fontSize: 12.5, fontWeight: '800', letterSpacing: 0.6, color: C.gris, textTransform: 'uppercase' },
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
  fait: { borderRadius: 14, paddingHorizontal: 14, paddingTop: 14, paddingBottom: 4, gap: 6, borderWidth: 1, borderColor: C.bord },
  faitNom: { fontSize: 14, fontWeight: '600', color: C.gris },
  faitValeur: { fontSize: 19, lineHeight: 25, fontWeight: '800', color: C.texte },
  repere: { fontSize: 14, lineHeight: 20, color: C.texte },
  basFait: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 44, borderTopWidth: 1, borderTopColor: C.bord, marginTop: 6 },
  sourceCourte: { fontSize: 13, color: C.gris },
  lienPetit: { fontSize: 14, fontWeight: '700', color: C.accent },
  details: { gap: 10, paddingBottom: 10 },
  detailTexte: { fontSize: 14, lineHeight: 20, color: C.texte },
  gras: { fontWeight: '700' },
  savoir: { fontSize: 14, lineHeight: 21, color: C.texte, backgroundColor: C.carte2, borderRadius: 10, padding: 12, overflow: 'hidden' },
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
  lienPied: { fontSize: 13, fontWeight: '600', color: C.accent },
  enTete: { flexDirection: 'row', gap: 12, alignItems: 'center' },
  medaillon: { position: 'absolute', right: -6, bottom: -6, borderRadius: 8, backgroundColor: '#fff', padding: 1 },
  etiquettes: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  etiq: { borderRadius: 999, borderWidth: 1, paddingHorizontal: 10, minHeight: 34, justifyContent: 'center', maxWidth: '100%' },
  etiqAlerte: { backgroundColor: '#fde9e7', borderColor: '#f0c9c4' },
  etiqVigilance: { backgroundColor: C.vigilanceFond, borderColor: '#f2c48a' },
  etiqTexte: { fontSize: 13, fontWeight: '700' },
  compteurBloc: { flex: 1, borderRadius: 14, paddingVertical: 8, alignItems: 'center', minHeight: 56, justifyContent: 'center', borderWidth: 1, borderColor: 'transparent' },
  compteurAlerte: { backgroundColor: C.alerte },
  compteurVigilance: { backgroundColor: C.vigilanceFond, borderColor: '#f2c48a' },
  compteurVide: { backgroundColor: C.carte, borderColor: C.bord },
  compteurN: { fontSize: 22, fontWeight: '800' },
  compteurL: { fontSize: 13, fontWeight: '700' },
  onglets: { flexDirection: 'row', gap: 6, alignItems: 'flex-end', position: 'relative', zIndex: 2 },
  onglet: { paddingHorizontal: 12, minHeight: 40, justifyContent: 'center', borderWidth: 1.5, borderBottomWidth: 0, borderTopLeftRadius: 12, borderTopRightRadius: 12, marginBottom: -1.5, paddingBottom: 1.5 },
  ongletFerme: { borderBottomLeftRadius: 12, borderBottomRightRadius: 12, marginBottom: 0, paddingBottom: 0, borderBottomWidth: 1.5 },
  ongletTexte: { fontSize: 14.5, fontWeight: '800' },
  classeur: { backgroundColor: C.carte, borderWidth: 1.5, borderRadius: 12, position: 'relative', zIndex: 1 },
  // Photo du produit en bandeau blanc d'un bord à l'autre, collé sous la barre du haut (comme la zone des piliers).
  bandeauPhoto: { height: 220, marginHorizontal: -16, marginTop: -16, backgroundColor: '#fff', borderBottomWidth: 1, borderColor: C.bord, padding: 16 },
  bandeauImage: { flex: 1 },
  avert: { backgroundColor: '#111', borderRadius: 6, paddingHorizontal: 12, paddingVertical: 10, gap: 6, borderWidth: 3, borderColor: '#fff', outlineColor: '#111', outlineWidth: 2, outlineStyle: 'solid' },
  avertTitre: { color: '#fff', fontSize: 12.5, fontWeight: '800', letterSpacing: 0.8 },
  avertLigne: { flexDirection: 'row', alignItems: 'flex-start', gap: 8, paddingVertical: 3 },
  avertTete: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 32 },
  avertCompte: { flex: 1, color: '#fff', fontSize: 14, fontWeight: '700' },
  avertFleche: { color: '#fff', fontSize: 13 },
  avertEmoji: { fontSize: 13, lineHeight: 20 },
  avertTexte: { flex: 1, color: '#fff', fontSize: 14.5, lineHeight: 20 },
  marqueGroupe: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 4, paddingHorizontal: 2 },
  marqueB: { fontSize: 21, lineHeight: 26, fontWeight: '800', color: C.texte, flexShrink: 1 },
  groupeB: { fontSize: 15, fontWeight: '700', color: C.texte, textDecorationLine: 'underline', flexShrink: 1 },
  info: { width: 24, height: 24, borderRadius: 12, alignItems: 'center', justifyContent: 'center', backgroundColor: C.carte2 },
  infoTexte: { fontSize: 14, color: C.accent, fontWeight: '700' },
  bulle: { alignSelf: 'flex-start', backgroundColor: C.texte, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, maxWidth: '100%' },
  bulleTexte: { color: '#fff', fontSize: 13.5, lineHeight: 19 },
  loupe: { position: 'absolute', right: 8, bottom: 8, backgroundColor: 'rgba(22,15,46,0.75)', color: '#fff', fontSize: 12, fontWeight: '600', paddingHorizontal: 9, paddingVertical: 3, borderRadius: 999, overflow: 'hidden' },
  ligneAlerte: { paddingHorizontal: 12, paddingVertical: 10, minHeight: 44, borderBottomWidth: 1, borderBottomColor: C.bord },
  ligneAlerteTexte: { fontSize: 14, lineHeight: 20, color: C.texte, fontWeight: '600' },
  titrePetit: { fontSize: 22, flexShrink: 1 },
  voile: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 },
  photoGrande: { width: '100%', height: '80%' },
  alt: { borderWidth: 1, borderStyle: 'dashed', borderRadius: 10, padding: 12, gap: 8, backgroundColor: C.carte },
  altTitre: { fontSize: 14, fontWeight: '800', color: C.texte },
  altListe: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, alignItems: 'center' },
  altMarque: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 4, paddingLeft: 4, paddingRight: 10, borderRadius: 999, borderWidth: 1, borderColor: C.bord, backgroundColor: C.carte2, maxWidth: '100%', minHeight: 36 },
  altFort: { borderColor: '#9cc9a3', backgroundColor: '#f1f9f2' },
  altNom: { fontSize: 13.5, fontWeight: '600', color: C.texte, flexShrink: 1 },
  sans: { borderWidth: 1, borderColor: '#9cc9a3', backgroundColor: '#f1f9f2', borderRadius: 12, padding: 12, gap: 8 },
  sansTitre: { fontSize: 15, fontWeight: '800', color: '#2f7a3b' },
  produitLu: { borderTopWidth: 1, borderTopColor: C.bord, paddingTop: 8, gap: 2 },
  produitLuNom: { fontSize: 15, fontWeight: '700', color: C.texte },
  produitLuStatut: { fontSize: 14, fontWeight: '600' },
  pastilles: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  pastilleChip: { flexDirection: 'row', alignItems: 'center', gap: 6, minHeight: 44, paddingHorizontal: 12, borderRadius: 999, borderWidth: 1 },
  pastilleNom: { fontSize: 14, fontWeight: '700', flexShrink: 1 },
  pastilleCompte: { fontSize: 12.5, color: C.gris, fontWeight: '600' },
  point: { width: 8, height: 8, borderRadius: 4 },
  panneau: { backgroundColor: C.carte, borderRadius: 16, borderWidth: 1.5, paddingTop: 12, overflow: 'hidden' },
  panneauLigne: { width: '100%', paddingTop: 6 },
  pastilleVide: { opacity: 0.42, borderStyle: 'dashed' },
  pastilleSignal: { fontSize: 12 },
  boutonEtiquette: { borderWidth: 1, borderStyle: 'dashed', borderColor: C.accent, borderRadius: 12, padding: 14, minHeight: 48, justifyContent: 'center' },
  boutonEtiquetteTexte: { fontSize: 15, fontWeight: '700', color: C.accent },
});
