import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'

// Types
export interface Patient {
  TCKN: string
  ADI: string
  SOYADI: string
  DOGUM_TARIHI?: string
  CINSIYET?: 'E' | 'K'
  TELEFON?: string
  ADRES?: string
}

export interface DiagnosisRequest {
  tckn: string
  chief_complaint: string
  model?: string
}

export interface DiagnosisResponse {
  differential_diagnosis: Array<{
    diagnosis: string
    icd10: string
    probability: number
    urgency: 'critical' | 'major' | 'moderate' | 'minor'
  }>
  red_flags: string[]
  recommended_tests: string[]
}

export interface TreatmentRequest {
  tckn: string
  diagnosis: string
  model?: string
}

export interface TreatmentResponse {
  medications: Array<{
    name: string
    dosage: string
    duration: string
  }>
  clinical_guidelines: string
  followup_plan: string
}

export interface DrugCheckRequest {
  tckn: string
  proposed_drug: string
  severity?: 'all' | 'major' | 'critical'
}

export interface DrugCheckResponse {
  interactions: Array<{
    type: string
    severity: 'critical' | 'major' | 'moderate' | 'minor'
    drug1: string
    drug2: string
    effect: string
    alternative_drugs?: string[]
  }>
  safety_recommendations: string[]
}

export interface LabTest {
  TEST_ADI: string
  SONUC: string
  BIRIM: string
  TEST_TARIHI: Date
  NORMAL_MIN: string
  NORMAL_MAX: string
}

// API Client Class
export class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any request logging or authentication
        if (process.env.NODE_ENV === 'development') {
          console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        if (process.env.NODE_ENV === 'development') {
          console.log(`API Response: ${response.status} ${response.config.url}`)
        }
        return response
      },
      (error: AxiosError) => {
        const errorMessage = this.handleError(error)
        if (process.env.NODE_ENV === 'development') {
          console.error('API Error:', errorMessage)
        }
        return Promise.reject(error)
      }
    )
  }

  private handleError(error: AxiosError): string {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          return data?.message || 'Invalid request data'
        case 404:
          return 'Resource not found'
        case 500:
          return 'Server error occurred'
        default:
          return data?.message || `Request failed with status ${status}`
      }
    } else if (error.request) {
      // Network error
      return 'Network error - please check your connection'
    } else {
      // Other error
      return error.message || 'An unexpected error occurred'
    }
  }

  // Health checks
  async getHealth() {
    const response = await this.client.get('/health')
    return response.data
  }

  async getDatabaseHealth() {
    const response = await this.client.get('/health/database')
    return response.data
  }

  // Patient operations
  async searchPatients(query: string, limit: number = 20): Promise<Patient[]> {
    const response = await this.client.get('/patients/search', {
      params: { q: query, limit }
    })
    return response.data
  }

  async getPatient(tckn: string): Promise<Patient> {
    const response = await this.client.get(`/patients/${tckn}`)
    return response.data
  }

  // AI Analysis operations
  async generateDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResponse> {
    const response = await this.client.post('/analyze/diagnosis', request)
    return response.data
  }

  async generateTreatment(request: TreatmentRequest): Promise<TreatmentResponse> {
    const response = await this.client.post('/analyze/treatment', request)
    return response.data
  }

  async checkDrugInteractions(request: DrugCheckRequest): Promise<DrugCheckResponse> {
    const response = await this.client.post('/drugs/interactions', request)
    return response.data
  }

  // Lab operations
  async getLabTests(tckn: string, test?: string): Promise<LabTest[]> {
    const params: any = {}
    if (test) params.test = test

    const response = await this.client.get(`/labs/${tckn}`, { params })
    return response.data
  }

  async getLabTrends(tckn: string, test: string, months: number = 12) {
    const response = await this.client.get(`/labs/${tckn}/trends`, {
      params: { test, months }
    })
    return response.data
  }
}

// Create singleton instance
export const apiClient = new ApiClient()
export default apiClient
