import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const currentDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      'lodash/isFunction': resolve(currentDir, 'src/shims/isFunction.ts'),
      'lodash/sortBy': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/throttle': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/upperFirst': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/some': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/range': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/sumBy': resolve(currentDir, 'src/shims/lodash.ts'),
      'lodash/uniqBy': resolve(currentDir, 'src/shims/lodash.ts'),
    },
  },
});
