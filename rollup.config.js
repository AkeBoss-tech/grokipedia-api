import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';

export default [
  // UMD build for browser (script tag usage)
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/browser/grokipedia-api.umd.js',
      format: 'umd',
      name: 'GrokipediaAPI',
      sourcemap: true,
      exports: 'named',
      globals: {
        axios: 'axios',
      },
    },
    plugins: [
      resolve({
        browser: true,
        preferBuiltins: false,
      }),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.browser.json',
        declaration: false,
        declarationDir: undefined,
        exclude: ['**/*.test.ts', '**/*.spec.ts'],
      }),
      terser({
        format: {
          comments: false,
        },
      }),
    ],
  },
  // ESM build for modern bundlers (webpack, vite, etc.)
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/browser/grokipedia-api.esm.js',
      format: 'es',
      sourcemap: true,
    },
    plugins: [
      resolve({
        browser: true,
        preferBuiltins: false,
      }),
      commonjs(),
      typescript({
        tsconfig: './tsconfig.browser.json',
        declaration: false,
        declarationDir: undefined,
        exclude: ['**/*.test.ts', '**/*.spec.ts'],
      }),
      terser({
        format: {
          comments: false,
        },
      }),
    ],
    external: ['axios'], // Keep axios as external for ESM builds (bundlers will handle it)
  },
];
