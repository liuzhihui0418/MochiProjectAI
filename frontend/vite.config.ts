import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // ⚠️ 核心修复：把基础路径改为相对路径 './'，而不是默认的 '/'
  base: './',
})