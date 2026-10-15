import { CameraView, useCameraPermissions, type BarcodeScanningResult } from 'expo-camera';
import { router } from 'expo-router';
import { useRef, useState } from 'react';
import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { C } from '@/lib/couleurs';

/** Lecture des codes-barres des produits (EAN-13, EAN-8, UPC). Aucune photo n'est gardée. */
export default function Scanner() {
  const [permission, demander] = useCameraPermissions();
  const [lampe, setLampe] = useState(false);
  const lu = useRef(false);

  const surCode = (r: BarcodeScanningResult) => {
    const code = (r.data ?? '').replace(/\D/g, '');
    if (lu.current || code.length < 8) return;
    lu.current = true;
    router.replace(`/code/${code}`);
  };

  if (!permission) return <View style={s.noir} />;
  if (!permission.granted) {
    return (
      <SafeAreaView style={[s.noir, s.centre]}>
        <Text style={s.titre}>Accès à l'appareil photo</Text>
        <Text style={s.texte}>
          Pour lire le code-barres d'un produit, l'appli a besoin de l'appareil photo. Aucune photo n'est gardée : seul le
          numéro du code est envoyé pour trouver la marque.
        </Text>
        {permission.canAskAgain ? (
          <Pressable onPress={demander} accessibilityRole="button" style={s.bouton}>
            <Text style={s.boutonTexte}>Autoriser l'appareil photo</Text>
          </Pressable>
        ) : (
          <Pressable onPress={() => Linking.openSettings()} accessibilityRole="button" style={s.bouton}>
            <Text style={s.boutonTexte}>Ouvrir les réglages du téléphone</Text>
          </Pressable>
        )}
        <Pressable onPress={() => router.replace('/')} accessibilityRole="button" style={s.secondaire}>
          <Text style={s.secondaireTexte}>Saisir le code à la main</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <View style={s.noir}>
      <CameraView
        style={StyleSheet.absoluteFill}
        facing="back"
        enableTorch={lampe}
        barcodeScannerSettings={{ barcodeTypes: ['ean13', 'ean8', 'upc_a', 'upc_e'] }}
        onBarcodeScanned={surCode}
      />
      <SafeAreaView style={s.calque} pointerEvents="box-none">
        <View style={s.barre}>
          <Pressable onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))} accessibilityRole="button" accessibilityLabel="Fermer le scanner" style={s.rond} hitSlop={6}>
            <Text style={s.rondTexte}>✕</Text>
          </Pressable>
          <Text style={s.barreTitre}>Scanner</Text>
          <Pressable
            onPress={() => setLampe(!lampe)}
            accessibilityRole="switch"
            accessibilityState={{ checked: lampe }}
            accessibilityLabel="Lampe"
            style={[s.rond, lampe && { backgroundColor: '#ffd84d' }]}
            hitSlop={6}>
            <Text style={[s.rondTexte, lampe && { color: '#000' }]}>⚡</Text>
          </Pressable>
        </View>
        <View style={s.cadreZone} pointerEvents="none">
          <View style={s.cadre} />
          <Text style={s.consigne}>Placez le code-barres dans le cadre. La fiche s'ouvre dès qu'il est lu.</Text>
        </View>
        <Text style={s.mention}>Aucune photo n'est gardée : seul le numéro du code est envoyé.</Text>
      </SafeAreaView>
    </View>
  );
}

const s = StyleSheet.create({
  noir: { flex: 1, backgroundColor: '#111016' },
  centre: { alignItems: 'center', justifyContent: 'center', padding: 24, gap: 16 },
  titre: { color: '#fff', fontSize: 24, fontWeight: '800', textAlign: 'center' },
  texte: { color: '#dcd8e8', fontSize: 16, lineHeight: 23, textAlign: 'center' },
  bouton: { backgroundColor: C.accent, borderRadius: 14, minHeight: 52, paddingHorizontal: 20, alignItems: 'center', justifyContent: 'center', alignSelf: 'stretch' },
  boutonTexte: { color: '#fff', fontSize: 17, fontWeight: '700' },
  secondaire: { minHeight: 48, justifyContent: 'center' },
  secondaireTexte: { color: '#cfc6ff', fontSize: 16, fontWeight: '600' },
  calque: { flex: 1, justifyContent: 'space-between', padding: 16 },
  barre: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  barreTitre: { color: '#fff', fontSize: 17, fontWeight: '700' },
  rond: { width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(30,28,38,0.85)', alignItems: 'center', justifyContent: 'center' },
  rondTexte: { color: '#fff', fontSize: 20, fontWeight: '700' },
  cadreZone: { alignItems: 'center', gap: 18 },
  cadre: { width: 300, height: 180, borderRadius: 22, borderWidth: 4, borderColor: '#fff' },
  consigne: { color: '#fff', fontSize: 17, lineHeight: 24, textAlign: 'center', maxWidth: 300, textShadowColor: '#000', textShadowRadius: 6 },
  mention: { color: '#e4e0ee', fontSize: 14, textAlign: 'center', textShadowColor: '#000', textShadowRadius: 6 },
});
