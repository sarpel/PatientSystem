import React, { useState } from "react";
import { DiagnosisRequest, DiagnosisResponse } from "../services/api";
import apiClient from "../services/api";
import { logger } from "../utils/logger";

interface DiagnosisPanelProps {
  tckn: string;
}

const DiagnosisPanel: React.FC<DiagnosisPanelProps> = ({ tckn }) => {
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [selectedModel, setSelectedModel] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateDiagnosis = async () => {
    if (!chiefComplaint.trim()) {
      setError("Please enter a chief complaint");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const request: DiagnosisRequest = {
        tckn,
        chief_complaint: chiefComplaint.trim(),
        model: selectedModel === "auto" ? undefined : selectedModel,
      };

      const response = await apiClient.generateDiagnosis(request);
      setResult(response);
    } catch (err) {
      logger.error("Diagnosis generation failed:", err);
      setError("Failed to generate diagnosis. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "severity-critical";
      case "major":
        return "severity-major";
      case "moderate":
        return "severity-moderate";
      case "minor":
        return "severity-minor";
      default:
        return "severity-moderate";
    }
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 0.7) return "text-green-600";
    if (probability >= 0.5) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">
            AI-Powered Differential Diagnosis
          </h2>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label
              htmlFor="complaint"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Chief Complaint & Symptoms
            </label>
            <textarea
              id="complaint"
              value={chiefComplaint}
              onChange={(e) => setChiefComplaint(e.target.value)}
              placeholder="Enter patient's chief complaint and symptoms..."
              rows={4}
              className="input"
              disabled={loading}
            />
            <p className="mt-1 text-sm text-gray-500">
              Be specific about symptoms, duration, and severity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="model"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
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
                onClick={handleGenerateDiagnosis}
                disabled={loading || !chiefComplaint.trim()}
                className="btn btn-primary w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  "Generate Diagnosis"
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <svg
                  className="h-5 w-5 text-red-400 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
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
          {/* Differential Diagnosis */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                Differential Diagnosis
              </h3>
            </div>
            <div className="card-body">
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Diagnosis</th>
                      <th>ICD-10 Code</th>
                      <th>Probability</th>
                      <th>Urgency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.differential_diagnosis.map((dx, index) => (
                      <tr key={index}>
                        <td className="font-medium">{dx.diagnosis}</td>
                        <td className="font-mono text-sm">{dx.icd10}</td>
                        <td
                          className={`font-semibold ${getProbabilityColor(dx.probability)}`}
                        >
                          {(dx.probability * 100).toFixed(1)}%
                        </td>
                        <td>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(dx.urgency)}`}
                          >
                            {dx.urgency.toUpperCase()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Red Flags */}
          {result.red_flags.length > 0 && (
            <div className="card border-l-4 border-red-500 bg-red-50">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-red-900">
                  ⚠️ Red Flags
                </h3>
              </div>
              <div className="card-body">
                <ul className="space-y-2">
                  {result.red_flags.map((flag, index) => (
                    <li key={index} className="flex items-start">
                      <svg
                        className="h-5 w-5 text-red-500 mr-2 mt-0.5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                      </svg>
                      <span className="text-red-800">{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Recommended Tests */}
          {result.recommended_tests.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">
                  Recommended Tests
                </h3>
              </div>
              <div className="card-body">
                <ul className="space-y-2">
                  {result.recommended_tests.map((test, index) => (
                    <li key={index} className="flex items-start">
                      <svg
                        className="h-5 w-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                        />
                      </svg>
                      <span className="text-gray-800">{test}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DiagnosisPanel;
