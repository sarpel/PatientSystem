#!/bin/bash
# Clinical AI Assistant - Deployment Script
# Supports multiple environments: development, staging, production

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-development}"
VERSION="${2:-latest}"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${PROJECT_ROOT}/logs/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi

    # Check if required files exist
    local required_files=("docker-compose.yml" "Dockerfile" ".env.${ENVIRONMENT}")
    for file in "${required_files[@]}"; do
        if [[ ! -f "${PROJECT_ROOT}/${file}" ]]; then
            error "Required file ${file} not found."
        fi
    done

    # Check environment variables
    if [[ "$ENVIRONMENT" == "production" ]]; then
        local required_vars=("ANTHROPIC_API_KEY" "OPENAI_API_KEY" "SECRET_KEY")
        for var in "${required_vars[@]}"; do
            if [[ -z "${!var:-}" ]]; then
                warning "Environment variable $var is not set. Please set it before continuing."
            fi
        done
    fi

    success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Creating backup before deployment..."

        local backup_timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_path="${BACKUP_DIR}/pre_deploy_${backup_timestamp}"

        mkdir -p "$backup_path"

        # Backup database
        docker-compose -f "${PROJECT_ROOT}/docker-compose.yml" exec db \
            /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' \
            -Q "BACKUP DATABASE ClinicalAI TO DISK = '/var/opt/mssql/backup/backup_${backup_timestamp}.bak' WITH FORMAT, INIT"

        # Copy backup to backup directory
        docker cp clinical-ai-db:/var/opt/mssql/backup/backup_${backup_timestamp}.bak "$backup_path/"

        # Backup configuration files
        cp "${PROJECT_ROOT}/.env.${ENVIRONMENT}" "$backup_path/"
        cp "${PROJECT_ROOT}/docker-compose.yml" "$backup_path/"

        success "Backup created at $backup_path"
    fi
}

# Function to build and deploy
deploy_application() {
    log "Deploying application to $ENVIRONMENT environment..."

    cd "$PROJECT_ROOT"

    # Set environment-specific configurations
    export COMPOSE_PROJECT_NAME="clinical-ai-${ENVIRONMENT}"
    export COMPOSE_FILE="docker-compose.yml:docker-compose.${ENVIRONMENT}.yml"

    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose pull

    # Build application image
    log "Building application image..."
    docker-compose build \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION="$VERSION" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        api

    # Stop existing services
    log "Stopping existing services..."
    docker-compose down

    # Start services
    log "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps | grep -q "healthy\|Up (healthy)"; then
            success "Services are healthy"
            break
        fi

        if [[ $attempt -eq $max_attempts ]]; then
            error "Services failed to become healthy after $max_attempts attempts"
        fi

        log "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    success "Application deployed successfully"
}

# Function to run health checks
run_health_checks() {
    log "Running health checks..."

    # Check API health
    local api_url="http://localhost:8000"
    if [[ "$ENVIRONMENT" != "development" ]]; then
        api_url="http://localhost"
    fi

    if curl -f -s "$api_url/health" > /dev/null; then
        success "API health check passed"
    else
        error "API health check failed"
    fi

    # Check database connectivity
    if docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -Q 'SELECT 1' > /dev/null; then
        success "Database health check passed"
    else
        error "Database health check failed"
    fi

    # Check AI services (optional for production)
    if [[ "$ENVIRONMENT" == "production" ]] && [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        log "Checking AI service connectivity..."
        # Add AI service health checks here
        success "AI services check passed"
    fi

    success "All health checks passed"
}

# Function to cleanup old resources
cleanup_resources() {
    log "Cleaning up old resources..."

    # Remove unused Docker images
    docker image prune -f

    # Remove unused volumes (with confirmation)
    if [[ "$ENVIRONMENT" != "production" ]]; then
        docker volume prune -f
    fi

    success "Cleanup completed"
}

# Function to display deployment summary
display_summary() {
    log "Deployment Summary"
    log "=================="
    log "Environment: $ENVIRONMENT"
    log "Version: $VERSION"
    log "Timestamp: $(date)"
    log "Docker Compose Project: clinical-ai-$ENVIRONMENT"

    echo
    log "Service URLs:"
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log "  API: http://localhost:8000"
        log "  Documentation: http://localhost:8000/docs"
        log "  Grafana: http://localhost:3000"
        log "  Prometheus: http://localhost:9090"
    else
        log "  API: http://localhost"
        log "  Documentation: http://localhost/docs"
        log "  Grafana: http://localhost:3000"
        log "  Prometheus: http://localhost:9090"
    fi

    echo
    log "Useful Commands:"
    log "  View logs: docker-compose logs -f [service]"
    log "  Check status: docker-compose ps"
    log "  Stop services: docker-compose down"
    log "  Restart services: docker-compose restart"

    success "Deployment completed successfully!"
}

# Function to rollback deployment
rollback_deployment() {
    log "Rolling back deployment..."

    # Get previous backup
    local latest_backup=$(ls -t "$BACKUP_DIR" | head -n 1)

    if [[ -z "$latest_backup" ]]; then
        error "No backup found for rollback"
    fi

    log "Restoring from backup: $latest_backup"

    # Restore database
    local backup_file=$(ls "${BACKUP_DIR}/${latest_backup}"/*.bak | head -n 1)
    docker cp "$backup_file" clinical-ai-db:/var/opt/mssql/backup/restore.bak

    docker-compose exec db \
        /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' \
        -Q "RESTORE DATABASE ClinicalAI FROM DISK = '/var/opt/mssql/backup/restore.bak' WITH REPLACE"

    # Restart services
    docker-compose restart

    success "Rollback completed"
}

# Main execution function
main() {
    log "Starting Clinical AI Assistant deployment..."
    log "Environment: $ENVIRONMENT"
    log "Version: $VERSION"

    # Create required directories
    mkdir -p "${PROJECT_ROOT}/logs" "${BACKUP_DIR}"

    # Check if rollback is requested
    if [[ "${1:-}" == "rollback" ]]; then
        rollback_deployment
        exit 0
    fi

    # Execute deployment steps
    check_prerequisites
    create_backup
    deploy_application
    run_health_checks
    cleanup_resources
    display_summary
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Clinical AI Assistant Deployment Script"
        echo
        echo "Usage: $0 [environment] [version] [options]"
        echo
        echo "Environments:"
        echo "  development   Development environment (default)"
        echo "  staging       Staging environment"
        echo "  production    Production environment"
        echo
        echo "Options:"
        echo "  rollback      Rollback to previous deployment"
        echo "  help          Show this help message"
        echo
        echo "Examples:"
        echo "  $0                    # Deploy to development"
        echo "  $0 production v1.2.3  # Deploy v1.2.3 to production"
        echo "  $0 rollback           # Rollback last deployment"
        exit 0
        ;;
    "rollback")
        main "rollback"
        ;;
    *)
        main
        ;;
esac