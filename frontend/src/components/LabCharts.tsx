import React, { useState, useEffect } from "react";
import { LabTest } from "../services/api";
import apiClient from "../services/api";
import { logger } from "../utils/logger";

interface LabChartsProps {
  tckn: string;
}

const LabCharts: React.FC<LabChartsProps> = ({ tckn }) => {
  const [selectedTest, setSelectedTest] = useState("Hemoglobin");
  const [timeRange, setTimeRange] = useState("6");
  const [labData, setLabData] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const commonTests = [
    "Hemoglobin",
    "White Blood Cell",
    "Platelet Count",
    "Glucose",
    "Creatinine",
    "ALT (SGPT)",
    "AST (SGOT)",
    "Total Cholesterol",
    "LDL Cholesterol",
    "HDL Cholesterol",
    "Triglycerides",
  ];

  useEffect(() => {
    loadLabData();
  }, [tckn, selectedTest, timeRange]);

  const loadLabData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.getLabTests(tckn, selectedTest);
      setLabData(data);
    } catch (err) {
      logger.error("Failed to load lab data:", err);
      setError("Failed to load laboratory data");
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value: string, unit: string): string => {
    if (!value) return "N/A";
    return `${value} ${unit}`.trim();
  };

  const isWithinNormalRange = (
    value: string,
    min: string,
    max: string,
  ): boolean => {
    try {
      const numValue = parseFloat(value.replace(",", "."));
      const numMin = parseFloat(min.replace(",", "."));
      const numMax = parseFloat(max.replace(",", "."));

      return numValue >= numMin && numValue <= numMax;
    } catch {
      return true;
    }
  };

  const getValueColor = (value: string, min: string, max: string): string => {
    if (!value) return "text-gray-500";

    if (isWithinNormalRange(value, min, max)) {
      return "text-green-600";
    } else {
      return "text-red-600";
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">
            Laboratory Results
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label
                htmlFor="test"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Test Type
              </label>
              <select
                id="test"
                value={selectedTest}
                onChange={(e) => setSelectedTest(e.target.value)}
                className="input"
                disabled={loading}
              >
                {commonTests.map((test) => (
                  <option key={test} value={test}>
                    {test}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="timeRange"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Time Range
              </label>
              <select
                id="timeRange"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="input"
                disabled={loading}
              >
                <option value="1">Last Month</option>
                <option value="3">Last 3 Months</option>
                <option value="6">Last 6 Months</option>
                <option value="12">Last Year</option>
                <option value="all">All Time</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={loadLabData}
                disabled={loading}
                className="btn btn-secondary w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </>
                ) : (
                  "Refresh"
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="card border-l-4 border-red-500 bg-red-50">
          <div className="card-body">
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
        </div>
      )}

      {/* Lab Results Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            {selectedTest} Results
            {labData.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-600">
                ({labData.length} result{labData.length !== 1 ? "s" : ""})
              </span>
            )}
          </h3>
        </div>
        <div className="card-body">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading laboratory results...</p>
            </div>
          ) : labData.length === 0 ? (
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-600">
                No laboratory results found for {selectedTest}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Try selecting a different test or time range
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Result</th>
                    <th>Reference Range</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {labData
                    .sort(
                      (a, b) =>
                        new Date(b.TEST_TARIHI).getTime() -
                        new Date(a.TEST_TARIHI).getTime(),
                    )
                    .map((test, index) => (
                      <tr key={index}>
                        <td className="font-medium">
                          {new Date(test.TEST_TARIHI).toLocaleDateString()}
                        </td>
                        <td
                          className={`font-semibold ${getValueColor(test.SONUC, test.NORMAL_MIN, test.NORMAL_MAX)}`}
                        >
                          {formatValue(test.SONUC, test.BIRIM)}
                        </td>
                        <td className="font-mono text-sm">
                          {test.NORMAL_MIN} - {test.NORMAL_MAX} {test.BIRIM}
                        </td>
                        <td>
                          {isWithinNormalRange(
                            test.SONUC,
                            test.NORMAL_MIN,
                            test.NORMAL_MAX,
                          ) ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Normal
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              Abnormal
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Chart Placeholder */}
      {labData.length > 1 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">
              Trend Analysis
            </h3>
          </div>
          <div className="card-body">
            <div className="text-center py-12">
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Chart Visualization
              </h3>
              <p className="text-gray-600">
                Interactive trend charts will be available here
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Showing {labData.length} data points over time
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LabCharts;
