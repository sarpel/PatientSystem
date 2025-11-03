import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { apiClient, Patient } from '../services/api'

// Types
interface AppState {
  // App state
  appReady: boolean
  loading: boolean
  error: string | null

  // Patient state
  currentPatient: Patient | null
  patientSearchResults: Patient[]
  searchingPatients: boolean

  // Database/AI status
  databaseStatus: 'connected' | 'disconnected' | 'unknown'
  aiStatus: 'ready' | 'unavailable' | 'unknown'
}

interface AppActions {
  // App actions
  initializeApp: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void

  // Patient actions
  setCurrentPatient: (patient: Patient | null) => void
  searchPatients: (query: string) => Promise<Patient[]>
  clearPatientSearch: () => void

  // Status actions
  updateDatabaseStatus: (status: 'connected' | 'disconnected' | 'unknown') => void
  updateAIStatus: (status: 'ready' | 'unavailable' | 'unknown') => void
}

type AppStore = AppState & AppActions

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        appReady: false,
        loading: false,
        error: null,
        currentPatient: null,
        patientSearchResults: [],
        searchingPatients: false,
        databaseStatus: 'unknown',
        aiStatus: 'unknown',

        // App actions
        initializeApp: async () => {
          const { setLoading, setError, updateDatabaseStatus, updateAIStatus } = get()

          setLoading(true)
          setError(null)

          try {
            // Check database and AI health
            await Promise.all([
              apiClient.getHealth().then(() => {
                updateDatabaseStatus('connected')
              }).catch(() => {
                updateDatabaseStatus('disconnected')
              }),

              apiClient.getHealth().then(() => {
                updateAIStatus('ready')
              }).catch(() => {
                updateAIStatus('unavailable')
              })
            ])

            set({ appReady: true })
          } catch (error) {
            console.error('Failed to initialize app:', error)
            setError('Failed to initialize application')
          } finally {
            setLoading(false)
          }
        },

        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),

        // Patient actions
        setCurrentPatient: (patient) => set({ currentPatient: patient }),

        searchPatients: async (query: string) => {
          if (!query || query.length < 2) {
            set({ patientSearchResults: [] })
            return []
          }

          set({ searchingPatients: true, error: null })

          try {
            const results = await apiClient.searchPatients(query)
            set({ patientSearchResults: results })
            return results
          } catch (error) {
            console.error('Patient search failed:', error)
            set({ error: 'Failed to search patients' })
            return []
          } finally {
            set({ searchingPatients: false })
          }
        },

        clearPatientSearch: () => set({
          patientSearchResults: [],
          searchingPatients: false
        }),

        // Status actions
        updateDatabaseStatus: (status) => set({ databaseStatus: status }),
        updateAIStatus: (status) => set({ aiStatus: status }),
      }),
      {
        name: 'clinical-ai-store',
        partialize: (state) => ({
          currentPatient: state.currentPatient,
          databaseStatus: state.databaseStatus,
          aiStatus: state.aiStatus,
        }),
      }
    ),
    {
      name: 'clinical-ai-store',
    }
  )
)

// Selectors
export const useAppState = () => useAppStore((state) => ({
  appReady: state.appReady,
  loading: state.loading,
  error: state.error,
}))

export const usePatientState = () => useAppStore((state) => ({
  currentPatient: state.currentPatient,
  patientSearchResults: state.patientSearchResults,
  searchingPatients: state.searchingPatients,
}))

export const useSystemStatus = () => useAppStore((state) => ({
  databaseStatus: state.databaseStatus,
  aiStatus: state.aiStatus,
}))

export const useAppActions = () => useAppStore((state) => ({
  initializeApp: state.initializeApp,
  setLoading: state.setLoading,
  setError: state.setError,
  clearError: state.clearError,
  setCurrentPatient: state.setCurrentPatient,
  searchPatients: state.searchPatients,
  clearPatientSearch: state.clearPatientSearch,
  updateDatabaseStatus: state.updateDatabaseStatus,
  updateAIStatus: state.updateAIStatus,
}))
