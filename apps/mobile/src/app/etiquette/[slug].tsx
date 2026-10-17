import { Image } from 'expo-image';
import { ImageManipulator, SaveFormat } from 'expo-image-manipulator';
import * as ImagePicker from 'expo-image-picker';
import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';

import { deposerEtiquette } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** « 17/10/2026 » → « 2026-10-17 » (vide ou invalide : rien). */
function dateIso(t: string): string | null {
  const m = t.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!m) return null;
  const iso = `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}`;
  return Number.isNaN(Date.parse(iso)) ? null : iso;
}

/**
 * Dépôt de la photo de l'étiquette d'un produit de la marque. La photo est réduite sur le téléphone
 * (2 000 pixels au plus) ; rien n'est publié avant qu'un éditeur ait recopié et relu la liste
 * d'ingrédients. Aucune donnée personnelle n'est demandée.
 */
export default function DepotEtiquette() {
  const { slug, nom } = useLocalSearchParams<{ slug: string; nom?: string }>();
  const [photo, setPhoto] = useState<{ uri: string } | null>(null);
  const [produit, setProduit] = useState('');
  const [date, setDate] = useState('');
  const [lieu, setLieu] = useState('');
  const [accord, setAccord] = useState(false);
  const [envoi, setEnvoi] = useState(false);
  const [message, setMessage] = useState<{ ok: boolean; texte: string } | null>(null);

  async function choisir(camera: boolean) {
    setMessage(null);
    if (camera) {
      const p = await ImagePicker.requestCameraPermissionsAsync();
      if (!p.granted) {
        setMessage({ ok: false, texte: "L'accès à l'appareil photo a été refusé. Vous pouvez choisir une photo déjà prise." });
        return;
      }
    }
    const options: ImagePicker.ImagePickerOptions = { mediaTypes: ['images'], quality: 1, exif: false };
    const r = camera ? await ImagePicker.launchCameraAsync(options) : await ImagePicker.launchImageLibraryAsync(options);
    if (r.canceled || !r.assets?.length) return;
    const a = r.assets[0];
    // Réduction : 2 000 pixels sur le plus grand côté, JPEG compressé (envoi rapide, sous la limite du site).
    const ctx = ImageManipulator.manipulate(a.uri);
    if (a.width && a.height && Math.max(a.width, a.height) > 2000) {
      ctx.resize(a.width >= a.height ? { width: 2000 } : { height: 2000 });
    }
    const img = await ctx.renderAsync();
    const res = await img.saveAsync({ compress: 0.8, format: SaveFormat.JPEG });
    setPhoto({ uri: res.uri });
  }

  async function envoyer() {
    const iso = date.trim() ? dateIso(date) : '';
    if (!photo) return setMessage({ ok: false, texte: "Ajoutez la photo de l'étiquette." });
    if (produit.trim().length < 2) return setMessage({ ok: false, texte: 'Indiquez le nom du produit.' });
    if (iso === null) return setMessage({ ok: false, texte: "Date d'achat au format JJ/MM/AAAA (ou laissez vide)." });
    if (!accord) return setMessage({ ok: false, texte: "Cochez l'autorisation : sans elle, la photo ne peut pas servir de pièce justificative." });
    setEnvoi(true);
    const r = await deposerEtiquette({
      slug: String(slug), produit: produit.trim(), dateAchat: iso, lieuAchat: lieu.trim(),
      photo: { uri: photo.uri, type: 'image/jpeg', nom: 'etiquette.jpg' },
    });
    setEnvoi(false);
    setMessage(r.status === 'ok'
      ? { ok: true, texte: "Merci ! La photo est enregistrée. Nous recopierons la liste d'ingrédients et la relirons contre votre photo avant de publier quoi que ce soit ; la photo servira alors de pièce justificative." }
      : { ok: false, texte: r.message ?? "L'envoi n'a pas abouti. Réessayez plus tard." });
  }

  const fini = message?.ok;
  return (
    <ScrollView contentContainerStyle={s.contenu} keyboardShouldPersistTaps="handled">
      <Stack.Screen options={{ title: 'Étiquette' }} />
      <Text style={s.titre} accessibilityRole="header">Ajouter l'étiquette d'un produit {nom ?? ''}</Text>
      <Text style={s.texte}>
        Photographiez la <Text style={s.gras}>liste des ingrédients</Text>, lisible et en entier, avec le nom du produit si possible.
        Aucune donnée personnelle n'est demandée.
      </Text>

      {!fini && (
        <>
          <View style={s.ligne}>
            <Pressable onPress={() => choisir(true)} accessibilityRole="button" style={({ pressed }) => [s.bouton, pressed && s.presse]}>
              <Text style={s.boutonTexte}>📷 Prendre une photo</Text>
            </Pressable>
            <Pressable onPress={() => choisir(false)} accessibilityRole="button" style={({ pressed }) => [s.bouton, pressed && s.presse]}>
              <Text style={s.boutonTexte}>🖼️ Choisir une photo</Text>
            </Pressable>
          </View>
          {photo && <Image source={{ uri: photo.uri }} style={s.apercu} contentFit="contain" accessibilityLabel="Aperçu de la photo de l'étiquette" />}

          <Text style={s.label}>Nom du produit</Text>
          <TextInput value={produit} onChangeText={setProduit} placeholder="Ex. : Pâte à tartiner noisettes 400 g" style={s.champ} maxLength={200} />
          <Text style={s.label}>Date d'achat (facultatif)</Text>
          <TextInput value={date} onChangeText={setDate} placeholder="JJ/MM/AAAA" style={s.champ} keyboardType="numbers-and-punctuation" maxLength={10} />
          <Text style={s.label}>Lieu d'achat (facultatif : enseigne et ville)</Text>
          <TextInput value={lieu} onChangeText={setLieu} placeholder="Ex. : Carrefour Market, Lyon" style={s.champ} maxLength={200} />

          <View style={[s.ligne, { alignItems: 'flex-start' }]}>
            <Switch value={accord} onValueChange={setAccord} accessibilityLabel="Autorisation de publication de la photo" />
            <Text style={[s.texte, s.flex]}>
              J'ai pris cette photo moi-même et j'autorise sa publication et sa réutilisation libre (licence Creative Commons CC BY 4.0) comme pièce justificative.
            </Text>
          </View>
        </>
      )}

      {message && <Text style={[s.message, { color: message.ok ? '#2f7a3b' : C.alerteTexte }]}>{message.texte}</Text>}

      {fini ? (
        <Pressable onPress={() => router.back()} accessibilityRole="button" style={({ pressed }) => [s.principal, pressed && s.presse]}>
          <Text style={s.principalTexte}>Revenir à la fiche</Text>
        </Pressable>
      ) : (
        <Pressable onPress={envoyer} disabled={envoi} accessibilityRole="button" style={({ pressed }) => [s.principal, (pressed || envoi) && s.presse]}>
          {envoi ? <ActivityIndicator color={C.surAccent} /> : <Text style={s.principalTexte}>Envoyer l'étiquette</Text>}
        </Pressable>
      )}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 16, gap: 12, paddingBottom: 48 },
  titre: { fontSize: 24, fontWeight: '800', color: C.texte },
  texte: { fontSize: 15, lineHeight: 21, color: C.texte },
  gras: { fontWeight: '700' },
  flex: { flex: 1 },
  ligne: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  bouton: { flex: 1, minHeight: 48, borderRadius: 12, borderWidth: 1, borderColor: C.accent, alignItems: 'center', justifyContent: 'center', padding: 10, backgroundColor: C.carte },
  boutonTexte: { fontSize: 15, fontWeight: '700', color: C.accent },
  presse: { opacity: 0.6 },
  apercu: { width: '100%', height: 260, borderRadius: 12, backgroundColor: '#fff', borderWidth: 1, borderColor: C.bord },
  label: { fontSize: 14, fontWeight: '600', color: C.gris, marginTop: 4 },
  champ: { minHeight: 48, borderRadius: 12, borderWidth: 1, borderColor: C.bordFort, backgroundColor: C.carte, paddingHorizontal: 12, fontSize: 16, color: C.texte },
  message: { fontSize: 15, lineHeight: 21, fontWeight: '600' },
  principal: { minHeight: 52, borderRadius: 14, backgroundColor: C.accent, alignItems: 'center', justifyContent: 'center', marginTop: 6 },
  principalTexte: { fontSize: 17, fontWeight: '800', color: C.surAccent },
});
