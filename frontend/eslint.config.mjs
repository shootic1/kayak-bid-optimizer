import next from 'eslint-config-next';
import tseslint from 'typescript-eslint';

/**
 * Flat ESLint config. `eslint-config-next` (v16) exports a ready-made flat
 * config array combining Next core-web-vitals + TypeScript rules. Project
 * overrides are layered on top; TypeScript-specific rules register the
 * typescript-eslint plugin so they resolve for `.ts`/`.tsx` files.
 */
const eslintConfig = [
  ...next,
  {
    ignores: ['.next/**', 'node_modules/**', 'next-env.d.ts'],
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    plugins: { '@typescript-eslint': tseslint.plugin },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],
    },
  },
  {
    rules: {
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
];

export default eslintConfig;
