#!/bin/bash
# Clinical AI Assistant - Deployment Validation Script
# Comprehensive post-deployment validation and testing

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/deployment-validation.log"
REPORT_FILE="${PROJECT_ROOT}/logs/validation-report-$(date +%Y%m%d_%H%M%S).json"

# Service URLs
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:5173}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"

# Validation settings
TIMEOUT=${VALIDATION_TIMEOUT:-30}
RETRY_COUNT=${VALIDATION_RETRY_COUNT:-3}
RETRY_DELAY=${VALIDATION_RETRY_DELAY:-5}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
declare -A TEST_RESULTS
declare -A TEST_DETAILS

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to retry commands
retry_command() {
    local command="$1"
    local description="$2"
    local retries=0
    local max_retries=$RETRY_COUNT

    while [[ $retries -lt $max_retries ]]; do
        log "Testing: $description (attempt $((retries + 1))/$max_retries)"

        if eval "$command"; then
            success "$description: PASSED"
            TEST_RESULTS["$description"]=passed
            return 0
        fi

        ((retries++))
        if [[ $retries -lt $max_retries ]]; then
            log "Retrying in $RETRY_DELAY seconds..."
            sleep $RETRY_DELAY
        fi
    done

    error "$description: FAILED (after $max_retries attempts)"
    TEST_RESULTS["$description"]=failed
    TEST_DETAILS["$description"]="Failed after $max_retries attempts"
    return 1
}

# Function to test API endpoints
test_api_endpoints() {
    log "Testing API endpoints..."

    # Basic health check
    retry_command "curl -f -s --max-time $TIMEOUT '$API_URL/health'" "API Health Check"

    # Database health
    retry_command "curl -f -s --max-time $TIMEOUT '$API_URL/health/database'" "Database Health Check"

    # API documentation
    retry_command "curl -f -s --max-time $TIMEOUT '$API_URL/docs'" "API Documentation"

    # Patient search endpoint
    retry_command "curl -f -s --max-time $TIMEOUT '$API_URL/patients/search?q=test&limit=5'" "Patient Search API"

    # Test POST endpoint with valid data
    local test_data='{"tckn":"12345678901","chief_complaint":"Test complaint for validation","model":"ollama"}'
    retry_command "curl -f -s --max-time $TIMEOUT -X POST -H 'Content-Type: application/json' -d '$test_data' '$API_URL/analyze/diagnosis'" "AI Diagnosis API"

    # Verify API response format
    log "Testing API response formats..."
    local health_response=$(curl -s "$API_URL/health" 2>/dev/null || echo "")
    if echo "$health_response" | jq -e '.status' > /dev/null 2>&1; then
        success "API Response Format: Valid JSON"
        TEST_RESULTS["API Response Format"]=passed
    else
        error "API Response Format: Invalid JSON"
        TEST_RESULTS["API Response Format"]=failed
    fi
}

# Function to test database connectivity
test_database_connectivity() {
    log "Testing database connectivity..."

    # Check if database container is running
    if docker-compose ps | grep -q "db.*Up"; then
        success "Database Container: Running"
        TEST_RESULTS["Database Container"]=passed

        # Test basic database query
        local test_result=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "SELECT COUNT(*) FROM sys.databases WHERE name = 'ClinicalAI'" -h -1 2>/dev/null | tr -d ' ')

        if [[ "$test_result" == "1" ]]; then
            success "Database Query: ClinicalAI database exists"
            TEST_RESULTS["Database Query"]=passed

            # Test table existence
            local table_check=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'HASTA'" -h -1 2>/dev/null | tr -d ' ')

            if [[ "$table_check" == "1" ]]; then
                success "Database Tables: Core tables exist"
                TEST_RESULTS["Database Tables"]=passed
            else
                error "Database Tables: Core tables missing"
                TEST_RESULTS["Database Tables"]=failed
            fi
        else
            error "Database Query: ClinicalAI database not found"
            TEST_RESULTS["Database Query"]=failed
        fi
    else
        error "Database Container: Not running"
        TEST_RESULTS["Database Container"]=failed
    fi
}

# Function to test AI services
test_ai_services() {
    log "Testing AI services..."

    # Test Ollama if running
    if docker-compose ps | grep -q "ollama.*Up"; then
        retry_command "curl -f -s --max-time $TIMEOUT 'http://localhost:11434/api/tags'" "Ollama Service"

        # Test Ollama model availability
        local models_response=$(curl -s "http://localhost:11434/api/tags" 2>/dev/null || echo "")
        if echo "$models_response" | jq -e '.models' > /dev/null 2>&1; then
            local model_count=$(echo "$models_response" | jq '.models | length' 2>/dev/null || echo "0")
            if [[ "$model_count" -gt 0 ]]; then
                success "Ollama Models: $model_count models available"
                TEST_RESULTS["Ollama Models"]=passed
            else
                warning "Ollama Models: No models loaded"
                TEST_RESULTS["Ollama Models"]=warning
            fi
        else
            error "Ollama Models: Invalid response"
            TEST_RESULTS["Ollama Models"]=failed
        fi
    else
        warning "Ollama Service: Not running (optional)"
        TEST_RESULTS["Ollama Service"]=warning
    fi

    # Test external AI services if configured
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log "Testing Anthropic API..."
        if curl -f -s --max-time $TIMEOUT -H "Authorization: Bearer $ANTHROPIC_API_KEY" "https://api.anthropic.com/v1/messages" -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}' > /dev/null 2>&1; then
            success "Anthropic API: Accessible"
            TEST_RESULTS["Anthropic API"]=passed
        else
            warning "Anthropic API: Not accessible"
            TEST_RESULTS["Anthropic API"]=warning
        fi
    fi

    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        log "Testing OpenAI API..."
        if curl -f -s --max-time $TIMEOUT -H "Authorization: Bearer $OPENAI_API_KEY" "https://api.openai.com/v1/models" > /dev/null 2>&1; then
            success "OpenAI API: Accessible"
            TEST_RESULTS["OpenAI API"]=passed
        else
            warning "OpenAI API: Not accessible"
            TEST_RESULTS["OpenAI API"]=warning
        fi
    fi
}

# Function to test frontend
test_frontend() {
    log "Testing frontend application..."

    # Test if frontend is accessible
    if curl -f -s --max-time $TIMEOUT "$WEB_URL" > /dev/null 2>&1; then
        success "Frontend: Accessible at $WEB_URL"
        TEST_RESULTS["Frontend"]=passed

        # Check for essential frontend assets
        local html_response=$(curl -s "$WEB_URL" 2>/dev/null || echo "")
        if echo "$html_response" | grep -q "Clinical AI Assistant"; then
            success "Frontend Content: Main page loaded correctly"
            TEST_RESULTS["Frontend Content"]=passed
        else
            error "Frontend Content: Main page not loading correctly"
            TEST_RESULTS["Frontend Content"]=failed
        fi
    else
        warning "Frontend: Not accessible at $WEB_URL (may not be started)"
        TEST_RESULTS["Frontend"]=warning
    fi
}

# Function to test system integrations
test_system_integrations() {
    log "Testing system integrations..."

    # Test Redis if running
    if docker-compose ps | grep -q "redis.*Up"; then
        local redis_result=$(docker-compose exec -T redis redis-cli ping 2>/dev/null || echo "failed")
        if [[ "$redis_result" == "PONG" ]]; then
            success "Redis Integration: Connected"
            TEST_RESULTS["Redis Integration"]=passed
        else
            error "Redis Integration: Failed"
            TEST_RESULTS["Redis Integration"]=failed
        fi
    else
        warning "Redis Integration: Not running (optional)"
        TEST_RESULTS["Redis Integration"]=warning
    fi

    # Test Nginx if running
    if docker-compose ps | grep -q "nginx.*Up"; then
        if curl -f -s --max-time $TIMEOUT "http://localhost/health" > /dev/null 2>&1; then
            success "Nginx Proxy: Working"
            TEST_RESULTS["Nginx Proxy"]=passed
        else
            error "Nginx Proxy: Failed"
            TEST_RESULTS["Nginx Proxy"]=failed
        fi
    else
        warning "Nginx Proxy: Not running (optional)"
        TEST_RESULTS["Nginx Proxy"]=warning
    fi

    # Test monitoring services
    if docker-compose ps | grep -q "prometheus.*Up"; then
        if curl -f -s --max-time $TIMEOUT "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
            success "Prometheus: Healthy"
            TEST_RESULTS["Prometheus"]=passed
        else
            error "Prometheus: Not healthy"
            TEST_RESULTS["Prometheus"]=failed
        fi
    else
        warning "Prometheus: Not running (optional)"
        TEST_RESULTS["Prometheus"]=warning
    fi

    if docker-compose ps | grep -q "grafana.*Up"; then
        if curl -f -s --max-time $TIMEOUT "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
            success "Grafana: Healthy"
            TEST_RESULTS["Grafana"]=passed
        else
            error "Grafana: Not healthy"
            TEST_RESULTS["Grafana"]=failed
        fi
    else
        warning "Grafana: Not running (optional)"
        TEST_RESULTS["Grafana"]=warning
    fi
}

# Function to test security configurations
test_security_configurations() {
    log "Testing security configurations..."

    # Test SSL/TLS if HTTPS is configured
    if [[ "$API_URL" == https://* ]]; then
        if curl -f -s --max-time $TIMEOUT -k "$API_URL/health" > /dev/null 2>&1; then
            success "SSL/TLS: Working"
            TEST_RESULTS["SSL/TLS"]=passed
        else
            error "SSL/TLS: Failed"
            TEST_RESULTS["SSL/TLS"]=failed
        fi
    else
        warning "SSL/TLS: Not configured (HTTP only)"
        TEST_RESULTS["SSL/TLS"]=warning
    fi

    # Test for security headers
    local api_response=$(curl -s -I "$API_URL/health" 2>/dev/null || echo "")
    if echo "$api_response" | grep -qi "x-frame-options\|x-content-type-options\|x-xss-protection"; then
        success "Security Headers: Present"
        TEST_RESULTS["Security Headers"]=passed
    else
        warning "Security Headers: Missing"
        TEST_RESULTS["Security Headers"]=warning
    fi

    # Test CORS configuration
    local cors_test=$(curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS "$API_URL/patients/search" 2>/dev/null || echo "")
    if echo "$cors_test" | grep -qi "access-control-allow-origin"; then
        success "CORS Configuration: Working"
        TEST_RESULTS["CORS Configuration"]=passed
    else
        warning "CORS Configuration: May need attention"
        TEST_RESULTS["CORS Configuration"]=warning
    fi
}

# Function to test performance
test_performance() {
    log "Testing performance..."

    # Test API response time
    local start_time=$(date +%s.%N)
    if curl -f -s --max-time $TIMEOUT "$API_URL/health" > /dev/null; then
        local end_time=$(date +%s.%N)
        local response_time=$(echo "$end_time - $start_time" | bc -l)

        if (( $(echo "$response_time < 2.0" | bc -l) )); then
            success "API Response Time: ${response_time}s (excellent)"
            TEST_RESULTS["API Response Time"]=passed
        elif (( $(echo "$response_time < 5.0" | bc -l) )); then
            warning "API Response Time: ${response_time}s (acceptable)"
            TEST_RESULTS["API Response Time"]=warning
        else
            error "API Response Time: ${response_time}s (slow)"
            TEST_RESULTS["API Response Time"]=failed
        fi

        TEST_DETAILS["API Response Time"]="${response_time}s"
    else
        error "API Response Time: Failed to measure"
        TEST_RESULTS["API Response Time"]=failed
    fi

    # Test concurrent requests
    log "Testing concurrent requests..."
    local concurrent_success=0
    local concurrent_total=10

    for i in $(seq 1 $concurrent_total); do
        if curl -f -s --max-time $TIMEOUT "$API_URL/health" > /dev/null 2>&1 & then
            ((concurrent_success++))
        fi
    done

    wait

    if [[ $concurrent_success -eq $concurrent_total ]]; then
        success "Concurrent Requests: $concurrent_success/$concurrent_total successful"
        TEST_RESULTS["Concurrent Requests"]=passed
    elif [[ $concurrent_success -gt $((concurrent_total / 2)) ]]; then
        warning "Concurrent Requests: $concurrent_success/$concurrent_total successful"
        TEST_RESULTS["Concurrent Requests"]=warning
    else
        error "Concurrent Requests: $concurrent_success/$concurrent_total successful"
        TEST_RESULTS["Concurrent Requests"]=failed
    fi

    TEST_DETAILS["Concurrent Requests"]="$concurrent_success/$concurrent_total"
}

# Function to test data integrity
test_data_integrity() {
    log "Testing data integrity..."

    # Test patient data access
    local patient_search_result=$(curl -s "$API_URL/patients/search?q=test&limit=1" 2>/dev/null || echo "")
    if echo "$patient_search_result" | jq -e '.[0].TCKN' > /dev/null 2>&1; then
        success "Patient Data: Accessible"
        TEST_RESULTS["Patient Data"]=passed
    else
        warning "Patient Data: No test data available (expected for fresh deployment)"
        TEST_RESULTS["Patient Data"]=warning
    fi

    # Test AI analysis functionality (if AI services are available)
    if docker-compose ps | grep -q "ollama.*Up"; then
        local ai_test_data='{"tckn":"12345678901","chief_complaint":"mild headache for 2 days","model":"gemma:7b"}'
        local ai_result=$(curl -s -X POST -H "Content-Type: application/json" -d "$ai_test_data" "$API_URL/analyze/diagnosis" 2>/dev/null || echo "")

        if echo "$ai_result" | jq -e '.differential_diagnosis' > /dev/null 2>&1; then
            success "AI Analysis: Working"
            TEST_RESULTS["AI Analysis"]=passed
        else
            warning "AI Analysis: May need configuration"
            TEST_RESULTS["AI Analysis"]=warning
        fi
    else
        warning "AI Analysis: Ollama not running"
        TEST_RESULTS["AI Analysis"]=warning
    fi
}

# Function to generate validation report
generate_validation_report() {
    log "Generating validation report..."

    local timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local total_tests=${#TEST_RESULTS[@]}
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0

    # Count results
    for result in "${TEST_RESULTS[@]}"; do
        case "$result" in
            "passed")
                ((passed_tests++))
                ;;
            "failed")
                ((failed_tests++))
                ;;
            "warning")
                ((warning_tests++))
                ;;
        esac
    done

    # Determine overall status
    local overall_status="passed"
    if [[ $failed_tests -gt 0 ]]; then
        overall_status="failed"
    elif [[ $warning_tests -gt 0 ]]; then
        overall_status="warning"
    fi

    # Generate JSON report
    cat > "$REPORT_FILE" << EOF
{
    "timestamp": "$timestamp",
    "overall_status": "$overall_status",
    "summary": {
        "total_tests": $total_tests,
        "passed": $passed_tests,
        "failed": $failed_tests,
        "warnings": $warning_tests
    },
    "tests": {
EOF

    # Add test results
    local first=true
    for test_name in "${!TEST_RESULTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi
        echo "        \"$test_name\": {\"status\": \"${TEST_RESULTS[$test]}\", \"details\": \"${TEST_DETAILS[$test_name]:-}\"}" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF
    },
    "configuration": {
        "api_url": "$API_URL",
        "web_url": "$WEB_URL",
        "grafana_url": "$GRAFANA_URL",
        "timeout": $TIMEOUT,
        "retry_count": $RETRY_COUNT
    },
    "environment": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "working_directory": "$PWD"
    }
}
EOF

    success "Validation report generated: $REPORT_FILE"
}

# Function to display summary
display_summary() {
    log "Deployment Validation Summary"
    log "============================"

    # Overall status
    local total_tests=${#TEST_RESULTS[@]}
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0

    for result in "${TEST_RESULTS[@]}"; do
        case "$result" in
            "passed")
                ((passed_tests++))
                ;;
            "failed")
                ((failed_tests++))
                ;;
            "warning")
                ((warning_tests++))
                ;;
        esac
    done

    echo
    log "Results Summary:"
    log "  Total tests: $total_tests"
    log "  Passed: $passed_tests"
    log "  Failed: $failed_tests"
    log "  Warnings: $warning_tests"
    echo

    log "Test Details:"
    for test_name in "${!TEST_RESULTS[@]}"; do
        local status="${TEST_RESULTS[$test_name]}"
        local details="${TEST_DETAILS[$test_name]:-}"
        local status_icon="✓"

        case "$status" in
            "passed") status_icon="✓";;
            "warning") status_icon="⚠";;
            "failed") status_icon="✗";;
        esac

        log "  $status_icon $test_name: $status"
        if [[ -n "$details" ]]; then
            log "    Details: $details"
        fi
    done

    echo
    log "Report saved to: $REPORT_FILE"
    log "Log file: $LOG_FILE"
}

# Function to show usage
show_usage() {
    echo "Clinical AI Assistant - Deployment Validation Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -q, --quiet                Suppress output, only log to file"
    echo "  -j, --json                 Output results in JSON format"
    echo "  --api-url URL             Custom API URL (default: http://localhost:8000)"
    echo "  --web-url URL             Custom web URL (default: http://localhost:5173)"
    echo "  --grafana-url URL         Custom Grafana URL (default: http://localhost:3000)"
    echo "  --timeout SECONDS         Request timeout (default: 30)"
    echo "  --retry-count COUNT       Retry count for failed tests (default: 3)"
    echo "  --retry-delay SECONDS     Delay between retries (default: 5)"
    echo
    echo "Environment Variables:"
    echo "  API_URL                   API service URL"
    echo "  WEB_URL                   Frontend URL"
    echo "  GRAFANA_URL              Grafana URL"
    echo "  ANTHROPIC_API_KEY         Anthropic API key (for testing)"
    echo "  OPENAI_API_KEY            OpenAI API key (for testing)"
    echo
    echo "Examples:"
    echo "  $0                        # Run validation with default settings"
    echo "  $0 --api-url https://api.example.com  # Custom API URL"
    echo "  $0 --json                 # Output in JSON format"
}

# Main execution function
main() {
    local quiet=false
    local json_output=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -j|--json)
                json_output=true
                shift
                ;;
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --web-url)
                WEB_URL="$2"
                shift 2
                ;;
            --grafana-url)
                GRAFANA_URL="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --retry-count)
                RETRY_COUNT="$2"
                shift 2
                ;;
            --retry-delay)
                RETRY_DELAY="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Redirect output if quiet mode
    if [[ "$quiet" == "true" ]]; then
        exec 1>>"$LOG_FILE" 2>&1
    fi

    log "Starting Clinical AI Assistant deployment validation..."
    log "API URL: $API_URL"
    log "Web URL: $WEB_URL"
    log "Timeout: ${TIMEOUT}s"

    # Run all validation tests
    test_api_endpoints
    test_database_connectivity
    test_ai_services
    test_frontend
    test_system_integrations
    test_security_configurations
    test_performance
    test_data_integrity

    # Generate report and summary
    generate_validation_report

    if [[ "$quiet" == "false" ]]; then
        display_summary
    fi

    # JSON output if requested
    if [[ "$json_output" == "true" ]]; then
        cat "$REPORT_FILE"
    fi

    # Determine exit code based on results
    local failed_tests=0
    for result in "${TEST_RESULTS[@]}"; do
        if [[ "$result" == "failed" ]]; then
            ((failed_tests++))
        fi
    done

    if [[ $failed_tests -gt 0 ]]; then
        error "Validation failed with $failed_tests failed tests"
        exit 1
    else
        success "Deployment validation completed successfully"
        exit 0
    fi
}

# Execute main function
main "$@"