import { Link } from 'expo-router';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { C } from '@/lib/couleurs';

export function Chargement({ texte }: { texte: string }) {
  return (
    <View style={s.centre} accessibilityLiveRegion="polite">
      <ActivityIndicator size="large" color={C.accent} />
      <Text style={s.texte}>{texte}</Text>
    </View>
  );
}

/** Erreur réseau ou site privé : le message, et de quoi réessayer ou régler. */
export function Erreur({ message, reessayer, reglages }: { message: string; reessayer: () => void; reglages?: boolean }) {
  return (
    <View style={s.boite} accessibilityLiveRegion="assertive">
      <Text style={s.titre}>Impossible d'afficher la fiche</Text>
      <Text style={s.texte}>{message}</Text>
      <Pressable onPress={reessayer} accessibilityRole="button" style={s.bouton}>
        <Text style={s.boutonTexte}>Réessayer</Text>
      </Pressable>
      {reglages && (
        <Link href="/reglages" asChild>
          <Pressable accessibilityRole="button" style={s.secondaire}>
            <Text style={s.secondaireTexte}>Ouvrir les réglages</Text>
          </Pressable>
        </Link>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  centre: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 14, padding: 24 },
  boite: { gap: 12, padding: 20 },
  titre: { fontSize: 24, fontWeight: '800', color: C.texte },
  texte: { fontSize: 16, lineHeight: 23, color: C.gris },
  bouton: { backgroundColor: C.accent, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center' },
  boutonTexte: { color: '#fff', fontSize: 17, fontWeight: '700' },
  secondaire: { backgroundColor: C.carte, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: C.bordFort },
  secondaireTexte: { color: C.texte, fontSize: 17, fontWeight: '600' },
});
