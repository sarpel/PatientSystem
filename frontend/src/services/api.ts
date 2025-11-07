import axios, { AxiosInstance, AxiosResponse, AxiosError } from "axios";
import axiosRetry from "axios-retry";
import { logger } from "../utils/logger";

// Types
export interface PatientSearchResult {
  tckn: string | null;
  name: string;
  age: number | null;
  gender: string | number | null;
  last_visit: string | null;
}

export interface PatientDemographics {
  patient_id: number;
  full_name: string;
  birth_date: string | null;
  age: number | null;
  gender: string | number | null;
  tc_number: string | number | null;
  blood_type: string | null;
  is_deceased: boolean;
  weight_kg?: number | null;
  height_cm?: number | null;
  bmi?: number | null;
  bmi_category?: string | null;
  smoking_status?: string | number | null;
  alcohol_use?: string | number | null;
}

export interface PatientVisitSummary {
  visit_id: number;
  admission_id: number;
  visit_type: number | null;
  primary_diagnosis: number | null;
  complaint: string | null;
  blood_pressure: string | null;
  pulse: number | null;
  temperature: number | null;
  weight_kg: number | null;
  bmi: number | null;
}

export interface PatientDiagnosisSummary {
  diagnosis_id: number;
  visit_id: number;
  icd10_code: number | string | null;
  diagnosis_type: number | null;
  description: string | null;
  severity: number | null;
  diagnosis_date: string | null;
  is_active: boolean;
}

export interface PatientPrescriptionSummary {
  prescription_id: number;
  visit_id: number | null;
  prescription_type: number | null;
  prescription_date: string;
  prescription_number: string | null;
  physician_id: number | null;
  diagnosis_code: number | null;
  notes: string | null;
  esy_number: string | null;
}

export interface PatientVitalsSummary {
  blood_pressure_systolic: number | null;
  blood_pressure_diastolic: number | null;
  blood_pressure_str: string | null;
  pulse: number | null;
  temperature_celsius: number | null;
  weight_kg: number | null;
  height_cm: number | null;
  bmi: number | null;
  waist_circumference_cm: number | null;
  hip_circumference_cm: number | null;
  waist_hip_ratio: number | null;
  glasgow_coma_scale: number | null;
}

export interface PatientSummaryStats {
  recent_visit_count: number;
  active_diagnosis_count: number;
  active_prescription_count: number;
  period_months: number;
}

export interface PatientSummary {
  demographics: PatientDemographics;
  recent_visits: PatientVisitSummary[];
  active_diagnoses: PatientDiagnosisSummary[];
  active_prescriptions: PatientPrescriptionSummary[];
  allergies: string[];
  latest_vitals: PatientVitalsSummary | null;
  summary_stats: PatientSummaryStats;
}

export interface DiagnosisRequest {
  tckn: string;
  chief_complaint: string;
  model?: string;
}

export interface DiagnosisResponse {
  differential_diagnosis: Array<{
    diagnosis: string;
    icd10: string;
    probability: number;
    urgency: "critical" | "major" | "moderate" | "minor";
  }>;
  red_flags: string[];
  recommended_tests: string[];
}

export interface TreatmentRequest {
  tckn: string;
  diagnosis: string;
  model?: string;
}

export interface TreatmentResponse {
  medications: Array<{
    name: string;
    dosage: string;
    duration: string;
  }>;
  clinical_guidelines: string;
  followup_plan: string;
}

export interface DrugCheckRequest {
  tckn: string;
  proposed_drug: string;
  severity?: "all" | "major" | "critical";
}

export interface DrugCheckResponse {
  interactions: Array<{
    type: string;
    severity: "critical" | "major" | "moderate" | "minor";
    drug1: string;
    drug2: string;
    effect: string;
    alternative_drugs?: string[];
  }>;
  safety_recommendations: string[];
}

export interface LabTest {
  TEST_ADI: string;
  SONUC: string;
  BIRIM: string;
  TEST_TARIHI: Date;
  NORMAL_MIN: string;
  NORMAL_MAX: string;
}

// API Client Class
export class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: "/api/v1",
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Apply retry logic
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return (
          axiosRetry.isNetworkOrIdempotentRequestError(error) ||
          (error.response?.status ?? 0) >= 500
        );
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any request logging or authentication
        if (process.env.NODE_ENV === "development") {
          logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        if (process.env.NODE_ENV === "development") {
          logger.debug(
            `API Response: ${response.status} ${response.config.url}`,
          );
        }
        return response;
      },
      (error: AxiosError) => {
        const errorMessage = this.handleError(error);
        if (process.env.NODE_ENV === "development") {
          logger.error("API Error:", errorMessage);
        }
        return Promise.reject(error);
      },
    );
  }

  private handleError(error: AxiosError): string {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 400:
          return data?.message || "Invalid request data";
        case 404:
          return "Resource not found";
        case 500:
          return "Server error occurred";
        default:
          return data?.message || `Request failed with status ${status}`;
      }
    } else if (error.request) {
      // Network error
      return "Network error - please check your connection";
    } else {
      // Other error
      return error.message || "An unexpected error occurred";
    }
  }

  // Health checks
  async getHealth() {
    const response = await axios.get("/health");
    return response.data;
  }

  async getDatabaseHealth() {
    const response = await axios.get("/health/database");
    return response.data;
  }

  // Patient operations
  async searchPatients(
    query: string,
    limit: number = 20,
  ): Promise<PatientSearchResult[]> {
    const response = await this.client.get("/patients/search", {
      params: { q: query, limit },
    });
    return response.data.patients || [];
  }

  async getPatient(tckn: string): Promise<PatientSummary> {
    const response = await this.client.get(`/patients/${tckn}`);
    return response.data;
  }

  // AI Analysis operations
  async generateDiagnosis(
    request: DiagnosisRequest,
  ): Promise<DiagnosisResponse> {
    const response = await this.client.post("/analyze/diagnosis", request);
    return response.data;
  }

  async generateTreatment(
    request: TreatmentRequest,
  ): Promise<TreatmentResponse> {
    const response = await this.client.post("/analyze/treatment", request);
    return response.data;
  }

  async checkDrugInteractions(
    request: DrugCheckRequest,
  ): Promise<DrugCheckResponse> {
    const response = await this.client.post("/drugs/interactions", request);
    return response.data;
  }

  // Lab operations
  async getLabTests(tckn: string, test?: string): Promise<LabTest[]> {
    const params: any = {};
    if (test) params.test = test;

    const response = await this.client.get(`/labs/${tckn}`, { params });
    return response.data;
  }

  async getLabTrends(tckn: string, test: string, months: number = 12) {
    const response = await this.client.get(`/labs/${tckn}/trends`, {
      params: { test, months },
    });
    return response.data;
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
export default apiClient;
