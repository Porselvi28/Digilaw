import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { DemoProvider } from './context/DemoContext'
import { AppShell, ProtectedRoute } from './components/layout'
import { ForgotPassword, Home, Login, Register } from './pages/MarketingPages'
import {
  ActionPlanPage, AnalysisPage, AskLegal, CaseWorkspace, Cases, Dashboard, DocumentsPage,
  EvidencePage, NotificationsPage, NotFound, ProfilePage, SettingsPage, SimilarCasesPage,
} from './pages/AppPages'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <DemoProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/cases" element={<Cases />} />
                <Route path="/cases/:caseId" element={<CaseWorkspace />} />
                <Route path="/cases/:caseId/documents" element={<DocumentsPage />} />
                <Route path="/cases/:caseId/evidence" element={<EvidencePage />} />
                <Route path="/cases/:caseId/analysis" element={<AnalysisPage />} />
                <Route path="/cases/:caseId/similar-cases" element={<SimilarCasesPage />} />
                <Route path="/cases/:caseId/action-plan" element={<ActionPlanPage />} />
                <Route path="/ask-legal" element={<AskLegal />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
            </Route>
            <Route path="/app" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </DemoProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
