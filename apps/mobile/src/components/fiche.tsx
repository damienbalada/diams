import { Image } from 'expo-image';
import { router } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { useEffect, useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';

import { Logo } from '@/components/logo';
import type { Fait, Fiche as TFiche, Pilier, ProduitLu } from '@/lib/api';
import { C, SOLIDITE, TEINTE } from '@/lib/couleurs';
import { lire } from '@/lib/stockage';

/** Réglage d'affichage de la fiche : pastilles par pilier (essai, par défaut) ou liste dépliable. */
export const CLE_AFFICHAGE = 'index.affichage';

const NIVEAU: Record<string, string> = { groupe: 'Groupe', marque: 'Marque', produit: 'Produits' };
const dfr = (d: string) => d.split('-').reverse().join('/');
const ouvrir = (url: string) => WebBrowser.openBrowserAsync(url);
/** Quantité affichée seulement si elle porte une unité (« 250 g », « 1,5 L ») : « 8 » seul ne dit rien. */
const quantite = (q: string | null) => (q && /\d\s*[a-zA-Zµ]/.test(q) ? ` · ${q}` : '');

/**
 * En-tête de fiche : photo du produit scanné (agrandie au toucher), logo et nom de la marque, logo et
 * nom du groupe propriétaire. Compact : la base produit est citée en bas de la fiche.
 */
function EnTete({ fiche, onMarque }: { fiche: TFiche; onMarque: (slug: string) => void }) {
  const [grand, setGrand] = useState(false);
  const pr = fiche.produit;
  return (
    <View style={s.enTete}>
      {pr ? (
        <Pressable onPress={() => pr.image && setGrand(true)} accessibilityRole="imagebutton" accessibilityLabel={`Photo du produit ${pr.nom}, l'agrandir`} disabled={!pr.image}>
          {pr.image ? (
            <Image source={{ uri: pr.image }} style={s.photo} contentFit="contain" />
          ) : (
            <View style={[s.photo, s.centre]}><Text style={{ fontSize: 28 }}>🛒</Text></View>
          )}
        </Pressable>
      ) : (
        <Logo src={fiche.logo} taille={64} groupe={!fiche.proprietaire} />
      )}
      <View style={[s.flex, { gap: 4 }]}>
        {pr && <Text style={s.produitNom} numberOfLines={2}>{pr.nom}{quantite(pr.quantite)}</Text>}
        <View style={s.ligne}>
          {pr && <Logo src={fiche.logo} taille={24} />}
          <Text style={[s.titre, pr && s.titrePetit]} accessibilityRole="header" numberOfLines={2}>{fiche.nom}</Text>
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
        <Modal visible={grand} transparent animationType="fade" onRequestClose={() => setGrand(false)}>
          <Pressable style={s.voile} onPress={() => setGrand(false)} accessibilityRole="button" accessibilityLabel="Fermer la photo">
            <Image source={{ uri: pr.image }} style={s.photoGrande} contentFit="contain" />
            <Text style={s.voileTexte}>Toucher pour fermer</Text>
          </Pressable>
        </Modal>
      )}
    </View>
  );
}

/** La fiche d'une marque ou d'un groupe : en-tête, alertes, piliers. */
export function Fiche({ fiche, onMarque }: { fiche: TFiche; onMarque: (slug: string) => void }) {
  const [liste, setListe] = useState(false);
  useEffect(() => {
    lire(CLE_AFFICHAGE).then((v) => setListe(v === 'liste'));
  }, []);
  const alertes = fiche.alertes.filter((a) => a.niveau === 'alerte');
  const vigilance = fiche.alertes.filter((a) => a.niveau === 'vigilance');
  return (
    <View style={s.pile}>
      <EnTete fiche={fiche} onMarque={onMarque} />

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
      {liste ? (
        <View style={s.carteListe}>
          {fiche.piliers.map((p, i) => (
            <LignePilier key={p.code} p={p} dernier={i === fiche.piliers.length - 1} />
          ))}
        </View>
      ) : (
        <Pastilles fiche={fiche} />
      )}
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
function CorpsPilier({ p, teinte, pleins, vides, plusieursNiveaux }: { p: Pilier; teinte: string; pleins: Fait[]; vides: Fait[]; plusieursNiveaux: boolean }) {
  return (
    <View style={s.corps}>
      {pleins.map((f) => <CarteFait key={f.code} f={f} teinte={teinte} niveau={plusieursNiveaux ? NIVEAU[f.niveau] : null} />)}
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
 * Fiche en pastilles (essai) : une pastille par pilier (icône, nom, état, nombre renseigné) ; un appui
 * déplie le contenu du pilier juste dessous, un second le replie. Les produits ont leur pastille.
 */
function Pastilles({ fiche }: { fiche: TFiche }) {
  const [choix, setChoix] = useState<string | null>(null);
  const p = fiche.piliers.find((x) => x.code === choix) ?? null;
  const teinte = p ? TEINTE[p.code] ?? C.accent : C.accent;
  const produits = fiche.estMarque ? fiche.produitsLus ?? [] : null;
  return (
    <View style={{ gap: 12 }}>
      <View style={s.pastilles} accessibilityRole="tablist">
        {fiche.piliers.map((x) => {
          const t = TEINTE[x.code] ?? C.accent;
          const sig = x.cle?.signal;
          const actif = choix === x.code;
          const vide = x.renseignes === 0;
          return (
            <Pressable
              key={x.code}
              onPress={() => setChoix(actif ? null : x.code)}
              accessibilityRole="tab"
              accessibilityState={{ selected: actif }}
              accessibilityLabel={`${x.nom} : ${x.renseignes} sur ${x.total} renseignés${sig === 'alerte' ? ', alerte' : sig === 'vigilance' ? ', point de vigilance' : ''}`}
              style={({ pressed }) => [
                s.pastilleChip,
                { borderColor: actif ? t : C.bord, backgroundColor: actif ? t + '1f' : C.carte },
                vide && !actif && { opacity: 0.7 },
                pressed && { opacity: 0.6 },
              ]}>
              <Text style={{ fontSize: 16 }}>{x.icone}</Text>
              <Text style={[s.pastilleNom, { color: actif ? t : C.texte }]} numberOfLines={1}>{nomCourt(x.nom)}</Text>
              {sig && <View style={[s.point, { backgroundColor: sig === 'alerte' ? C.alerte : '#d97a00' }]} />}
              <Text style={s.pastilleCompte}>{x.renseignes}/{x.total}</Text>
            </Pressable>
          );
        })}
        {produits && (
          <Pressable
            onPress={() => setChoix(choix === 'PRODUITS' ? null : 'PRODUITS')}
            accessibilityRole="tab"
            accessibilityState={{ selected: choix === 'PRODUITS' }}
            accessibilityLabel={`Ingrédients des produits de la marque : ${produits.length} produit${produits.length > 1 ? 's' : ''} lus`}
            style={({ pressed }) => [s.pastilleChip, { borderColor: choix === 'PRODUITS' ? '#2f7a3b' : C.bord, backgroundColor: choix === 'PRODUITS' ? '#f1f9f2' : C.carte }, pressed && { opacity: 0.6 }]}>
            <Text style={{ fontSize: 16 }}>🧾</Text>
            <Text style={[s.pastilleNom, { color: choix === 'PRODUITS' ? '#2f7a3b' : C.texte }]}>Ingrédients</Text>
            <Text style={s.pastilleCompte}>{produits.length}</Text>
          </Pressable>
        )}
      </View>

      {!choix && <Text style={s.petit}>Touchez une pastille pour lire le détail du pilier.</Text>}

      {p && (() => {
        const { pleins, vides, plusieursNiveaux } = trierFaits(p);
        return (
          <View style={[s.panneau, { borderColor: teinte }]}>
            <View style={[s.ligne, { paddingHorizontal: 14 }]}>
              <Text style={{ fontSize: 20 }}>{p.icone}</Text>
              <Text style={[s.pilierNom, { color: teinte }]}>{p.nom.toUpperCase()}</Text>
              <Pressable onPress={() => setChoix(null)} accessibilityRole="button" accessibilityLabel="Replier le pilier" hitSlop={10} style={s.bouton44}>
                <Text style={s.lienPetit}>Replier ▲</Text>
              </Pressable>
            </View>
            <CorpsPilier p={p} teinte={teinte} pleins={pleins} vides={vides} plusieursNiveaux={plusieursNiveaux} />
          </View>
        );
      })()}

      {choix === 'PRODUITS' && (
        <View style={[s.panneau, { borderColor: '#2f7a3b', padding: 14, gap: 12 }]}>
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
function CarteFait({ f, teinte, niveau }: { f: Fait; teinte: string; niveau: string | null }) {
  const [details, setDetails] = useState(false);
  const [toute, setToute] = useState(false);
  const sig = f.signal?.niveau;
  const fond = sig === 'alerte' ? C.alerteFond : sig === 'vigilance' ? '#fffaf2' : C.carte;
  const bordGauche = sig === 'alerte' ? C.alerte : sig === 'vigilance' ? '#d97a00' : teinte;
  // Avec un signal, la valeur dit déjà le repère (« il faudrait 4,2 % ») : il passe dans le détail.
  const repereVisible = f.repere && !f.signal ? f.repere : null;
  const aDetail = !!(f.preuve || f.raison || f.note || f.signal || f.enSavoirPlus || (f.repere && !repereVisible));
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
  titrePetit: { fontSize: 22, flexShrink: 1 },
  voile: { flex: 1, backgroundColor: 'rgba(10,6,24,0.92)', alignItems: 'center', justifyContent: 'center', padding: 16, gap: 12 },
  photoGrande: { width: '100%', height: '80%' },
  voileTexte: { color: '#fff', fontSize: 14, opacity: 0.8 },
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
  boutonEtiquette: { borderWidth: 1, borderStyle: 'dashed', borderColor: C.accent, borderRadius: 12, padding: 14, minHeight: 48, justifyContent: 'center' },
  boutonEtiquetteTexte: { fontSize: 15, fontWeight: '700', color: C.accent },
});
