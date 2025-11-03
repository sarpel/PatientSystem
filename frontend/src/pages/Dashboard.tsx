import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useSystemStatus } from '../stores/useAppStore'

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { databaseStatus, aiStatus } = useSystemStatus()

  const statusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'ready':
        return 'text-green-600 bg-green-100'
      case 'disconnected':
      case 'unavailable':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Clinical AI Assistant Dashboard
        </h1>
        <p className="mt-2 text-gray-600">
          AI-powered clinical decision support system for family medicine
        </p>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-700">Database Connection</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor(databaseStatus)}`}>
                {databaseStatus}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-700">AI Services</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor(aiStatus)}`}>
                {aiStatus}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </div>
          <div className="card-body space-y-3">
            <button
              onClick={() => navigate('/search')}
              className="w-full btn btn-primary"
            >
              Search Patient
            </button>
            <button
              className="w-full btn btn-secondary"
              disabled={aiStatus !== 'ready'}
            >
              AI Analysis ({aiStatus === 'ready' ? 'Available' : 'Unavailable'})
            </button>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Patient Records</h3>
            <p className="text-sm text-gray-600">
              Search and view patient medical history, lab results, and treatment records
            </p>
          </div>
        </div>

        <div className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI Diagnosis</h3>
            <p className="text-sm text-gray-600">
              Generate differential diagnoses using advanced AI models with probability scoring
            </p>
          </div>
        </div>

        <div className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Treatment Plans</h3>
            <p className="text-sm text-gray-600">
              Evidence-based treatment recommendations with clinical guidelines
            </p>
          </div>
        </div>

        <div className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Drug Interactions</h3>
            <p className="text-sm text-gray-600">
              Check for drug interactions and safety warnings before prescribing
            </p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">System Information</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">7</div>
              <div className="text-sm text-gray-600">Years of Patient Data</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">6,000+</div>
              <div className="text-sm text-gray-600">Patients in Database</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">641</div>
              <div className="text-sm text-gray-600">Database Tables</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
