import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text } from 'react-native';

import { Chargement, Erreur } from '@/components/etat';
import { Fiche } from '@/components/fiche';
import { ErreurSite, ficheParSlug, type ReponseFiche } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** Fiche d'une marque ou d'un groupe (depuis la recherche ou le lien « Appartient à »). */
export default function FicheMarque() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
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
    <ScrollView contentContainerStyle={s.contenu}>
      <Fiche fiche={rep.fiche} onMarque={(x) => router.push(`/fiche/${x}`)} />
    </ScrollView>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 16, gap: 16, paddingBottom: 48 },
  texte: { padding: 20, fontSize: 16, color: C.texte },
});
