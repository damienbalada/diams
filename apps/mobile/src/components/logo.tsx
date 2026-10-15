import { Image } from 'expo-image';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { adresseImage, entetes } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** Logo d'une marque ou d'un groupe ; à défaut, un pictogramme neutre (jamais une initiale). */
export function Logo({ src, taille, groupe }: { src: string | null | undefined; taille: number; groupe?: boolean }) {
  const [source, setSource] = useState<{ uri: string; headers?: Record<string, string> } | null>(null);
  useEffect(() => {
    let vivant = true;
    (async () => {
      const uri = await adresseImage(src);
      // Le mot de passe du site n'accompagne QUE les images du site lui-même (src relative, « /logos/… »),
      // et seulement s'il est saisi : jamais une image externe (Wikimedia, icônes de sites).
      const h = src && src.startsWith('/') ? await entetes() : {};
      // Pas d'objet d'en-têtes vide : sur le web, il ferait télécharger l'image par une requête réseau.
      if (vivant && uri) setSource('Authorization' in h ? { uri, headers: { Authorization: h.Authorization } } : { uri });
    })();
    return () => {
      vivant = false;
    };
  }, [src]);
  const cadre = { width: taille, height: taille, borderRadius: Math.round(taille * 0.22) };
  if (!source) {
    return (
      <View style={[s.vide, cadre]} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
        <Text style={{ fontSize: Math.round(taille * 0.45) }}>{groupe ? '🏢' : '🏷️'}</Text>
      </View>
    );
  }
  return <Image source={source} style={[s.logo, cadre]} contentFit="contain" accessibilityIgnoresInvertColors accessible={false} />;
}

const s = StyleSheet.create({
  logo: { backgroundColor: '#fff', borderWidth: 1, borderColor: C.bord, padding: 4 },
  vide: { backgroundColor: C.carte2, alignItems: 'center', justifyContent: 'center' },
});
