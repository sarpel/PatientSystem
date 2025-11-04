import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { usePatientState, useAppActions } from "../stores/useAppStore";
import { Patient } from "../services/api";

const PatientSearch: React.FC = () => {
  const navigate = useNavigate();
  const { patientSearchResults, searchingPatients } = usePatientState();
  const { searchPatients, clearPatientSearch, setCurrentPatient } =
    useAppActions();

  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Search when debounced query changes
  useEffect(() => {
    if (debouncedQuery) {
      searchPatients(debouncedQuery);
    } else {
      clearPatientSearch();
    }
  }, [debouncedQuery, searchPatients, clearPatientSearch]);

  const handlePatientSelect = (patient: Patient) => {
    setCurrentPatient(patient);
    navigate(`/patient/${patient.TCKN}`);
  };

  const calculateAge = (birthDate?: string): string => {
    if (!birthDate) return "Unknown";

    const birth = new Date(birthDate);
    const today = new Date();
    const age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birth.getDate())
    ) {
      return `${age - 1} years`;
    }

    return `${age} years`;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Patient Search</h1>
        <p className="mt-2 text-gray-600">
          Search for patients by name or TCKN (Turkish ID number)
        </p>
      </div>

      {/* Search Input */}
      <div className="card">
        <div className="card-body">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter patient name or TCKN..."
              className="input pl-10"
              autoFocus
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            {searchingPatients && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>

          {query && query.length < 2 && (
            <p className="mt-2 text-sm text-gray-500">
              Please enter at least 2 characters to search
            </p>
          )}
        </div>
      </div>

      {/* Search Results */}
      {query && query.length >= 2 && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">
              Search Results
              {patientSearchResults.length > 0 && (
                <span className="ml-2 text-sm font-normal text-gray-600">
                  ({patientSearchResults.length} patients found)
                </span>
              )}
            </h2>
          </div>
          <div className="card-body">
            {searchingPatients ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Searching patients...</p>
              </div>
            ) : patientSearchResults.length === 0 ? (
              <div className="text-center py-8">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"
                  />
                </svg>
                <p className="text-gray-600">No patients found for "{query}"</p>
                <p className="text-sm text-gray-500 mt-1">
                  Try searching with different terms or check the spelling
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {patientSearchResults.map((patient) => (
                  <div
                    key={patient.TCKN}
                    onClick={() => handlePatientSelect(patient)}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {patient.ADI} {patient.SOYADI}
                        </h3>
                        <div className="mt-1 flex flex-wrap gap-2 text-sm text-gray-600">
                          <span className="font-medium">TCKN:</span>
                          <span>{patient.TCKN}</span>
                          <span className="font-medium">Age:</span>
                          <span>{calculateAge(patient.DOGUM_TARIHI)}</span>
                          <span className="font-medium">Gender:</span>
                          <span>
                            {patient.CINSIYET === "E"
                              ? "Male"
                              : patient.CINSIYET === "K"
                                ? "Female"
                                : "Unknown"}
                          </span>
                        </div>
                        {patient.TELEFON && (
                          <div className="mt-1 text-sm text-gray-600">
                            <span className="font-medium">Phone:</span>{" "}
                            {patient.TELEFON}
                          </div>
                        )}
                      </div>
                      <svg
                        className="h-5 w-5 text-gray-400 mt-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-body">
          <h3 className="font-semibold text-blue-900 mb-2">Search Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Enter partial names (e.g., "Ahm" for "Ahmet")</li>
            <li>• Search by TCKN (Turkish ID number) with partial digits</li>
            <li>• Results are limited to 20 patients for performance</li>
            <li>
              • Click on any patient to view their complete medical record
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PatientSearch;
