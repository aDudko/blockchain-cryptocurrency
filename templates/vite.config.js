import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    root: '.',
    plugins: [vue()],
    server: {
        proxy: {
            '/api': 'http://localhost:5000'
        }
    }
})
