import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  usePatientState,
  useAppActions,
  useSystemStatus,
} from "../stores/useAppStore";
import DiagnosisPanel from "../components/DiagnosisPanel";
import TreatmentPanel from "../components/TreatmentPanel";
import LabCharts from "../components/LabCharts";
import apiClient from "../services/api";
import { logger } from "../utils/logger";

const formatGender = (
  gender: string | number | null | undefined,
): string => {
  if (gender === null || gender === undefined) {
    return "Unknown";
  }

  if (typeof gender === "string") {
    const normalized = gender.trim().toUpperCase();
    if (normalized === "E") return "Male";
    if (normalized === "K") return "Female";
    if (normalized === "U") return "Unknown";
    return normalized || "Unknown";
  }

  switch (gender) {
    case 1:
      return "Male";
    case 2:
      return "Female";
    default:
      return String(gender);
  }
};

const calculateAge = (birthDate?: string | null): string | null => {
  if (!birthDate) return null;

  const birth = new Date(birthDate);
  if (Number.isNaN(birth.getTime())) {
    return null;
  }

  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age -= 1;
  }

  return `${age} years`;
};

const PatientDetails: React.FC = () => {
  const { tckn } = useParams<{ tckn: string }>();
  const navigate = useNavigate();
  const { currentPatient } = usePatientState();
  const { setCurrentPatient, setError } = useAppActions();
  const { aiStatus } = useSystemStatus();

  const [activeTab, setActiveTab] = useState("diagnosis");
  const [loading, setLoading] = useState(false);

  const currentSummaryTckn = currentPatient?.demographics?.tc_number
    ? String(currentPatient.demographics.tc_number)
    : null;

  useEffect(() => {
    if (!tckn) {
      navigate("/search");
      return;
    }

    const loadPatient = async () => {
      setLoading(true);
      try {
        const patient = await apiClient.getPatient(tckn);
        setCurrentPatient(patient);
      } catch (error) {
        logger.error("Failed to load patient:", error);
        setError("Failed to load patient data");
        navigate("/search");
      } finally {
        setLoading(false);
      }
    };

    if (!currentSummaryTckn || currentSummaryTckn !== tckn) {
      loadPatient();
    }
  }, [tckn, currentSummaryTckn, navigate, setCurrentPatient, setError]);

  if (loading || !currentPatient) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const demographics = currentPatient.demographics;
  const summaryStats = currentPatient.summary_stats;
  const latestVitals = currentPatient.latest_vitals;

  const patientTckn = demographics.tc_number
    ? String(demographics.tc_number)
    : null;
  const ageLabel =
    demographics.age !== null && demographics.age !== undefined
      ? `${demographics.age} years`
      : calculateAge(demographics.birth_date) ?? "Unknown";
  const birthDateLabel = demographics.birth_date
    ? new Date(demographics.birth_date).toLocaleDateString()
    : "Unknown";
  const genderLabel = formatGender(demographics.gender);

  const tabs = [
    {
      id: "diagnosis",
      label: "AI Diagnosis",
      disabled: aiStatus !== "ready" || !patientTckn,
    },
    {
      id: "treatment",
      label: "Treatment Plan",
      disabled: aiStatus !== "ready" || !patientTckn,
    },
    { id: "labs", label: "Lab Results", disabled: !patientTckn },
    { id: "medications", label: "Medications", disabled: true },
    { id: "history", label: "Visit History", disabled: true },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Patient Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div className="space-y-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {demographics.full_name}
                </h1>
                <p className="text-sm text-gray-500">
                  Patient ID: {demographics.patient_id}
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-600">TCKN:</span>
                  <span className="ml-1 text-gray-900">
                    {patientTckn ?? "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Age:</span>
                  <span className="ml-1 text-gray-900">{ageLabel}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Gender:</span>
                  <span className="ml-1 text-gray-900">{genderLabel}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Birth Date:</span>
                  <span className="ml-1 text-gray-900">{birthDateLabel}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Blood Type:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.blood_type ?? "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Smoking Status:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.smoking_status ?? "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Weight:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.weight_kg
                      ? `${demographics.weight_kg.toFixed(1)} kg`
                      : "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Height:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.height_cm
                      ? `${demographics.height_cm} cm`
                      : "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">BMI:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.bmi
                      ? `${demographics.bmi} (${demographics.bmi_category ?? "N/A"})`
                      : "Unknown"}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Alcohol Use:</span>
                  <span className="ml-1 text-gray-900">
                    {demographics.alcohol_use ?? "Unknown"}
                  </span>
                </div>
              </div>
              {demographics.is_deceased && (
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-red-50 text-red-700 text-xs font-semibold">
                  ⚠️ Marked as deceased in registry
                </div>
              )}
            </div>
            <div>
              <button
                onClick={() => navigate("/search")}
                className="btn btn-secondary"
              >
                Search Another Patient
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Snapshot cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">
              Care Summary (Last {summaryStats.period_months} months)
            </h3>
          </div>
          <div className="card-body grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold text-blue-600">
                {summaryStats.recent_visit_count}
              </p>
              <p className="text-sm text-gray-600">Visits</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-600">
                {summaryStats.active_diagnosis_count}
              </p>
              <p className="text-sm text-gray-600">Active Diagnoses</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-600">
                {summaryStats.active_prescription_count}
              </p>
              <p className="text-sm text-gray-600">Active Prescriptions</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">
              Latest Vitals
            </h3>
          </div>
          <div className="card-body grid grid-cols-2 gap-4 text-sm">
            {latestVitals ? (
              <>
                <div>
                  <p className="font-medium text-gray-600">Blood Pressure</p>
                  <p className="text-gray-900">
                    {latestVitals.blood_pressure_str ?? "Unknown"}
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-600">Pulse</p>
                  <p className="text-gray-900">
                    {latestVitals.pulse ?? "Unknown"}
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-600">Temperature</p>
                  <p className="text-gray-900">
                    {latestVitals.temperature_celsius
                      ? `${latestVitals.temperature_celsius} °C`
                      : "Unknown"}
                  </p>
                </div>
                <div>
                  <p className="font-medium text-gray-600">BMI</p>
                  <p className="text-gray-900">
                    {latestVitals.bmi ?? "Unknown"}
                  </p>
                </div>
              </>
            ) : (
              <p className="text-gray-600">
                No recent vital signs available.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={tab.disabled}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : tab.disabled
                    ? "border-transparent text-gray-400 cursor-not-allowed"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
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
        {activeTab === "diagnosis" && patientTckn && (
          <DiagnosisPanel tckn={patientTckn} />
        )}
        {activeTab === "treatment" && patientTckn && (
          <TreatmentPanel tckn={patientTckn} />
        )}
        {activeTab === "labs" && patientTckn && <LabCharts tckn={patientTckn} />}
        {activeTab === "medications" && (
          <div className="card">
            <div className="card-body text-gray-600">
              Medication history integration coming soon.
            </div>
          </div>
        )}
        {activeTab === "history" && (
          <div className="card">
            <div className="card-body text-gray-600">
              Visit history insights coming soon.
            </div>
          </div>
        )}
        {!patientTckn && (
          <div className="card">
            <div className="card-body text-gray-600">
              Unable to load patient-specific operations because no TC number was
              provided.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientDetails;
