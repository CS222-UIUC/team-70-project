import globals from "globals";
import pluginJs from "@eslint/js";
import pluginReact from "eslint-plugin-react";
import jest from "eslint-plugin-jest";


/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    settings: {
      react: {
        version: 'detect', // Automatically detect React version
      },
    },
  },
  {
    plugins: { jest }
  },
  {
    files: ["**/*.{js,mjs,cjs,jsx}"], // Apply to JavaScript and JSX files
  },
  {
    languageOptions: {
      globals: {
        ...globals.browser, // Browser globals (window, document, etc.)
        ...globals.node,    // Node.js globals (module, process, etc.)
        ...globals.jest,    // Jest globals (test, expect, etc.)
      },
    },
  },
  pluginJs.configs.recommended,    // Recommended ESLint config for JS
  pluginReact.configs.flat.recommended, // Recommended ESLint config for React
];