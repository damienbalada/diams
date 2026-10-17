import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';

import { effacerHistorique, enregistrerReglages, lireReglages, SITE_PAR_DEFAUT, type Reglages } from '@/lib/api';
import { CLE_AFFICHAGE, CLE_ENTETE, type VarianteEnTete } from '@/components/fiche';
import { C } from '@/lib/couleurs';
import { ecrire, lire } from '@/lib/stockage';

/** Adresse du site et mot de passe (tant que le site est privé), gardés dans le coffre du téléphone. */
export default function EcranReglages() {
  const [r, setR] = useState<Reglages | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [pastilles, setPastilles] = useState(true);
  const [entete, setEntete] = useState<VarianteEnTete>('B');
  useEffect(() => {
    lireReglages().then(setR);
    lire(CLE_AFFICHAGE).then((v) => setPastilles(v !== 'liste'));
    lire(CLE_ENTETE).then((v) => setEntete(v === 'A' || v === 'C' || v === 'E' ? v : 'B'));
  }, []);
  if (!r) return null;
  const enregistrer = async () => {
    await enregistrerReglages(r);
    setMessage('Réglages enregistrés.');
  };
  return (
    <ScrollView contentContainerStyle={s.contenu} keyboardShouldPersistTaps="handled">
      <Text style={s.texte}>
        Tant que le site de l'Index est privé, l'appli a besoin de son mot de passe. Il reste sur ce téléphone, dans son coffre
        sécurisé, et n'est envoyé qu'au site ci-dessous.
      </Text>
      <View style={s.champBloc}>
        <Text style={s.label} nativeID="l-site">Adresse du site</Text>
        <TextInput value={r.site} onChangeText={(site) => setR({ ...r, site })} autoCapitalize="none" autoCorrect={false} keyboardType="url" accessibilityLabelledBy="l-site" placeholder={SITE_PAR_DEFAUT} style={s.champ} />
      </View>
      <View style={s.champBloc}>
        <Text style={s.label} nativeID="l-util">Identifiant</Text>
        <TextInput value={r.utilisateur} onChangeText={(utilisateur) => setR({ ...r, utilisateur })} autoCapitalize="none" autoCorrect={false} accessibilityLabelledBy="l-util" style={s.champ} />
      </View>
      <View style={s.champBloc}>
        <Text style={s.label} nativeID="l-mdp">Mot de passe du site</Text>
        <TextInput value={r.motDePasse} onChangeText={(motDePasse) => setR({ ...r, motDePasse })} secureTextEntry autoCapitalize="none" autoCorrect={false} accessibilityLabelledBy="l-mdp" style={s.champ} />
      </View>
      <Pressable onPress={enregistrer} accessibilityRole="button" style={s.bouton}>
        <Text style={s.boutonTexte}>Enregistrer</Text>
      </Pressable>
      {message && <Text style={s.message} accessibilityLiveRegion="polite">{message}</Text>}
      <View style={s.option}>
        <View style={{ flex: 1, gap: 2 }}>
          <Text style={s.label}>Fiche en pastilles (essai)</Text>
          <Text style={s.petit}>Une pastille par pilier : le détail s'ouvre quand on la touche. Désactivé : tous les piliers en liste dépliable.</Text>
        </View>
        <Switch
          value={pastilles}
          onValueChange={async (v) => {
            setPastilles(v);
            await ecrire(CLE_AFFICHAGE, v ? null : 'liste');
          }}
          accessibilityLabel="Fiche en pastilles"
        />
      </View>
      <View style={[s.option, { flexDirection: 'column', alignItems: 'stretch' }]}>
        <Text style={s.label}>En-tête de fiche (essai)</Text>
        <View style={{ flexDirection: 'row', gap: 8 }} accessibilityRole="radiogroup">
          {([
            ['A', 'A · bandeaux'],
            ['B', 'B · photo'],
            ['C', 'C · étiquettes'],
            ['E', 'E · compteurs'],
          ] as [VarianteEnTete, string][]).map(([v, t]) => (
            <Pressable
              key={v}
              onPress={async () => {
                setEntete(v);
                await ecrire(CLE_ENTETE, v === 'B' ? null : v);
              }}
              accessibilityRole="radio"
              accessibilityState={{ selected: entete === v }}
              style={[s.choix, entete === v && s.choixActif]}>
              <Text style={[s.choixTexte, entete === v && { color: C.accent }]}>{t}</Text>
            </Pressable>
          ))}
        </View>
        <Text style={s.petit}>A : alertes en deux bandeaux. B : photo du produit en bandeau. C : chaque alerte en étiquette, qui ouvre son pilier. E : alertes et vigilances en onglets.</Text>
      </View>
      <Pressable
        onPress={async () => {
          await effacerHistorique();
          setMessage('Historique des scans effacé.');
        }}
        accessibilityRole="button"
        style={s.secondaire}>
        <Text style={s.secondaireTexte}>Effacer l'historique des scans</Text>
      </Pressable>
      <Text style={s.petit}>
        Les fiches viennent de l'Index général des marques : des faits publiés, datés et vérifiés mot pour mot dans leurs sources.
        Les noms et photos de produits viennent d'Open Food Facts et d'Open Beauty Facts, bases collaboratives sous licence ouverte.
      </Text>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  contenu: { padding: 20, gap: 16, paddingBottom: 48 },
  texte: { fontSize: 16, lineHeight: 23, color: C.texte },
  champBloc: { gap: 6 },
  label: { fontSize: 14, fontWeight: '700', color: C.texte },
  champ: { height: 50, backgroundColor: C.carte, borderRadius: 12, borderWidth: 1, borderColor: C.bordFort, paddingHorizontal: 14, fontSize: 16, color: C.texte },
  bouton: { backgroundColor: C.accent, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center' },
  boutonTexte: { color: '#fff', fontSize: 17, fontWeight: '700' },
  secondaire: { backgroundColor: C.carte, borderRadius: 14, minHeight: 52, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: C.bordFort },
  secondaireTexte: { color: C.texte, fontSize: 16, fontWeight: '600' },
  message: { fontSize: 15, color: C.accent, fontWeight: '600' },
  petit: { fontSize: 13, lineHeight: 19, color: C.gris },
  choix: { flex: 1, minHeight: 44, borderRadius: 10, borderWidth: 1, borderColor: C.bordFort, alignItems: 'center', justifyContent: 'center', backgroundColor: C.fond },
  choixActif: { borderColor: C.accent, backgroundColor: C.carte2 },
  choixTexte: { fontSize: 14, fontWeight: '700', color: C.texte },
  option: { flexDirection: 'row', gap: 12, alignItems: 'center', backgroundColor: C.carte, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: C.bordFort },
});
