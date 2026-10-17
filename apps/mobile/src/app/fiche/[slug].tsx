import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { BoutonScanner, MARGE_BOUTON } from '@/components/bouton-scanner';
import { Chargement, Erreur } from '@/components/etat';
import { Fiche, titreFiche } from '@/components/fiche';
import { ErreurSite, ficheParSlug, type ReponseFiche } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** Fiche d'une marque ou d'un groupe (depuis la recherche ou le lien « Appartient à »). */
export default function FicheMarque() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const defile = useRef<ScrollView>(null);
  const [rep, setRep] = useState<ReponseFiche | null>(null);
  const [erreur, setErreur] = useState<ErreurSite | null>(null);
  const [tentative, setTentative] = useState(0);
  useEffect(() => {
    let vivant = true;
    ficheParSlug(String(slug))
      .then((r) => vivant && setRep(r))
      .catch((e) => vivant && setErreur(e instanceof ErreurSite ? e : new ErreurSite(String(e))));
    return () => {
      vivant = false;
    };
  }, [slug, tentative]);
  const reessayer = () => {
    setErreur(null);
    setRep(null);
    setTentative((n) => n + 1);
  };
  if (erreur) return <Erreur message={erreur.message} reessayer={reessayer} reglages={erreur.statut === 401} />;
  if (!rep) return <Chargement texte="Chargement de la fiche…" />;
  if (!rep.trouve) return <Text style={s.texte}>{rep.raison}</Text>;
  return (
    <View style={{ flex: 1 }}>
      <Stack.Screen options={{ title: titreFiche(rep.fiche) }} />
      <ScrollView ref={defile} contentContainerStyle={s.contenu}>
        <Fiche fiche={rep.fiche} onMarque={(x) => router.push(`/fiche/${x}`)} defiler={(y) => defile.current?.scrollTo({ y: y + 8, animated: true })} />
      </ScrollView>
      <BoutonScanner />
    </View>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 16, gap: 16, paddingBottom: MARGE_BOUTON },
  texte: { padding: 20, fontSize: 16, color: C.texte },
});
