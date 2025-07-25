import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import autoprefixer from 'autoprefixer';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	css: {
		postcss: {
			plugins: [autoprefixer]
		}
	}
});
