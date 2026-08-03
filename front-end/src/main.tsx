import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import "./index.css"
import App from "./App.tsx"
import { AppProviders } from "@/providers"
import { Toaster } from "@/components/ui/sonner"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppProviders>
      <App />
      <Toaster richColors position="bottom-right" />
    </AppProviders>
  </StrictMode>
)
