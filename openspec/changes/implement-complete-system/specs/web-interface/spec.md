# Web Interface Capability Specification

## ADDED Requirements

### Requirement: React-Based Web Application

The system SHALL provide a modern, responsive web interface built with React 18 and Vite.

#### Scenario: Development server launch

- **WHEN** developer runs `npm run dev` in frontend directory
- **THEN** Vite dev server starts on http://localhost:5173 with hot module replacement

#### Scenario: Production build

- **WHEN** developer runs `npm run build`
- **THEN** Vite generates optimized production bundle in dist/ directory with code splitting

#### Scenario: Responsive layout adaptation

- **WHEN** user accesses web app on tablet (768px width)
- **THEN** layout adjusts to single-column view with collapsible sidebar

### Requirement: Patient Search Component

The system SHALL provide type-ahead patient search with real-time API queries.

#### Scenario: Type-ahead search with debouncing

- **WHEN** user types patient name or TCKN with 300ms pause
- **THEN** component sends API request and displays matching results dropdown

#### Scenario: Search results display

- **WHEN** API returns patient list
- **THEN** component displays patient name, TCKN, age, and last visit date for each result

#### Scenario: Patient selection navigation

- **WHEN** user clicks a patient from search results
- **THEN** app navigates to /patient/:tckn route and loads clinical dashboard

### Requirement: Clinical Dashboard Component

The system SHALL organize patient clinical data in tabbed interface with real-time updates.

#### Scenario: Dashboard initialization

- **WHEN** user navigates to patient dashboard
- **THEN** component fetches patient summary, recent visits, active diagnoses, and medications in parallel

#### Scenario: Tab navigation

- **WHEN** user clicks "Tanı" tab
- **THEN** component switches to diagnosis panel without page reload and preserves previous tab state

#### Scenario: Loading states

- **WHEN** component is fetching data from API
- **THEN** skeleton loaders display in place of content with pulsing animation

### Requirement: Diagnosis Panel Component

The system SHALL provide interactive interface for AI-powered diagnosis generation.

#### Scenario: Chief complaint input

- **WHEN** user enters symptoms in complaint textarea
- **THEN** component tracks character count and enables "Analiz Et" button when at least 10 characters entered

#### Scenario: Vital signs input form

- **WHEN** user enters vital signs (temperature, BP, SpO2, heart rate)
- **THEN** component validates numeric ranges and highlights out-of-range values in yellow

#### Scenario: AI diagnosis request

- **WHEN** user clicks "Analiz Et" button
- **THEN** component shows loading spinner, disables button, and sends POST request to /api/v1/analyze/diagnosis

#### Scenario: Display diagnosis results

- **WHEN** API returns diagnosis results
- **THEN** component displays differential diagnoses sorted by probability with ICD-10 codes, supporting findings, and confidence scores

### Requirement: Treatment Panel Component

The system SHALL display comprehensive treatment recommendations with drug interaction alerts.

#### Scenario: Treatment recommendations display

- **WHEN** treatment analysis completes
- **THEN** component displays pharmacological, lifestyle, and follow-up recommendations in collapsible sections

#### Scenario: Drug interaction alert banner

- **WHEN** recommended medication has major interaction with current medications
- **THEN** component displays red alert banner above medication card with interaction details

#### Scenario: Expand recommendation details

- **WHEN** user clicks "Detaylar" on a medication recommendation
- **THEN** component expands to show dosage, frequency, contraindications, monitoring requirements, and cost estimate

### Requirement: Lab Charts Component

The system SHALL visualize lab results with interactive charts using Chart.js.

#### Scenario: Render HbA1c trend chart

- **WHEN** component receives lab data for HbA1c
- **THEN** line chart displays values over time with reference range shaded area (4.0-6.0%) and target line at 7.0%

#### Scenario: Critical value highlighting

- **WHEN** lab value exceeds critical threshold
- **THEN** chart marks point with red circle and displays critical value label

#### Scenario: Interactive tooltips

- **WHEN** user hovers over chart data point
- **THEN** tooltip displays exact value, date, reference range, deviation percentage, and interpretation

### Requirement: API Client Service

The system SHALL provide centralized HTTP client for all backend API communication.

#### Scenario: Axios instance configuration

- **WHEN** application initializes
- **THEN** API client creates Axios instance with baseURL http://localhost:8080 and default headers

#### Scenario: Automatic error handling

- **WHEN** API request fails with 500 Internal Server Error
- **THEN** API client intercepts response, logs error, and shows user-friendly toast notification

#### Scenario: Request retry with exponential backoff

- **WHEN** API request fails with network timeout
- **THEN** API client retries up to 2 times with 1s and 2s delays before showing error

### Requirement: State Management with Zustand

The system SHALL manage global application state using Zustand store.

#### Scenario: Current patient state

- **WHEN** user selects a patient
- **THEN** store updates currentPatient state and all subscribed components re-render with new data

#### Scenario: AI analysis loading state

- **WHEN** AI diagnosis request is in progress
- **THEN** store sets isAnalyzing: true and diagnosis button shows loading spinner

#### Scenario: Persist user preferences

- **WHEN** user changes theme or language preference
- **THEN** store persists preferences to localStorage and reloads on next session

### Requirement: Tailwind CSS Styling

The system SHALL use Tailwind CSS utility classes for consistent, responsive design.

#### Scenario: Medical theme colors

- **WHEN** components render
- **THEN** primary color is medical blue (#3B82F6), success is green (#10B981), warning is amber (#F59E0B), danger is red (#EF4444)

#### Scenario: Dark mode support

- **WHEN** user toggles dark mode
- **THEN** all components switch to dark background with light text and adjusted color contrast

#### Scenario: Responsive breakpoints

- **WHEN** screen width changes
- **THEN** layout adapts at sm:640px, md:768px, lg:1024px, xl:1280px breakpoints
