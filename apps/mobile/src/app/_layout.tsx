import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';

import { C } from '@/lib/couleurs';

SplashScreen.preventAutoHideAsync();

export default function Racine() {
  useEffect(() => {
    SplashScreen.hideAsync();
  }, []);
  return (
    <>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: C.fond },
          headerTintColor: C.accent,
          headerTitleStyle: { color: C.texte, fontWeight: '700' },
          headerBackTitle: 'Retour',
          contentStyle: { backgroundColor: C.fond },
        }}>
        <Stack.Screen name="index" options={{ headerShown: false, title: 'Accueil' }} />
        <Stack.Screen name="scanner" options={{ headerShown: false, presentation: 'fullScreenModal', title: 'Scanner' }} />
        <Stack.Screen name="code/[ean]" options={{ title: 'Produit scanné' }} />
        <Stack.Screen name="fiche/[slug]" options={{ title: 'Fiche' }} />
        <Stack.Screen name="recherche" options={{ title: 'Rechercher' }} />
        <Stack.Screen name="reglages" options={{ title: 'Réglages' }} />
      </Stack>
    </>
  );
}
