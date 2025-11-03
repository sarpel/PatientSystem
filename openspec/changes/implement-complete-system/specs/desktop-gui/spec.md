# Desktop GUI Capability Specification

## ADDED Requirements

### Requirement: Main Application Window
The system SHALL provide a PySide6-based desktop application with MenuBar, StatusBar, and tabbed central widget.

#### Scenario: Application launch
- **WHEN** user runs the desktop application
- **THEN** the main window opens with title "Clinical AI Assistant", menu bar, and status bar showing connection status

#### Scenario: Database connection indicator
- **WHEN** database connection is successful
- **THEN** status bar displays "DB: ✓ Bağlı" with green indicator

#### Scenario: AI model indicator
- **WHEN** AI services are configured
- **THEN** status bar displays current AI model (e.g., "AI Model: Claude 3.5 Sonnet")

### Requirement: Patient Search Widget
The system SHALL provide patient search by TCKN, name, or protocol number with autocomplete.

#### Scenario: Search by TCKN
- **WHEN** user enters 11-digit TCKN and clicks "Ara"
- **THEN** system queries database and displays matching patient in results table

#### Scenario: Search by name with autocomplete
- **WHEN** user types at least 3 characters of patient name
- **THEN** system displays autocomplete dropdown with matching patients

#### Scenario: Patient selection
- **WHEN** user double-clicks a patient in results table
- **THEN** system loads patient clinical dashboard and emits patient_selected signal

### Requirement: Clinical Dashboard with Tabs
The system SHALL organize clinical information in tabbed panels for easy navigation.

#### Scenario: Overview tab displays patient summary
- **WHEN** patient is selected
- **THEN** Overview tab shows demographics, recent visits, active diagnoses, medications, allergies, and alerts

#### Scenario: Diagnosis tab for AI analysis
- **WHEN** user switches to Diagnosis tab
- **THEN** tab displays chief complaint input, vitals input, and "AI TANI HESAPLA" button

#### Scenario: Treatment tab for recommendations
- **WHEN** user switches to Treatment tab
- **THEN** tab displays diagnosis selector and treatment recommendations panel

#### Scenario: Lab tab for test results
- **WHEN** user switches to Lab tab
- **THEN** tab displays lab results table with reference ranges and trend charts

### Requirement: AI-Powered Diagnosis Panel
The system SHALL provide interactive diagnosis suggestions with probability scoring.

#### Scenario: Trigger AI diagnosis analysis
- **WHEN** user enters chief complaint "ateş, öksürük, balgam" and clicks "AI TANI HESAPLA"
- **THEN** system shows progress indicator and sends request to AI service

#### Scenario: Display differential diagnosis results
- **WHEN** AI analysis completes successfully
- **THEN** panel displays ranked list of diagnoses with ICD-10 codes, probability percentages, and supporting findings

#### Scenario: Red flag warnings
- **WHEN** AI identifies urgent conditions (e.g., chest pain with radiation)
- **THEN** system displays red warning banner with emergency alert icon

### Requirement: Treatment Recommendations Panel
The system SHALL display evidence-based treatment suggestions organized by category.

#### Scenario: Pharmacological recommendations
- **WHEN** treatment analysis completes
- **THEN** panel displays medication suggestions with dosage, frequency, contraindications, and priority ratings

#### Scenario: Lifestyle recommendations
- **WHEN** treatment analysis completes
- **THEN** panel displays lifestyle modifications (diet, exercise) with implementation guidance

#### Scenario: Laboratory follow-up plan
- **WHEN** treatment analysis completes
- **THEN** panel displays recommended lab tests with frequency and target values

### Requirement: Lab Trend Charts
The system SHALL visualize lab results over time with reference range indicators.

#### Scenario: Display HbA1c trend chart
- **WHEN** user selects HbA1c lab test
- **THEN** chart displays values over last 12 months with reference range shaded area and trend line

#### Scenario: Highlight critical values
- **WHEN** lab value exceeds critical threshold (e.g., Potassium >6.5)
- **THEN** chart marks the point with red icon and critical alert label

#### Scenario: Interactive chart tooltips
- **WHEN** user hovers over a data point
- **THEN** tooltip displays exact value, date, reference range, and deviation percentage

### Requirement: Drug Interaction Alert Dialogs
The system SHALL warn users about drug-drug and drug-allergy interactions before prescribing.

#### Scenario: Major drug interaction warning
- **WHEN** user attempts to prescribe NSAİİ to patient on Warfarin
- **THEN** system displays blocking dialog with severity "Major", interaction description, and alternative suggestions

#### Scenario: Critical allergy alert
- **WHEN** user attempts to prescribe Amoxicillin to patient with Penicillin allergy
- **THEN** system displays blocking dialog with red background "KESİNLİKLE KULLANMAYIN!" and alternative antibiotics

#### Scenario: User override with confirmation
- **WHEN** user acknowledges moderate interaction warning
- **THEN** system requires explicit confirmation and logs the override decision

### Requirement: Configuration Management Dialog
The system SHALL allow users to configure AI models and database settings through GUI.

#### Scenario: AI model selection
- **WHEN** user opens Settings → AI Configuration dialog
- **THEN** dialog displays checkboxes to enable/disable each AI provider and input fields for API keys

#### Scenario: Database connection settings
- **WHEN** user opens Settings → Database Configuration dialog
- **THEN** dialog displays server name, database name, authentication type, and "Test Connection" button

#### Scenario: Save and apply configuration
- **WHEN** user clicks "Save" in configuration dialog
- **THEN** system validates settings, saves to .env file, and restarts affected services
