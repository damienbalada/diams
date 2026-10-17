import { router } from 'expo-router';
import { Pressable, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { C } from '@/lib/couleurs';

/**
 * Bouton flottant du scanner, en bas à droite (accueil, fiches, recherche). Les écrans qui le portent
 * réservent une marge en bas de leur contenu (MARGE_BOUTON) pour qu'il ne cache rien.
 */
export const MARGE_BOUTON = 96;

export function BoutonScanner() {
  const bas = useSafeAreaInsets().bottom;
  return (
    <Pressable
      onPress={() => router.push('/scanner')}
      accessibilityRole="button"
      accessibilityLabel="Scanner un code-barres"
      style={({ pressed }) => [s.bouton, { bottom: 20 + bas }, pressed && { transform: [{ scale: 0.94 }], opacity: 0.9 }]}>
      <View style={s.barres} accessible={false} importantForAccessibility="no-hide-descendants">
        {[3, 1.5, 4, 1.5, 2.5, 4, 1.5, 3].map((l, i) => (
          <View key={i} style={{ width: l, height: 24, backgroundColor: '#fff', borderRadius: 1 }} />
        ))}
      </View>
    </Pressable>
  );
}

const s = StyleSheet.create({
  bouton: {
    position: 'absolute', right: 20, width: 62, height: 62, borderRadius: 31, backgroundColor: C.accent,
    alignItems: 'center', justifyContent: 'center',
    shadowColor: '#160f2e', shadowOpacity: 0.28, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 6,
  },
  barres: { flexDirection: 'row', gap: 2, alignItems: 'flex-end' },
});
