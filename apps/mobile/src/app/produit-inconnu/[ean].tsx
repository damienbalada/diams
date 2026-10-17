import { Image } from 'expo-image';
import { ImageManipulator, SaveFormat } from 'expo-image-manipulator';
import * as ImagePicker from 'expo-image-picker';
import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';

import { envoyerProduitInconnu } from '@/lib/api';
import { C } from '@/lib/couleurs';

type Champ = 'photo_face' | 'photo_dos' | 'photo_ingredients';
const PHOTOS: { champ: Champ; titre: string; aide: string }[] = [
  { champ: 'photo_face', titre: 'Face avant', aide: 'Le nom du produit et la marque, bien lisibles.' },
  { champ: 'photo_dos', titre: 'Dos : le fabricant', aide: '« Fabriqué par », « fabriqué pour » ou « distribué par », avec l’adresse.' },
  { champ: 'photo_ingredients', titre: 'Ingrédients', aide: 'Pour un produit alimentaire : la liste des ingrédients en entier.' },
];

/**
 * Produit non reconnu : le lecteur envoie des photos (face, dos, ingrédients) pour que l'équipe trouve la
 * marque et son propriétaire. Photos réduites sur le téléphone (1 600 pixels au plus) pour que l'envoi
 * reste léger. Aucune donnée personnelle n'est demandée ; rien n'est publié sans vérification.
 */
export default function ProduitInconnu() {
  const { ean, nom, marque } = useLocalSearchParams<{ ean: string; nom?: string; marque?: string }>();
  const [photos, setPhotos] = useState<Partial<Record<Champ, string>>>({});
  const [produit, setProduit] = useState(nom ?? '');
  const [nomMarque, setNomMarque] = useState(marque ?? '');
  const [alimentaire, setAlimentaire] = useState<boolean | null>(null);
  const [lieu, setLieu] = useState('');
  const [accord, setAccord] = useState(false);
  const [envoi, setEnvoi] = useState(false);
  const [message, setMessage] = useState<{ ok: boolean; texte: string } | null>(null);

  async function choisir(champ: Champ, camera: boolean) {
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
    // Trois photos par envoi : 1 600 pixels et JPEG compressé, pour rester sous la limite du site.
    const ctx = ImageManipulator.manipulate(a.uri);
    if (a.width && a.height && Math.max(a.width, a.height) > 1600) {
      ctx.resize(a.width >= a.height ? { width: 1600 } : { height: 1600 });
    }
    const img = await ctx.renderAsync();
    const res = await img.saveAsync({ compress: 0.7, format: SaveFormat.JPEG });
    setPhotos((p) => ({ ...p, [champ]: res.uri }));
  }

  async function envoyer() {
    if (!photos.photo_face) return setMessage({ ok: false, texte: 'Ajoutez au moins la photo de la face avant.' });
    if (!accord) return setMessage({ ok: false, texte: "Cochez l'autorisation : sans elle, les photos ne peuvent pas servir." });
    setEnvoi(true);
    const r = await envoyerProduitInconnu({
      code: String(ean), produit: produit.trim(), marque: nomMarque.trim(), alimentaire, lieuAchat: lieu.trim(),
      photos: (Object.entries(photos) as [Champ, string][]).map(([champ, uri]) => ({ champ, uri })),
    });
    setEnvoi(false);
    setMessage(r.status === 'ok'
      ? { ok: true, texte: 'Merci ! Vos photos sont enregistrées. Nous allons identifier la marque et le groupe qui la possède, preuve à l’appui, avant de l’ajouter à l’Index.' }
      : { ok: false, texte: r.message ?? "L'envoi n'a pas abouti. Réessayez plus tard." });
  }

  const fini = message?.ok;
  return (
    <ScrollView contentContainerStyle={s.contenu} keyboardShouldPersistTaps="handled">
      <Stack.Screen options={{ title: 'Photos du produit' }} />
      <Text style={s.titre} accessibilityRole="header">Aidez-nous à ajouter ce produit</Text>
      <Text style={s.texte}>
        Envoyez quelques photos : nous y lirons la marque et le fabricant, puis nous chercherons le groupe qui la possède dans les
        registres officiels. Aucune donnée personnelle n'est demandée.
      </Text>
      <Text style={s.code}>Code-barres : {ean}</Text>

      {!fini && (
        <>
          {PHOTOS.map((p) => (
            <View key={p.champ} style={s.carte}>
              <Text style={s.sousTitre}>{p.titre}{p.champ === 'photo_face' ? '' : ' (facultatif)'}</Text>
              <Text style={s.aide}>{p.aide}</Text>
              <View style={s.ligne}>
                <Pressable onPress={() => choisir(p.champ, true)} accessibilityRole="button" accessibilityLabel={`Prendre la photo : ${p.titre}`} style={({ pressed }) => [s.bouton, pressed && s.presse]}>
                  <Text style={s.boutonTexte}>📷 Photo</Text>
                </Pressable>
                <Pressable onPress={() => choisir(p.champ, false)} accessibilityRole="button" accessibilityLabel={`Choisir une photo : ${p.titre}`} style={({ pressed }) => [s.bouton, pressed && s.presse]}>
                  <Text style={s.boutonTexte}>🖼️ Galerie</Text>
                </Pressable>
              </View>
              {photos[p.champ] && <Image source={{ uri: photos[p.champ] }} style={s.apercu} contentFit="contain" accessibilityLabel={`Aperçu : ${p.titre}`} />}
            </View>
          ))}

          <Text style={s.label}>Nom du produit (facultatif)</Text>
          <TextInput value={produit} onChangeText={setProduit} placeholder="Ex. : Liquide vaisselle citron 750 ml" style={s.champ} maxLength={200} />
          <Text style={s.label}>Marque inscrite sur le produit (facultatif)</Text>
          <TextInput value={nomMarque} onChangeText={setNomMarque} placeholder="Ex. : Paic" style={s.champ} maxLength={120} />
          <Text style={s.label}>Est-ce un produit alimentaire ?</Text>
          <View style={s.ligne} accessibilityRole="radiogroup">
            {([['Oui', true], ['Non', false]] as const).map(([lab, v]) => (
              <Pressable key={lab} onPress={() => setAlimentaire(alimentaire === v ? null : v)} accessibilityRole="radio" accessibilityState={{ checked: alimentaire === v }}
                style={[s.choix, alimentaire === v && s.choixActif]}>
                <Text style={[s.choixTexte, alimentaire === v && { color: C.accent }]}>{lab}</Text>
              </Pressable>
            ))}
          </View>
          <Text style={s.label}>Lieu d'achat (facultatif : enseigne et ville)</Text>
          <TextInput value={lieu} onChangeText={setLieu} placeholder="Ex. : Intermarché, Nantes" style={s.champ} maxLength={200} />

          <View style={[s.ligne, { alignItems: 'flex-start' }]}>
            <Switch value={accord} onValueChange={setAccord} accessibilityLabel="Autorisation d'utilisation des photos" />
            <Text style={[s.texte, s.flex]}>
              J'ai pris ces photos moi-même et j'autorise leur utilisation et leur publication libre (licence Creative Commons CC BY 4.0) pour documenter ce produit.
            </Text>
          </View>
        </>
      )}

      {message && <Text style={[s.message, { color: message.ok ? '#2f7a3b' : C.alerteTexte }]}>{message.texte}</Text>}

      {fini ? (
        <Pressable onPress={() => router.back()} accessibilityRole="button" style={({ pressed }) => [s.principal, pressed && s.presse]}>
          <Text style={s.principalTexte}>Revenir</Text>
        </Pressable>
      ) : (
        <Pressable onPress={envoyer} disabled={envoi} accessibilityRole="button" style={({ pressed }) => [s.principal, (pressed || envoi) && s.presse]}>
          {envoi ? <ActivityIndicator color={C.surAccent} /> : <Text style={s.principalTexte}>Envoyer les photos</Text>}
        </Pressable>
      )}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 16, gap: 12, paddingBottom: 48 },
  titre: { fontSize: 24, fontWeight: '800', color: C.texte },
  texte: { fontSize: 15, lineHeight: 21, color: C.texte },
  code: { fontSize: 14, color: C.gris },
  flex: { flex: 1 },
  carte: { backgroundColor: C.carte, borderRadius: 14, borderWidth: 1, borderColor: C.bord, padding: 12, gap: 8 },
  sousTitre: { fontSize: 16, fontWeight: '800', color: C.texte },
  aide: { fontSize: 14, lineHeight: 19, color: C.gris },
  ligne: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  bouton: { flex: 1, minHeight: 48, borderRadius: 12, borderWidth: 1, borderColor: C.accent, alignItems: 'center', justifyContent: 'center', padding: 10, backgroundColor: C.carte },
  boutonTexte: { fontSize: 15, fontWeight: '700', color: C.accent },
  presse: { opacity: 0.6 },
  apercu: { width: '100%', height: 200, borderRadius: 12, backgroundColor: '#fff', borderWidth: 1, borderColor: C.bord },
  label: { fontSize: 14, fontWeight: '600', color: C.gris, marginTop: 4 },
  champ: { minHeight: 48, borderRadius: 12, borderWidth: 1, borderColor: C.bordFort, backgroundColor: C.carte, paddingHorizontal: 12, fontSize: 16, color: C.texte },
  choix: { flex: 1, minHeight: 44, borderRadius: 10, borderWidth: 1, borderColor: C.bordFort, alignItems: 'center', justifyContent: 'center', backgroundColor: C.carte },
  choixActif: { borderColor: C.accent, backgroundColor: C.carte2 },
  choixTexte: { fontSize: 15, fontWeight: '700', color: C.texte },
  message: { fontSize: 15, lineHeight: 21, fontWeight: '600' },
  principal: { minHeight: 52, borderRadius: 14, backgroundColor: C.accent, alignItems: 'center', justifyContent: 'center', marginTop: 6 },
  principalTexte: { fontSize: 17, fontWeight: '800', color: C.surAccent },
});
