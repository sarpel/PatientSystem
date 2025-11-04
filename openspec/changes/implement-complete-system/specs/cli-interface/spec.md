# CLI Interface Capability Specification

## ADDED Requirements

### Requirement: Typer-Based Command Structure

The system SHALL provide a hierarchical command-line interface using Typer framework.

#### Scenario: Display help information

- **WHEN** user runs `clinical-ai --help`
- **THEN** CLI displays command list with descriptions in Rich-formatted output

#### Scenario: Version information

- **WHEN** user runs `clinical-ai --version`
- **THEN** CLI displays application version, Python version, and installed AI providers

#### Scenario: Invalid command error

- **WHEN** user runs `clinical-ai invalid-command`
- **THEN** CLI displays error message with suggestion for similar valid commands

### Requirement: Patient Analysis Commands

The system SHALL provide commands for patient clinical analysis and summary generation.

#### Scenario: Analyze patient by TCKN

- **WHEN** user runs `clinical-ai analyze --tckn 12345678901`
- **THEN** CLI fetches patient data, performs AI analysis, and displays formatted summary with demographics, diagnoses, medications, and alerts

#### Scenario: JSON output format

- **WHEN** user runs `clinical-ai analyze --tckn 12345678901 --output json`
- **THEN** CLI outputs complete patient analysis as valid JSON to stdout

#### Scenario: Save analysis to file

- **WHEN** user runs `clinical-ai analyze --tckn 12345678901 --save patient_analysis.json`
- **THEN** CLI writes analysis results to specified file path

### Requirement: Diagnosis Commands

The system SHALL provide commands for AI-powered diagnosis generation from symptoms.

#### Scenario: Diagnose with chief complaint

- **WHEN** user runs `clinical-ai diagnose --tckn 12345678901 --complaint "ateş, öksürük, boğaz ağrısı"`
- **THEN** CLI sends complaint to AI service and displays differential diagnoses with probability scores

#### Scenario: Include vitals in diagnosis

- **WHEN** user runs `clinical-ai diagnose --tckn 12345678901 --complaint "baş ağrısı" --vitals "BP:160/95,HR:88"`
- **THEN** CLI includes vital signs in AI prompt and returns diagnoses considering hypertension

#### Scenario: Specify AI model manually

- **WHEN** user runs `clinical-ai diagnose --tckn 12345678901 --complaint "göğüs ağrısı" --model claude`
- **THEN** CLI bypasses smart routing and sends request directly to Claude 3.5 Sonnet

### Requirement: Database Inspection Commands

The system SHALL provide commands for exploring database schema and contents.

#### Scenario: List all database tables

- **WHEN** user runs `clinical-ai inspect database`
- **THEN** CLI displays categorized table list (GP*\*, DTY*\_, LST\_\_, HRC\_\*) with row counts

#### Scenario: Show table schema

- **WHEN** user runs `clinical-ai inspect table GP_HASTA_KAYIT`
- **THEN** CLI displays column names, types, constraints, and foreign key relationships

#### Scenario: Query patient statistics

- **WHEN** user runs `clinical-ai inspect stats`
- **THEN** CLI displays total patients, active patients, visits this year, and most common diagnoses

### Requirement: Configuration Management Commands

The system SHALL provide commands for viewing and modifying application configuration.

#### Scenario: Display current configuration

- **WHEN** user runs `clinical-ai config show`
- **THEN** CLI displays current database connection, enabled AI models, and routing strategy

#### Scenario: Set AI model preference

- **WHEN** user runs `clinical-ai config set-model gpt-4o`
- **THEN** CLI updates configuration to prefer GPT-4o for complex tasks

#### Scenario: Test AI provider connection

- **WHEN** user runs `clinical-ai config test-ai`
- **THEN** CLI attempts connection to each enabled AI provider and reports success/failure status

### Requirement: Drug Interaction Check Commands

The system SHALL provide commands for checking drug interactions and contraindications.

#### Scenario: Check interaction for new drug

- **WHEN** user runs `clinical-ai drug-check --tckn 12345678901 --add "Amoksisilin 1000mg"`
- **THEN** CLI analyzes patient's current medications and allergies, displays interaction warnings if any

#### Scenario: Severity filtering

- **WHEN** user runs `clinical-ai drug-check --tckn 12345678901 --add "Aspirin" --severity major`
- **THEN** CLI displays only major and critical interactions, hiding minor warnings

#### Scenario: Alternative drug suggestions

- **WHEN** drug interaction is detected
- **THEN** CLI displays list of alternative medications without interactions

### Requirement: Rich Terminal Formatting

The system SHALL use Rich library for enhanced terminal output with colors, tables, and progress indicators.

#### Scenario: Progress bar for long operations

- **WHEN** user runs analysis command that takes >2 seconds
- **THEN** CLI displays progress bar with estimated time remaining

#### Scenario: Color-coded severity indicators

- **WHEN** CLI displays clinical alerts
- **THEN** critical alerts are red, warnings are yellow, info is blue, success is green

#### Scenario: Formatted tables for results

- **WHEN** CLI displays diagnosis results
- **THEN** output uses Rich table with borders, column headers, and aligned text

### Requirement: Batch Processing Support

The system SHALL support batch operations on multiple patients via CSV input.

#### Scenario: Analyze multiple patients from CSV

- **WHEN** user runs `clinical-ai batch analyze --input patients.csv`
- **THEN** CLI processes each patient TCKN from CSV and exports results to patients_analysis.json

#### Scenario: Progress tracking for batch jobs

- **WHEN** batch processing is running
- **THEN** CLI displays progress bar with current patient count and estimated completion time

#### Scenario: Error handling in batch mode

- **WHEN** batch processing encounters invalid TCKN
- **THEN** CLI logs error, continues processing remaining patients, and reports failed entries at end
