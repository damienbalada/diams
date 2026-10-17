import { Image } from 'expo-image';
import { Link, router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Chargement, Erreur } from '@/components/etat';
import { BoutonScanner, MARGE_BOUTON } from '@/components/bouton-scanner';
import { Fiche, titreFiche } from '@/components/fiche';
import { ErreurSite, ficheParCode, noterScan, type ReponseFiche } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** Produit scanné : code → produit → marque → fiche. */
export default function ProduitScanne() {
  const { ean } = useLocalSearchParams<{ ean: string }>();
  const defile = useRef<ScrollView>(null);
  const [rep, setRep] = useState<ReponseFiche | null>(null);
  const [erreur, setErreur] = useState<ErreurSite | null>(null);

  const [tentative, setTentative] = useState(0);
  useEffect(() => {
    let vivant = true;
    (async () => {
      try {
        const r = await ficheParCode(String(ean));
        if (!vivant) return;
        setRep(r);
        if (r.trouve && r.fiche.produit) {
          await noterScan({
            code: String(ean), produit: r.fiche.produit.nom, marque: r.fiche.nom,
            alertes: r.fiche.alertes.filter((a) => a.niveau === 'alerte').length, date: new Date().toISOString(),
          });
        }
      } catch (e) {
        if (vivant) setErreur(e instanceof ErreurSite ? e : new ErreurSite(String(e)));
      }
    })();
    return () => {
      vivant = false;
    };
  }, [ean, tentative]);
  const reessayer = () => {
    setErreur(null);
    setRep(null);
    setTentative((n) => n + 1);
  };
  if (erreur) return <Erreur message={erreur.message} reessayer={reessayer} reglages={erreur.statut === 401} />;
  if (!rep) return <Chargement texte="Recherche du produit…" />;
  if (!rep.trouve) {
    if (rep.indisponible) return <Erreur message={rep.raison} reessayer={reessayer} />;
    return (
      <ScrollView contentContainerStyle={s.contenu}>
        <Text style={s.titre} accessibilityRole="header">Ce produit n'est pas encore dans l'Index</Text>
        {rep.produit && (
          <View style={s.produit}>
            {rep.produit.image ? <Image source={{ uri: rep.produit.image }} style={s.photo} contentFit="contain" accessible={false} /> : null}
            <Text style={s.produitNom}>{rep.produit.nom}</Text>
          </View>
        )}
        <Text style={s.texte}>{rep.raison}</Text>
        <Text style={s.code}>Code lu : {ean}</Text>
        <Pressable
          onPress={() => router.push({
            pathname: '/produit-inconnu/[ean]',
            params: { ean: String(ean), nom: rep.produit?.nom ?? '', marque: rep.produit?.marques?.[0] ?? '' },
          })}
          accessibilityRole="button"
          accessibilityHint="Ouvre l'envoi de photos du produit"
          style={[s.bouton, { paddingHorizontal: 16, paddingVertical: 10 }]}>
          <Text style={[s.boutonTexte, { textAlign: 'center' }]}>📷 Aidez-nous : envoyez des photos du produit</Text>
        </Pressable>
        <Link href="/recherche" asChild>
          <Pressable accessibilityRole="button" style={s.secondaire}>
            <Text style={s.secondaireTexte}>Chercher la marque par son nom</Text>
          </Pressable>
        </Link>
        <Pressable onPress={() => router.replace('/scanner')} accessibilityRole="button" style={s.secondaire}>
          <Text style={s.secondaireTexte}>Scanner un autre produit</Text>
        </Pressable>
        <Text style={s.petit}>
          L'absence d'une marque n'est pas un jugement sur elle : l'Index ne couvre pas encore tout. Une marque n'est ajoutée
          qu'une fois son propriétaire confirmé par un document officiel.
        </Text>
      </ScrollView>
    );
  }
  return (
    <View style={{ flex: 1 }}>
      <Stack.Screen options={{ title: titreFiche(rep.fiche) }} />
      <ScrollView ref={defile} contentContainerStyle={[s.contenu, { paddingBottom: MARGE_BOUTON }]}>
        <Fiche fiche={rep.fiche} onMarque={(slug) => router.push(`/fiche/${slug}`)} defiler={(y) => defile.current?.scrollTo({ y: y + 8, animated: true })} />
      </ScrollView>
      <BoutonScanner />
    </View>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 16, gap: 16, paddingBottom: 48 },
  titre: { fontSize: 26, fontWeight: '800', color: C.texte },
  produit: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  photo: { width: 64, height: 64, borderRadius: 12, backgroundColor: '#fff' },
  produitNom: { fontSize: 17, fontWeight: '700', color: C.texte, flex: 1 },
  texte: { fontSize: 16, lineHeight: 23, color: C.texte },
  code: { fontSize: 14, color: C.gris },
  petit: { fontSize: 14, lineHeight: 20, color: C.gris },
  bouton: { backgroundColor: C.accent, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center' },
  boutonTexte: { color: '#fff', fontSize: 17, fontWeight: '700' },
  secondaire: { backgroundColor: C.carte, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: C.bordFort },
  secondaireTexte: { color: C.texte, fontSize: 17, fontWeight: '600' },
});
