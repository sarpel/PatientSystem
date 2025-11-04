#!/bin/bash
# Clinical AI Assistant - Health Check Script
# Comprehensive system health monitoring and reporting

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/health-check.log"
REPORT_FILE="${PROJECT_ROOT}/logs/health-report-$(date +%Y%m%d_%H%M%S).json"
ALERT_THRESHOLD=${ALERT_THRESHOLD:-3}  # Number of failures before alerting

# Service URLs
API_URL="http://localhost:8000"
DATABASE_HOST="localhost"
REDIS_HOST="localhost"
OLLAMA_URL="http://localhost:11434"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Health check results
declare -A RESULTS
declare -A RESPONSE_TIMES
declare -A ERROR_COUNTS

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    ((ERROR_COUNTS["$1"]++))
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
    RESULTS["$1"]=healthy
}

# Function to measure response time
measure_response_time() {
    local url="$1"
    local timeout="${2:-10}"
    local start_time=$(date +%s.%N)

    if curl -f -s --max-time "$timeout" "$url" > /dev/null; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l)
        echo "$duration"
        return 0
    else
        echo "timeout"
        return 1
    fi
}

# Function to check API service
check_api_service() {
    log "Checking API service..."

    local health_url="${API_URL}/health"
    local response_time
    response_time=$(measure_response_time "$health_url" 5)

    if [[ "$response_time" == "timeout" ]]; then
        error "API Service: Health check timeout"
        RESULTS["api"]=unhealthy
        return 1
    fi

    local status_code=$(curl -f -s -o /dev/null -w "%{http_code}" --max-time 5 "$health_url")

    if [[ "$status_code" == "200" ]]; then
        RESPONSE_TIMES["api"]="$response_time"
        success "API Service: Healthy (${response_time}s)"

        # Additional API checks
        check_api_endpoints
        return 0
    else
        error "API Service: HTTP $status_code"
        RESULTS["api"]=unhealthy
        return 1
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    log "Checking API endpoints..."

    local endpoints=(
        "/health"
        "/health/database"
        "/patients/search?q=test&limit=1"
    )

    for endpoint in "${endpoints[@]}"; do
        local url="${API_URL}${endpoint}"
        local response_time
        response_time=$(measure_response_time "$url" 10)

        if [[ "$response_time" != "timeout" ]]; then
            log "  ✓ $endpoint (${response_time}s)"
        else
            error "  ✗ $endpoint (timeout)"
        fi
    done
}

# Function to check database connectivity
check_database() {
    log "Checking database connectivity..."

    # Check if SQL Server container is running
    if docker-compose ps | grep -q "db.*Up"; then
        local test_query="SELECT 1"

        if docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "$test_query" > /dev/null 2>&1; then
            success "Database: Connected and responding"

            # Check database size and health
            check_database_health
            return 0
        else
            error "Database: Query failed"
            RESULTS["database"]=unhealthy
            return 1
        fi
    else
        error "Database: Container not running"
        RESULTS["database"]=unhealthy
        return 1
    fi
}

# Function to check database health metrics
check_database_health() {
    log "Checking database health metrics..."

    # Get database size
    local db_size=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "
        SELECT CAST(SUM(size * 8.0 / 1024) AS DECIMAL(10,2))
        FROM sys.master_files
        WHERE database_id = DB_ID('ClinicalAI')
    " -h -1 | tr -d ' ')

    # Get active connections
    local connections=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "
        SELECT COUNT(*)
        FROM sys.dm_exec_sessions
        WHERE is_user_process = 1
    " -h -1 | tr -d ' ')

    log "  Database size: ${db_size}MB"
    log "  Active connections: $connections"

    # Check for long-running queries
    local long_queries=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q "
        SELECT COUNT(*)
        FROM sys.dm_exec_requests
        WHERE total_elapsed_time > 30000000  -- 30 seconds
    " -h -1 | tr -d ' ')

    if [[ "$long_queries" -gt 0 ]]; then
        warning "  Long-running queries: $long_queries"
    fi
}

# Function to check Redis cache
check_redis() {
    log "Checking Redis cache..."

    if docker-compose ps | grep -q "redis.*Up"; then
        local response
        response=$(docker-compose exec -T redis redis-cli ping 2>/dev/null || echo "failed")

        if [[ "$response" == "PONG" ]]; then
            success "Redis: Responding"

            # Get Redis metrics
            check_redis_metrics
            return 0
        else
            error "Redis: Not responding"
            RESULTS["redis"]=unhealthy
            return 1
        fi
    else
        error "Redis: Container not running"
        RESULTS["redis"]=unhealthy
        return 1
    fi
}

# Function to check Redis metrics
check_redis_metrics() {
    log "Checking Redis metrics..."

    # Get memory usage
    local memory_info=$(docker-compose exec -T redis redis-cli info memory 2>/dev/null || echo "")
    local used_memory=$(echo "$memory_info" | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')

    # Get key count
    local key_count=$(docker-compose exec -T redis redis-cli dbsize 2>/dev/null || echo "0")

    # Get connection count
    local connected_clients=$(docker-compose exec -T redis redis-cli info clients 2>/dev/null | grep "connected_clients:" | cut -d: -f2 | tr -d '\r' || echo "0")

    log "  Memory usage: ${used_memory:-unknown}"
    log "  Keys: $key_count"
    log "  Connected clients: $connected_clients"
}

# Function to check Ollama AI service
check_ollama() {
    log "Checking Ollama AI service..."

    if docker-compose ps | grep -q "ollama.*Up"; then
        local response_time
        response_time=$(measure_response_time "${OLLAMA_URL}/api/tags" 10)

        if [[ "$response_time" != "timeout" ]]; then
            success "Ollama: Responding (${response_time}s)"

            # Check loaded models
            check_ollama_models
            return 0
        else
            error "Ollama: Not responding"
            RESULTS["ollama"]=unhealthy
            return 1
        fi
    else
        warning "Ollama: Container not running (optional service)"
        RESULTS["ollama"]=disabled
        return 0
    fi
}

# Function to check Ollama models
check_ollama_models() {
    log "Checking Ollama models..."

    local models=$(curl -f -s "${OLLAMA_URL}/api/tags" 2>/dev/null | jq -r '.models[].name' 2>/dev/null || echo "")

    if [[ -n "$models" ]]; then
        while IFS= read -r model; do
            if [[ -n "$model" ]]; then
                log "  ✓ Model loaded: $model"
            fi
        done <<< "$models"
    else
        warning "  No models loaded"
    fi
}

# Function to check system resources
check_system_resources() {
    log "Checking system resources..."

    # Check disk space
    local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        error "Disk usage critical: ${disk_usage}%"
        RESULTS["disk"]=critical
    elif [[ $disk_usage -gt 80 ]]; then
        warning "Disk usage high: ${disk_usage}%"
        RESULTS["disk"]=warning
    else
        success "Disk usage OK: ${disk_usage}%"
        RESULTS["disk"]=healthy
    fi

    # Check memory usage
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $memory_usage -gt 90 ]]; then
        error "Memory usage critical: ${memory_usage}%"
        RESULTS["memory"]=critical
    elif [[ $memory_usage -gt 80 ]]; then
        warning "Memory usage high: ${memory_usage}%"
        RESULTS["memory"]=warning
    else
        success "Memory usage OK: ${memory_usage}%"
        RESULTS["memory"]=healthy
    fi

    # Check CPU load
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_count=$(nproc)
    local load_percentage=$(echo "$load_avg * 100 / $cpu_count" | bc -l)

    if (( $(echo "$load_percentage > 90" | bc -l) )); then
        error "CPU load critical: ${load_percentage}%"
        RESULTS["cpu"]=critical
    elif (( $(echo "$load_percentage > 80" | bc -l) )); then
        warning "CPU load high: ${load_percentage}%"
        RESULTS["cpu"]=warning
    else
        success "CPU load OK: ${load_percentage}%"
        RESULTS["cpu"]=healthy
    fi
}

# Function to check Docker services
check_docker_services() {
    log "Checking Docker services..."

    local services=("api" "db" "redis" "ollama")
    local unhealthy_services=0

    for service in "${services[@]}"; do
        local status=$(docker-compose ps -q "$service" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null || echo "not_found")

        case "$status" in
            "running")
                log "  ✓ $service: running"
                ;;
            "exited")
                error "  ✗ $service: exited"
                ((unhealthy_services++))
                ;;
            "not_found")
                warning "  ? $service: not found"
                ;;
            *)
                error "  ✗ $service: $status"
                ((unhealthy_services++))
                ;;
        esac
    done

    if [[ $unhealthy_services -eq 0 ]]; then
        success "Docker services: All healthy"
        RESULTS["docker"]=healthy
    else
        error "Docker services: $unhealthy_services unhealthy"
        RESULTS["docker"]=unhealthy
    fi
}

# Function to check log files for errors
check_log_files() {
    log "Checking log files for errors..."

    local log_files=(
        "${PROJECT_ROOT}/logs/clinical_ai.log"
        "${PROJECT_ROOT}/logs/api.log"
        "${PROJECT_ROOT}/logs/error.log"
    )

    local total_errors=0

    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local recent_errors=$(tail -100 "$log_file" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l || echo "0")
            total_errors=$((total_errors + recent_errors))

            if [[ $recent_errors -gt 0 ]]; then
                warning "  $log_file: $recent_errors recent errors"
            fi
        fi
    done

    if [[ $total_errors -eq 0 ]]; then
        success "Log files: No recent errors"
        RESULTS["logs"]=healthy
    else
        warning "Log files: $total_errors recent errors"
        RESULTS["logs"]=warning
    fi
}

# Function to generate health report
generate_health_report() {
    log "Generating health report..."

    local timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local overall_status="healthy"
    local critical_issues=0
    local warning_issues=0

    # Count issues
    for status in "${RESULTS[@]}"; do
        case "$status" in
            "critical"|"unhealthy")
                ((critical_issues++))
                overall_status="unhealthy"
                ;;
            "warning")
                ((warning_issues++))
                if [[ "$overall_status" == "healthy" ]]; then
                    overall_status="degraded"
                fi
                ;;
        esac
    done

    # Generate JSON report
    cat > "$REPORT_FILE" << EOF
{
    "timestamp": "$timestamp",
    "overall_status": "$overall_status",
    "summary": {
        "critical_issues": $critical_issues,
        "warning_issues": $warning_issues,
        "total_checks": ${#RESULTS[@]}
    },
    "services": {
EOF

    # Add service statuses
    local first=true
    for service in "${!RESULTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi
        echo "        \"$service\": {\"status\": \"${RESULTS[$service]}\"}" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF
    },
    "response_times": {
EOF

    # Add response times
    first=true
    for service in "${!RESPONSE_TIMES[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi
        echo "        \"$service\": \"${RESPONSE_TIMES[$service]}\"" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF
    },
    "error_counts": {
EOF

    # Add error counts
    first=true
    for service in "${!ERROR_COUNTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi
        echo "        \"$service\": ${ERROR_COUNTS[$service]}" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF
    },
    "hostname": "$(hostname)",
    "system_info": {
        "uptime": "$(uptime -p 2>/dev/null || echo 'unknown')",
        "kernel": "$(uname -r)",
        "platform": "$(uname -s)"
    }
}
EOF

    success "Health report generated: $REPORT_FILE"
}

# Function to display summary
display_summary() {
    log "Health Check Summary"
    log "==================="

    # Overall status
    local overall_status="healthy"
    for status in "${RESULTS[@]}"; do
        if [[ "$status" == "critical" || "$status" == "unhealthy" ]]; then
            overall_status="unhealthy"
            break
        elif [[ "$status" == "warning" ]]; then
            overall_status="degraded"
        fi
    done

    case "$overall_status" in
        "healthy")
            success "Overall Status: All systems healthy"
            ;;
        "degraded")
            warning "Overall Status: Some warnings detected"
            ;;
        "unhealthy")
            error "Overall Status: Critical issues detected"
            ;;
    esac

    echo
    log "Service Status:"
    for service in "${!RESULTS[@]}"; do
        local status="${RESULTS[$service]}"
        local status_icon="✓"

        case "$status" in
            "healthy") status_icon="✓";;
            "warning") status_icon="⚠";;
            "critical"|"unhealthy") status_icon="✗";;
            "disabled") status_icon="-";;
        esac

        log "  $status_icon $service: $status"

        # Show response time if available
        if [[ -n "${RESPONSE_TIMES[$service]:-}" ]]; then
            log "    Response time: ${RESPONSE_TIMES[$service]}"
        fi

        # Show error count if available
        if [[ -n "${ERROR_COUNTS[$service]:-}" ]] && [[ "${ERROR_COUNTS[$service]}" -gt 0 ]]; then
            log "    Errors: ${ERROR_COUNTS[$service]}"
        fi
    done

    echo
    log "Report saved to: $REPORT_FILE"
    log "Log file: $LOG_FILE"
}

# Function to send alerts
send_alerts() {
    local overall_status="$1"

    # Only send alerts for critical issues
    if [[ "$overall_status" == "unhealthy" ]]; then
        # Check if we should send an alert (avoid spam)
        local alert_key_file="${PROJECT_ROOT}/.last_health_alert"
        local current_time=$(date +%s)
        local last_alert_time=0

        if [[ -f "$alert_key_file" ]]; then
            last_alert_time=$(cat "$alert_key_file")
        fi

        local time_since_last_alert=$((current_time - last_alert_time))
        local alert_interval=3600  # 1 hour

        if [[ $time_since_last_alert -gt $alert_interval ]]; then
            log "Sending health alert..."

            # Email alert (if configured)
            if command -v mail &> /dev/null && [[ -n "${HEALTH_ALERT_EMAIL:-}" ]]; then
                local subject="CRITICAL: Clinical AI System Health Alert"
                local message="Clinical AI Assistant system health check has detected critical issues.

Overall Status: UNHEALTHY
Time: $(date)
Hostname: $(hostname)

Please check the system immediately.
Report: $REPORT_FILE"

                echo "$message" | mail -s "$subject" "$HEALTH_ALERT_EMAIL"
                log "Alert email sent to $HEALTH_ALERT_EMAIL"
            fi

            # Slack alert (if configured)
            if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
                curl -X POST -H 'Content-type: application/json' \
                    --data "{\"text\":\"🚨 CRITICAL: Clinical AI System Health Alert\n\nOverall Status: UNHEALTHY\nTime: $(date)\nHostname: $(hostname)\n\nPlease check the system immediately.\nReport: $REPORT_FILE\"}" \
                    "$SLACK_WEBHOOK_URL" 2>/dev/null || true

                log "Slack alert sent"
            fi

            # Update last alert time
            echo "$current_time" > "$alert_key_file"
        fi
    fi
}

# Function to show usage
show_usage() {
    echo "Clinical AI Assistant - Health Check Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -q, --quiet          Suppress output, only log to file"
    echo "  -j, --json           Output results in JSON format"
    echo "  -w, --webhook URL    Send results to webhook URL"
    echo "  --api-url URL        Custom API URL (default: http://localhost:8000)"
    echo "  --report-only        Generate report without new checks"
    echo "  --continuous         Run health checks continuously (every 60s)"
    echo
    echo "Environment Variables:"
    echo "  HEALTH_ALERT_EMAIL    Email for health alerts"
    echo "  SLACK_WEBHOOK_URL    Slack webhook for alerts"
    echo "  ALERT_THRESHOLD      Failure threshold before alerting (default: 3)"
    echo
    echo "Examples:"
    echo "  $0                    # Run health check"
    echo "  $0 --json            # Output in JSON format"
    echo "  $0 --continuous      # Run continuously"
}

# Main execution function
main() {
    local quiet=false
    local json_output=false
    local webhook_url=""
    local report_only=false
    local continuous=false

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
            -w|--webhook)
                webhook_url="$2"
                shift 2
                ;;
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --report-only)
                report_only=true
                shift
                ;;
            --continuous)
                continuous=true
                shift
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

    # Continuous mode
    if [[ "$continuous" == "true" ]]; then
        log "Starting continuous health monitoring..."
        while true; do
            main --quiet
            sleep 60
        done
        exit 0
    fi

    # Redirect output if quiet mode
    if [[ "$quiet" == "true" ]]; then
        exec 1>>"$LOG_FILE" 2>&1
    fi

    if [[ "$report_only" == "false" ]]; then
        log "Starting Clinical AI Assistant health check..."

        # Run all health checks
        check_api_service
        check_database
        check_redis
        check_ollama
        check_system_resources
        check_docker_services
        check_log_files
    fi

    # Generate report and summary
    generate_health_report

    if [[ "$quiet" == "false" ]]; then
        display_summary
    fi

    # Determine overall status
    local overall_status="healthy"
    for status in "${RESULTS[@]}"; do
        if [[ "$status" == "critical" || "$status" == "unhealthy" ]]; then
            overall_status="unhealthy"
            break
        elif [[ "$status" == "warning" ]]; then
            overall_status="degraded"
        fi
    done

    # Send alerts if needed
    send_alerts "$overall_status"

    # Send webhook if configured
    if [[ -n "$webhook_url" ]]; then
        log "Sending results to webhook: $webhook_url"
        curl -X POST -H 'Content-type: application/json' \
            -d "@$REPORT_FILE" \
            "$webhook_url" 2>/dev/null || true
    fi

    # JSON output if requested
    if [[ "$json_output" == "true" ]]; then
        cat "$REPORT_FILE"
    fi

    # Exit with appropriate code
    case "$overall_status" in
        "healthy")
            exit 0
            ;;
        "degraded")
            exit 1
            ;;
        "unhealthy")
            exit 2
            ;;
    esac
}

# Execute main function
main "$@"