/**
 * Petit stockage clé → valeur : coffre sécurisé du téléphone (expo-secure-store) sur iPhone et
 * Android ; sur l'aperçu web, où le coffre n'existe pas, le stockage local du navigateur.
 */
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

export async function lire(cle: string): Promise<string | null> {
  if (Platform.OS === 'web') {
    try {
      return globalThis.localStorage?.getItem(cle) ?? null;
    } catch {
      return null;
    }
  }
  return SecureStore.getItemAsync(cle);
}

export async function ecrire(cle: string, valeur: string | null): Promise<void> {
  if (Platform.OS === 'web') {
    try {
      if (valeur === null) globalThis.localStorage?.removeItem(cle);
      else globalThis.localStorage?.setItem(cle, valeur);
    } catch {
      /* stockage du navigateur indisponible : sans effet */
    }
    return;
  }
  if (valeur === null) await SecureStore.deleteItemAsync(cle);
  else await SecureStore.setItemAsync(cle, valeur);
}
