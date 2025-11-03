import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usePatientState, useAppActions, useSystemStatus } from '../stores/useAppStore'
import DiagnosisPanel from '../components/DiagnosisPanel'
import TreatmentPanel from '../components/TreatmentPanel'
import LabCharts from '../components/LabCharts'
import apiClient from '../services/api'

const PatientDetails: React.FC = () => {
  const { tckn } = useParams<{ tckn: string }>()
  const navigate = useNavigate()
  const { currentPatient } = usePatientState()
  const { setCurrentPatient, setError } = useAppActions()
  const { aiStatus } = useSystemStatus()

  const [activeTab, setActiveTab] = useState('diagnosis')
  const [loading, setLoading] = useState(false)

  // Load patient data
  useEffect(() => {
    if (!tckn) {
      navigate('/search')
      return
    }

    const loadPatient = async () => {
      setLoading(true)
      try {
        const patient = await apiClient.getPatient(tckn)
        setCurrentPatient(patient)
      } catch (error) {
        console.error('Failed to load patient:', error)
        setError('Failed to load patient data')
        navigate('/search')
      } finally {
        setLoading(false)
      }
    }

    if (!currentPatient || currentPatient.TCKN !== tckn) {
      loadPatient()
    }
  }, [tckn, currentPatient, navigate, setCurrentPatient, setError])

  const calculateAge = (birthDate?: string): string => {
    if (!birthDate) return 'Unknown'

    const birth = new Date(birthDate)
    const today = new Date()
    const age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      return `${age - 1} years`
    }

    return `${age} years`
  }

  if (loading || !currentPatient) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'diagnosis', label: 'AI Diagnosis', disabled: aiStatus !== 'ready' },
    { id: 'treatment', label: 'Treatment Plan', disabled: aiStatus !== 'ready' },
    { id: 'labs', label: 'Lab Results', disabled: false },
    { id: 'medications', label: 'Medications', disabled: true },
    { id: 'history', label: 'Visit History', disabled: true },
  ]

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Patient Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {currentPatient.ADI} {currentPatient.SOYADI}
              </h1>
              <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-600">TCKN:</span>
                  <span className="ml-1 text-gray-900">{currentPatient.TCKN}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Age:</span>
                  <span className="ml-1 text-gray-900">{calculateAge(currentPatient.DOGUM_TARIHI)}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Gender:</span>
                  <span className="ml-1 text-gray-900">
                    {currentPatient.CINSIYET === 'E' ? 'Male' : currentPatient.CINSIYET === 'K' ? 'Female' : 'Unknown'}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Birth Date:</span>
                  <span className="ml-1 text-gray-900">
                    {currentPatient.DOGUM_TARIHI ? new Date(currentPatient.DOGUM_TARIHI).toLocaleDateString() : 'Unknown'}
                  </span>
                </div>
              </div>
              {currentPatient.TELEFON && (
                <div className="mt-2 text-sm">
                  <span className="font-medium text-gray-600">Phone:</span>
                  <span className="ml-1 text-gray-900">{currentPatient.TELEFON}</span>
                </div>
              )}
              {currentPatient.ADRES && (
                <div className="mt-2 text-sm">
                  <span className="font-medium text-gray-600">Address:</span>
                  <span className="ml-1 text-gray-900">{currentPatient.ADRES}</span>
                </div>
              )}
            </div>
            <button
              onClick={() => navigate('/search')}
              className="btn btn-secondary"
            >
              Search Another Patient
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={tab.disabled}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : tab.disabled
                    ? 'border-transparent text-gray-400 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab.label}
              {tab.disabled && (
                <span className="ml-2 text-xs text-gray-500">(Coming Soon)</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {activeTab === 'diagnosis' && <DiagnosisPanel tckn={currentPatient.TCKN} />}
        {activeTab === 'treatment' && <TreatmentPanel tckn={currentPatient.TCKN} />}
        {activeTab === 'labs' && <LabCharts tckn={currentPatient.TCKN} />}
        {activeTab === 'medications' && (
          <div className="card">
            <div className="card-body text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Medication History</h3>
              <p className="text-gray-600">Medication history will be available here soon</p>
            </div>
          </div>
        )}
        {activeTab === 'history' && (
          <div className="card">
            <div className="card-body text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Visit History</h3>
              <p className="text-gray-600">Visit history will be available here soon</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PatientDetails
