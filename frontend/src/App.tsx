import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { useAppStore } from './stores/useAppStore'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import PatientSearch from './pages/PatientSearch'
import PatientDetails from './pages/PatientDetails'

function App() {
  const { initializeApp, appReady } = useAppStore()

  React.useEffect(() => {
    initializeApp()
  }, [initializeApp])

  if (!appReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing Clinical AI Assistant...</p>
        </div>
      </div>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<PatientSearch />} />
        <Route path="/patient/:tckn" element={<PatientDetails />} />
      </Routes>
    </Layout>
  )
}

export default App
