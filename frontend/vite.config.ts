import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Cấu hình Vite cho môi trường phát triển và đóng gói sản phẩm
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path: string): string => path.replace(/^\/api/, ""),
      },
    },
  },
});
