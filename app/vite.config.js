import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite config for Migration Atlas frontend.
// In dev, /api/* is proxied to the FastAPI backend on :8000.
// In prod, set VITE_API_URL to the deployed backend URL.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
