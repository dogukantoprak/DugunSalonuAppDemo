import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("desktopBridge", {
  platform: process.platform,
  apiBaseUrl: process.env.VITE_API_BASE_URL || "http://localhost:8000",
});
