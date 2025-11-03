import React, { useState } from 'react'
import { TreatmentRequest, TreatmentResponse } from '../services/api'
import apiClient from '../services/api'

interface TreatmentPanelProps {
  tckn: string
}

const TreatmentPanel: React.FC<TreatmentPanelProps> = ({ tckn }) => {
  const [diagnosis, setDiagnosis] = useState('')
  const [selectedModel, setSelectedModel] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TreatmentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateTreatment = async () => {
    if (!diagnosis.trim()) {
      setError('Please enter a diagnosis')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const request: TreatmentRequest = {
        tckn,
        diagnosis: diagnosis.trim(),
        model: selectedModel === 'auto' ? undefined : selectedModel
      }

      const response = await apiClient.generateTreatment(request)
      setResult(response)
    } catch (err) {
      console.error('Treatment generation failed:', err)
      setError('Failed to generate treatment plan. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">AI-Powered Treatment Recommendations</h2>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label htmlFor="diagnosis" className="block text-sm font-medium text-gray-700 mb-2">
              Confirmed Diagnosis
            </label>
            <textarea
              id="diagnosis"
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="Enter confirmed diagnosis..."
              rows={3}
              className="input"
              disabled={loading}
            />
            <p className="mt-1 text-sm text-gray-500">
              Enter the primary diagnosis for treatment planning
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-2">
                AI Model
              </label>
              <select
                id="model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="input"
                disabled={loading}
              >
                <option value="auto">Auto (Smart Routing)</option>
                <option value="claude">Claude (Recommended)</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gemini">Gemini</option>
                <option value="ollama">Ollama (Local)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleGenerateTreatment}
                disabled={loading || !diagnosis.trim()}
                className="btn btn-primary w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  'Generate Treatment'
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <svg className="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-red-800">{error}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Medication Recommendations */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Medication Recommendations</h3>
            </div>
            <div className="card-body">
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Medication</th>
                      <th>Dosage</th>
                      <th>Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.medications.map((med, index) => (
                      <tr key={index}>
                        <td className="font-medium">{med.name}</td>
                        <td>{med.dosage}</td>
                        <td>{med.duration}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {result.medications.length === 0 && (
                <p className="text-gray-500 text-center py-4">No medication recommendations available</p>
              )}
            </div>
          </div>

          {/* Clinical Guidelines */}
          {result.clinical_guidelines && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Clinical Guidelines</h3>
              </div>
              <div className="card-body">
                <div className="prose max-w-none">
                  <p className="text-gray-800 whitespace-pre-wrap">{result.clinical_guidelines}</p>
                </div>
              </div>
            </div>
          )}

          {/* Follow-up Plan */}
          {result.followup_plan && (
            <div className="card bg-blue-50 border-blue-200">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-blue-900">Follow-up Plan</h3>
              </div>
              <div className="card-body">
                <div className="prose max-w-none">
                  <p className="text-blue-800 whitespace-pre-wrap">{result.followup_plan}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default TreatmentPanel
