import { Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/app-layout"
import { DashboardPage } from "@/pages/dashboard"
import { HomePage } from "@/pages/home"
import { NotebookPage } from "@/pages/notebook"
import { ProfileUpdatePage } from "@/pages/profile-update"

export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="notebooks/:notebookId" element={<NotebookPage />} />
        <Route path="profile-update" element={<ProfileUpdatePage />} />
      </Route>
    </Routes>
  )
}

export default App
