import { Link } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { Logo } from '@/components/logo';
import { ErreurSite, rechercher, type Resultat } from '@/lib/api';
import { C } from '@/lib/couleurs';

/** Recherche d'une marque ou d'un groupe par son nom (aussi par le nom du groupe : « Unilever »). */
export default function Recherche() {
  const [q, setQ] = useState('');
  const [res, setRes] = useState<Resultat[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const derniere = useRef(0);
  useEffect(() => {
    const t = setTimeout(async () => {
      if (q.trim().length < 2) {
        setRes([]);
        setMessage(null);
        return;
      }
      const n = ++derniere.current;
      try {
        const r = await rechercher(q.trim());
        if (n !== derniere.current) return;
        setRes(r.resultats);
        setMessage(r.resultats.length ? null : `Aucune marque ne correspond à « ${q.trim()} ». L'Index ne couvre pas encore tout : ce n'est pas un jugement sur elle.`);
      } catch (e) {
        if (n === derniere.current) setMessage(e instanceof ErreurSite ? e.message : String(e));
      }
    }, 250);
    return () => clearTimeout(t);
  }, [q]);
  return (
    <View style={s.ecran}>
      <TextInput
        value={q}
        onChangeText={setQ}
        placeholder="Zara, Danone, Président…"
        placeholderTextColor={C.grisClair}
        accessibilityLabel="Rechercher une marque ou un groupe"
        autoFocus
        autoCorrect={false}
        style={s.champ}
        returnKeyType="search"
      />
      {message && <Text style={s.message} accessibilityLiveRegion="polite">{message}</Text>}
      <FlatList
        data={res}
        keyExtractor={(x) => x.slug}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{ paddingBottom: 40 }}
        renderItem={({ item }) => (
          <Link href={`/fiche/${item.slug}`} asChild>
            <Pressable style={s.ligne} accessibilityRole="button" accessibilityLabel={`${item.nom}${item.groupe ? `, groupe ${item.groupe}` : ''}`}>
              <Logo src={item.logo} taille={44} groupe={!item.marque} />
              <View style={{ flex: 1 }}>
                <Text style={s.nom}>{item.nom}</Text>
                {item.groupe && <Text style={s.groupe}>{item.groupe}</Text>}
              </View>
              <Text style={s.chevron} accessible={false}>›</Text>
            </Pressable>
          </Link>
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  ecran: { flex: 1, padding: 16, gap: 12, backgroundColor: C.fond },
  champ: { height: 52, backgroundColor: C.carte, borderRadius: 14, borderWidth: 1, borderColor: C.bordFort, paddingHorizontal: 16, fontSize: 17, color: C.texte },
  message: { fontSize: 15, lineHeight: 21, color: C.gris },
  ligne: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 10, minHeight: 64, borderBottomWidth: 1, borderBottomColor: C.bord },
  nom: { fontSize: 17, fontWeight: '700', color: C.texte },
  groupe: { fontSize: 14, color: C.gris },
  chevron: { fontSize: 26, color: C.grisClair },
});
