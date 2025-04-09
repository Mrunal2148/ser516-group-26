// vite.config.js (or vite.config.mjs if you're using ESM)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [
        react({
            // ✅ THIS is critical — enables JSX parsing in `.js` files
            include: [/\.js$/, /\.jsx$/],
        }),
    ],
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.js',
    },
});
