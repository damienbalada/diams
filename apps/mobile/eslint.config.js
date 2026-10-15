// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require('eslint/config');
const expoConfig = require('eslint-config-expo/flat');

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ['dist/*'],
  },
  {
    // Appli native : les apostrophes du texte français s'affichent telles quelles (pas de HTML).
    rules: { 'react/no-unescaped-entities': 'off' },
  },
]);
