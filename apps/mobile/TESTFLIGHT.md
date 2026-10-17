# Distribuer l'appli sur iPhone avec TestFlight

TestFlight est l'appli d'Apple qui installe les versions d'essai. La construction se fait dans le cloud
d'Expo (EAS) : aucun Mac n'est nécessaire.

## Ce qui est déjà prêt dans le code

- `app.json` : identifiant iOS `fr.indexdesmarques.app`, version `1.0.0`, icône 1024 × 1024 sans
  transparence, écran de lancement, textes d'autorisation en français (appareil photo pour le scanner et
  les photos d'étiquettes, photothèque pour choisir une photo), chiffrement déclaré « non soumis à
  déclaration » (`ITSAppUsesNonExemptEncryption = false` : l'appli n'utilise que le HTTPS du système).
- `eas.json` : profil `production` (numéro de construction tenu par EAS et augmenté à chaque
  construction, canal de mises à jour `production`) et soumission iOS en français.
- Aucun identifiant secret dans le dépôt : EAS demande les accès Apple au moment voulu et garde les
  certificats sur ses serveurs.

## Étapes à faire par l'éditeur

1. **Compte Apple Developer** (99 $ par an) : https://developer.apple.com/programs/enroll/ avec son
   identifiant Apple. L'activation peut prendre de quelques heures à deux jours.
2. **Créer l'appli dans App Store Connect** : https://appstoreconnect.apple.com → Apps → « + » →
   Nouvelle app. Plateforme iOS, nom « Index des marques » (ou un nom libre s'il est pris), langue
   principale Français, identifiant de lot `fr.indexdesmarques.app` (à créer d'abord dans
   « Certificates, Identifiers & Profiles » s'il n'apparaît pas), SKU libre, par exemple
   `index-des-marques`. *Variante : `eas build` peut créer l'identifiant et `eas submit` l'appli tout seuls.*
3. **Connexion à Expo** : `npx eas-cli@latest login` (déjà fait sur cet ordinateur : compte
   propriétaire de l'organisation `index-awareness`). Vérifier avec `npx eas-cli@latest whoami`.
4. **Construction** (environ 15 à 30 minutes) :

   ```bash
   cd apps/mobile
   npx eas-cli@latest build --platform ios --profile production
   ```

   EAS demande de se connecter au compte Apple (identifiant, mot de passe, code à deux facteurs, saisis
   par l'éditeur dans son terminal) puis propose de créer le certificat de distribution et le profil :
   répondre oui.
5. **Envoi à App Store Connect** :

   ```bash
   npx eas-cli@latest submit --platform ios --profile production --latest
   ```

   La première fois, EAS propose de créer une clé d'API App Store Connect : accepter, il la garde.
   Apple traite ensuite la construction (10 à 30 minutes) ; elle apparaît dans l'onglet TestFlight.
6. **Testeurs internes** : App Store Connect → l'appli → TestFlight → « Testeurs internes » → « + »
   pour créer un groupe, puis ajouter des membres de l'équipe (Utilisateurs et accès → inviter la
   personne avec un rôle, par exemple « Marketing » ou « Développeur »). Chacun reçoit un courriel,
   installe TestFlight sur son iPhone et accepte l'invitation. Jusqu'à 100 testeurs internes, sans
   relecture par Apple.

   *Testeurs externes* (personnes hors de l'équipe, jusqu'à 10 000, lien public possible) : il faut une
   relecture rapide de la version par Apple, une description de l'essai, une adresse de contact et une
   **politique de confidentialité en ligne** (le site n'en a pas encore).

## Versions suivantes

- Changement de code JavaScript seulement : `npx eas-cli@latest update --channel production --message "…"`
  (les testeurs reçoivent la mise à jour au prochain lancement, sans nouvelle construction).
- Nouveau module natif, nouvelle autorisation ou changement d'`app.json` : refaire les étapes 4 et 5.
  Augmenter `version` dans `app.json` pour une version visible différente (1.0.1, 1.1.0…).

## Ce qui peut bloquer l'essai

- **Le site est privé** : sans identifiant et mot de passe saisis dans les Réglages, chaque fiche affiche
  « Le site est encore privé ». Il faut donner ces accès aux testeurs par un canal privé (jamais dans
  la description publique de TestFlight).
- **Relecture Apple pour les testeurs externes** : l'examinateur doit pouvoir entrer ; donner
  l'identifiant et le mot de passe dans « Informations de connexion » de la relecture TestFlight.
- **Politique de confidentialité** : obligatoire pour les testeurs externes et pour l'App Store.
- Le profil `development` d'`eas.json` suppose `expo-dev-client`, qui n'est pas installé : ne pas
  l'utiliser tel quel.

## Texte d'aide pour les testeurs

> **Bienvenue dans l'essai de l'Index des marques.**
>
> L'appli lit le code-barres d'un produit et affiche la fiche de sa marque : faits publiés, datés et
> vérifiés dans leurs sources.
>
> **Avant de commencer** : le site de l'Index est encore privé. Ouvrez l'appli, touchez **Réglages**,
> puis saisissez l'**identifiant** et le **mot de passe** que l'équipe vous a envoyés, et touchez
> **Enregistrer**. Laissez l'adresse du site telle quelle. Ces accès restent dans le coffre sécurisé de
> votre téléphone et ne sont envoyés qu'au site de l'Index.
>
> **À essayer** : scanner des produits du quotidien (alimentation, beauté, entretien, vêtements),
> chercher une marque par son nom, ouvrir les piliers d'une fiche. Si un produit est inconnu, l'appli
> propose d'envoyer des photos : elles ne sont publiées qu'après relecture par l'équipe.
>
> **Pour signaler un problème** : faites une capture d'écran dans l'appli, TestFlight propose alors
> d'envoyer un commentaire. Dites ce que vous faisiez et, si possible, le code-barres du produit.
