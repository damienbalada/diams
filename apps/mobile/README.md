# Appli mobile de l'Index général des marques

Appli iPhone et Android (Expo, React Native) : on scanne le code-barres d'un produit et la fiche de
sa marque s'affiche, avec les mêmes faits que le site (alertes, piliers, sources vérifiées mot pour mot).

## Comment elle marche

1. L'appareil photo lit le code-barres (EAN-13, EAN-8, UPC). Aucune photo n'est gardée.
2. Le numéro est envoyé à l'API du site (`/api/code/<numéro>`).
3. Le site lit le produit dans Open Food Facts ou Open Beauty Facts (bases collaboratives), rapproche
   la marque inscrite sur le produit d'une marque de l'Index, et renvoie la fiche.
4. L'appli l'affiche ; si la marque n'est pas encore dans l'Index, elle le dit et propose la recherche.

Écrans : accueil (scanner, recherche, saisie du code, derniers scans), scanner, fiche du produit
scanné, fiche d'une marque, recherche, réglages.

## Réglages

Tant que le site est privé, l'appli a besoin de son mot de passe (écran Réglages). Il est gardé dans
le coffre sécurisé du téléphone et n'est envoyé qu'au site, jamais à un autre serveur (pas même pour
les logos venant de Wikimedia). Une fois le site public, il ne sert plus.

## L'essayer sur son téléphone

Le plus simple, sans compte développeur :

```bash
cd apps/mobile
npm install
npx expo start
```

Puis scanner le QR code affiché avec l'appli **Expo Go** (App Store ou Google Play). L'appareil photo et
le coffre sécurisé fonctionnent dans Expo Go.

Aperçu dans un navigateur (sans scanner) : `npx expo start --web`.

## Publier dans les magasins

Construction dans le cloud avec EAS (pas besoin de Mac pour l'iPhone) :

```bash
npx eas-cli@latest login
npx eas-cli@latest build --profile preview --platform android   # APK à installer directement
npx eas-cli@latest build --profile production --platform all     # versions pour les magasins
npx eas-cli@latest submit --platform all
```

Il faut un compte Apple Developer (99 $ par an) et un compte Google Play Console (25 $, une fois),
une politique de confidentialité (accès à l'appareil photo) et la relecture des deux magasins.

## Contrôles

```bash
npm run typecheck   # types
npx expo lint       # règles de code
npx expo-doctor     # configuration Expo
```
