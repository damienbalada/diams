import { Link, useFocusEffect, router } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BoutonScanner, MARGE_BOUTON } from '@/components/bouton-scanner';
import { historique, type Scan } from '@/lib/api';
import { C } from '@/lib/couleurs';

export default function Accueil() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [code, setCode] = useState('');
  useFocusEffect(
    useCallback(() => {
      historique().then(setScans);
    }, []),
  );
  const ouvrirCode = () => {
    const c = code.replace(/\D/g, '');
    if (c.length >= 8) router.push(`/code/${c}`);
  };
  return (
    <SafeAreaView style={s.ecran} edges={['top']}>
      <ScrollView contentContainerStyle={s.contenu} keyboardShouldPersistTaps="handled">
        <View style={s.haut}>
          <Text style={s.titre} accessibilityRole="header">Index des marques</Text>
          <Link href="/reglages" asChild>
            <Pressable accessibilityRole="button" accessibilityLabel="Réglages" style={s.rond} hitSlop={6}>
              <Text style={{ fontSize: 20 }}>⚙️</Text>
            </Pressable>
          </Link>
        </View>
        <Text style={s.sousTitre}>Qui fabrique ce que vous achetez, et ce que disent les sources officielles.</Text>

        <Link href="/recherche" asChild>
          <Pressable accessibilityRole="search" style={s.recherche}>
            <Text style={s.rechercheTexte}>🔍  Rechercher une marque ou un groupe</Text>
          </Pressable>
        </Link>

        <View style={s.saisie}>
          <Text style={s.label} nativeID="label-code">Ou saisir le code à la main</Text>
          <View style={s.ligne}>
            <TextInput
              value={code}
              onChangeText={setCode}
              keyboardType="number-pad"
              placeholder="3017620422003"
              placeholderTextColor={C.grisClair}
              accessibilityLabelledBy="label-code"
              style={s.champ}
              returnKeyType="go"
              onSubmitEditing={ouvrirCode}
              maxLength={14}
            />
            <Pressable onPress={ouvrirCode} accessibilityRole="button" style={s.ok}>
              <Text style={s.okTexte}>Voir</Text>
            </Pressable>
          </View>
        </View>

        <Text style={s.section} accessibilityRole="header">Derniers scans</Text>
        {scans.length === 0 ? (
          <Text style={s.vide}>Vos scans apparaîtront ici. Ils restent sur votre téléphone.</Text>
        ) : (
          <View style={s.liste}>
            {scans.map((x, i) => (
              <Link key={x.code} href={`/code/${x.code}`} asChild>
                <Pressable style={StyleSheet.flatten([s.ligneScan, i < scans.length - 1 && s.sep])} accessibilityRole="button">
                  <View style={{ flex: 1 }}>
                    <Text style={s.scanProduit}>{x.produit}</Text>
                    <Text style={s.scanMarque}>{x.marque}</Text>
                  </View>
                  {x.alertes > 0 && <Text style={s.badge}>{x.alertes} alerte{x.alertes > 1 ? 's' : ''}</Text>}
                </Pressable>
              </Link>
            ))}
          </View>
        )}
      </ScrollView>
      <BoutonScanner />
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  ecran: { flex: 1, backgroundColor: C.fond },
  contenu: { padding: 20, gap: 16, paddingBottom: MARGE_BOUTON },
  haut: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  titre: { fontSize: 32, fontWeight: '800', color: C.texte, flex: 1 },
  rond: { width: 44, height: 44, borderRadius: 22, backgroundColor: C.carte2, alignItems: 'center', justifyContent: 'center' },
  sousTitre: { fontSize: 16, lineHeight: 22, color: C.gris },
  recherche: { backgroundColor: C.carte, borderRadius: 14, borderWidth: 1, borderColor: C.bordFort, minHeight: 52, justifyContent: 'center', paddingHorizontal: 16 },
  rechercheTexte: { fontSize: 16, color: C.gris },
  saisie: { gap: 6 },
  label: { fontSize: 14, fontWeight: '600', color: C.texte },
  ligne: { flexDirection: 'row', gap: 8 },
  champ: { flex: 1, height: 50, backgroundColor: C.carte, borderRadius: 12, borderWidth: 1, borderColor: C.bordFort, paddingHorizontal: 14, fontSize: 17, color: C.texte },
  ok: { height: 50, paddingHorizontal: 18, borderRadius: 12, backgroundColor: C.texte, alignItems: 'center', justifyContent: 'center' },
  okTexte: { color: '#fff', fontWeight: '700', fontSize: 16 },
  section: { fontSize: 21, fontWeight: '800', color: C.texte, marginTop: 6 },
  vide: { fontSize: 15, color: C.gris },
  liste: { backgroundColor: C.carte, borderRadius: 16, borderWidth: 1, borderColor: C.bord },
  ligneScan: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14, minHeight: 64 },
  sep: { borderBottomWidth: 1, borderBottomColor: C.bord },
  scanProduit: { fontSize: 16, fontWeight: '700', color: C.texte },
  scanMarque: { fontSize: 14, color: C.gris },
  badge: { backgroundColor: C.alerte, color: '#fff', fontSize: 13, fontWeight: '800', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 999, overflow: 'hidden' },
});
