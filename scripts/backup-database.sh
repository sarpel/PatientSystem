#!/bin/bash
# Clinical AI Assistant - Database Backup Script
# Automated database backup with compression, encryption, and retention management

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${PROJECT_ROOT}/logs/backup.log"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-90}
ENCRYPT_BACKUP=${ENCRYPT_BACKUP:-true}
COMPRESSION_LEVEL=${COMPRESSION_LEVEL:-6}

# Database Configuration
DB_SERVER="localhost"
DB_NAME="ClinicalAI"
DB_USER="sa"
DB_PASSWORD="StrongPassword123!"

# Encryption Configuration
ENCRYPTION_KEY_FILE="${PROJECT_ROOT}/.backup_key"
GPG_RECIPIENT=${GPG_RECIPIENT:-""}

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

# Function to create backup directory
create_backup_directory() {
    local backup_date=$(date +%Y%m%d)
    local backup_path="${BACKUP_DIR}/${backup_date}"

    mkdir -p "$backup_path"
    echo "$backup_path"
}

# Function to check database connectivity
check_database_connectivity() {
    log "Checking database connectivity..."

    if ! docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$DB_PASSWORD" -Q "SELECT 1" > /dev/null; then
        error "Cannot connect to database. Please check if database is running."
    fi

    success "Database connectivity verified"
}

# Function to generate backup filename
generate_backup_filename() {
    local backup_type="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${DB_NAME}_${backup_type}_${timestamp}.bak"
}

# Function to create full database backup
create_full_backup() {
    local backup_path="$1"
    local backup_file=$(generate_backup_filename "full")
    local backup_file_path="${backup_path}/${backup_file}"

    log "Creating full database backup: $backup_file"

    # Execute backup command
    local backup_sql="BACKUP DATABASE [${DB_NAME}] TO DISK = '/var/opt/mssql/backup/${backup_file}' WITH FORMAT, COMPRESSION, STATS = 5, CHECKSUM;"

    if docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$DB_PASSWORD" -Q "$backup_sql"; then
        log "Full database backup completed: $backup_file"

        # Copy backup from container to host
        docker cp "clinical-ai-db:/var/opt/mssql/backup/${backup_file}" "$backup_file_path"

        echo "$backup_file_path"
    else
        error "Failed to create full database backup"
    fi
}

# Function to create transaction log backup
create_log_backup() {
    local backup_path="$1"
    local backup_file=$(generate_backup_filename "log")
    local backup_file_path="${backup_path}/${backup_file}"

    log "Creating transaction log backup: $backup_file"

    # Execute log backup command
    local backup_sql="BACKUP LOG [${DB_NAME}] TO DISK = '/var/opt/mssql/backup/${backup_file}' WITH COMPRESSION, STATS = 5;"

    if docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$DB_PASSWORD" -Q "$backup_sql"; then
        log "Transaction log backup completed: $backup_file"

        # Copy backup from container to host
        docker cp "clinical-ai-db:/var/opt/mssql/backup/${backup_file}" "$backup_file_path"

        echo "$backup_file_path"
    else
        warning "Failed to create transaction log backup (database might be in SIMPLE recovery mode)"
    fi
}

# Function to create differential backup
create_differential_backup() {
    local backup_path="$1"
    local backup_file=$(generate_backup_filename "diff")
    local backup_file_path="${backup_path}/${backup_file}"

    log "Creating differential backup: $backup_file"

    # Execute differential backup command
    local backup_sql="BACKUP DATABASE [${DB_NAME}] TO DISK = '/var/opt/mssql/backup/${backup_file}' WITH DIFFERENTIAL, COMPRESSION, STATS = 5, CHECKSUM;"

    if docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$DB_PASSWORD" -Q "$backup_sql"; then
        log "Differential backup completed: $backup_file"

        # Copy backup from container to host
        docker cp "clinical-ai-db:/var/opt/mssql/backup/${backup_file}" "$backup_file_path"

        echo "$backup_file_path"
    else
        error "Failed to create differential backup"
    fi
}

# Function to compress backup file
compress_backup() {
    local backup_file="$1"
    local compressed_file="${backup_file}.gz"

    log "Compressing backup file..."

    if gzip -c "$backup_file" > "$compressed_file"; then
        local original_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file")
        local compressed_size=$(stat -f%z "$compressed_file" 2>/dev/null || stat -c%s "$compressed_file")
        local compression_ratio=$(echo "scale=2; (1 - $compressed_size / $original_size) * 100" | bc -l)

        success "Backup compressed. Size reduced by ${compression_ratio}%"

        # Remove original uncompressed file
        rm "$backup_file"

        echo "$compressed_file"
    else
        error "Failed to compress backup file"
    fi
}

# Function to encrypt backup file
encrypt_backup() {
    local backup_file="$1"

    if [[ "$ENCRYPT_BACKUP" != "true" ]]; then
        echo "$backup_file"
        return
    fi

    log "Encrypting backup file..."

    local encrypted_file="${backup_file}.gpg"

    if [[ -n "$GPG_RECIPIENT" ]]; then
        # Encrypt for specific recipient
        if gpg --trust-model always --encrypt -r "$GPG_RECIPIENT" --output "$encrypted_file" "$backup_file"; then
            success "Backup encrypted for recipient: $GPG_RECIPIENT"
            rm "$backup_file"
            echo "$encrypted_file"
        else
            error "Failed to encrypt backup for recipient"
        fi
    elif [[ -f "$ENCRYPTION_KEY_FILE" ]]; then
        # Encrypt with symmetric key
        if gpg --batch --yes --passphrase-file "$ENCRYPTION_KEY_FILE" --symmetric --cipher-algo AES256 --output "$encrypted_file" "$backup_file"; then
            success "Backup encrypted with symmetric key"
            rm "$backup_file"
            echo "$encrypted_file"
        else
            error "Failed to encrypt backup with symmetric key"
        fi
    else
        warning "Encryption key not found, skipping encryption"
        echo "$backup_file"
    fi
}

# Function to verify backup integrity
verify_backup() {
    local backup_file="$1"

    log "Verifying backup integrity..."

    if [[ "$backup_file" == *.gpg ]]; then
        # Verify encrypted backup
        if gpg --list-packets "$backup_file" > /dev/null 2>&1; then
            success "Encrypted backup verification passed"
        else
            error "Encrypted backup verification failed"
        fi
    elif [[ "$backup_file" == *.gz ]]; then
        # Verify compressed backup
        if gzip -t "$backup_file" 2>/dev/null; then
            success "Compressed backup verification passed"
        else
            error "Compressed backup verification failed"
        fi
    else
        # Verify plain backup (basic check)
        if [[ -f "$backup_file" ]] && [[ -s "$backup_file" ]]; then
            success "Backup file exists and is not empty"
        else
            error "Backup file verification failed"
        fi
    fi
}

# Function to create backup metadata
create_backup_metadata() {
    local backup_file="$1"
    local backup_type="$2"
    local metadata_file="${backup_file}.meta"

    log "Creating backup metadata..."

    local backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file")
    local backup_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local database_size=$(docker-compose exec -T db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$DB_PASSWORD" -Q "SELECT SUM(size * 8.0 / 1024) FROM sys.master_files WHERE database_id = DB_ID('${DB_NAME}')" -h -1 | tr -d ' ')

    cat > "$metadata_file" << EOF
{
    "backup_file": "$(basename "$backup_file")",
    "backup_type": "$backup_type",
    "backup_date": "$backup_date",
    "backup_size_bytes": $backup_size,
    "database_name": "$DB_NAME",
    "database_size_mb": $database_size,
    "compression_enabled": $([[ "$backup_file" == *.gz ]] && echo "true" || echo "false"),
    "encryption_enabled": $([[ "$backup_file" == *.gpg ]] && echo "true" || echo "false"),
    "script_version": "1.0",
    "hostname": "$(hostname)",
    "user": "$(whoami)"
}
EOF

    success "Backup metadata created: $(basename "$metadata_file")"
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."

    local deleted_count=0
    local total_freed_space=0

    # Find and remove old backup directories
    while IFS= read -r backup_dir; do
        if [[ -d "$backup_dir" ]]; then
            local dir_size=$(du -sb "$backup_dir" | cut -f1)
            rm -rf "$backup_dir"
            ((deleted_count++))
            ((total_freed_space += dir_size))

            log "Removed old backup directory: $(basename "$backup_dir")"
        fi
    done < <(find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" -mtime +$RETENTION_DAYS)

    if [[ $deleted_count -gt 0 ]]; then
        local freed_mb=$((total_freed_space / 1024 / 1024))
        success "Cleanup completed. Removed $deleted_count old backup directories, freed ${freed_mb}MB"
    else
        log "No old backups found for cleanup"
    fi
}

# Function to create backup summary report
create_backup_report() {
    local backup_file="$1"
    local backup_type="$2"
    local report_file="${PROJECT_ROOT}/logs/backup_report_$(date +%Y%m%d).log"

    log "Creating backup summary report..."

    {
        echo "=== Clinical AI Assistant - Database Backup Report ==="
        echo "Backup Date: $(date)"
        echo "Backup Type: $backup_type"
        echo "Backup File: $(basename "$backup_file")"
        echo "Backup Size: $(du -h "$backup_file" | cut -f1)"
        echo "Database: $DB_NAME"
        echo "Server: $DB_SERVER"
        echo "Hostname: $(hostname)"
        echo "User: $(whoami)"
        echo "Retention Period: $RETENTION_DAYS days"
        echo "Encryption: $ENCRYPT_BACKUP"
        echo "Compression: Enabled (level $COMPRESSION_LEVEL)"
        echo ""
        echo "Backup Location: $(dirname "$backup_file")"
        echo "Metadata File: $(basename "$backup_file").meta"
        echo ""
        echo "=== Disk Usage ==="
        df -h "$BACKUP_DIR"
        echo ""
        echo "=== Recent Backups ==="
        ls -la "$BACKUP_DIR" | tail -10
        echo ""
        echo "Report generated at: $(date)"
        echo "======================================"
    } >> "$report_file"

    success "Backup report created: $report_file"
}

# Function to send notification
send_notification() {
    local status="$1"
    local backup_file="$2"
    local backup_type="$3"

    # Email notification (if configured)
    if command -v mail &> /dev/null && [[ -n "${BACKUP_NOTIFICATION_EMAIL:-}" ]]; then
        local subject="Clinical AI Database Backup ${status^}: $backup_type"
        local message="Backup $status for Clinical AI database.

Details:
- Type: $backup_type
- File: $(basename "$backup_file")
- Size: $(du -h "$backup_file" | cut -f1)
- Date: $(date)
- Server: $(hostname)

This is an automated message from the Clinical AI Assistant backup system."

        echo "$message" | mail -s "$subject" "$BACKUP_NOTIFICATION_EMAIL"
        log "Notification email sent to $BACKUP_NOTIFICATION_EMAIL"
    fi

    # Slack notification (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        local color="good"
        [[ "$status" == "failed" ]] && color="danger"

        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Clinical AI Database Backup ${status^}\",\"attachments\":[{\"color\":\"$color\",\"fields\":[{\"title\":\"Type\",\"value\":\"$backup_type\",\"short\":true},{\"title\":\"File\",\"value\":\"$(basename "$backup_file")\",\"short\":true},{\"title\":\"Size\",\"value\":\"$(du -h "$backup_file" | cut -f1)\",\"short\":true},{\"title\":\"Server\",\"value\":\"$(hostname)\",\"short\":true}]}]}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true

        log "Slack notification sent"
    fi
}

# Function to show usage
show_usage() {
    echo "Clinical AI Assistant - Database Backup Script"
    echo
    echo "Usage: $0 [options] [backup_type]"
    echo
    echo "Backup Types:"
    echo "  full         Full database backup (default)"
    echo "  differential Differential backup"
    echo "  log          Transaction log backup"
    echo
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -c, --cleanup-only   Only cleanup old backups"
    echo "  -v, --verify-only    Only verify existing backups"
    echo "  -l, --list           List available backups"
    echo "  --no-encrypt         Skip encryption"
    echo "  --no-compress        Skip compression"
    echo
    echo "Environment Variables:"
    echo "  BACKUP_RETENTION_DAYS    Backup retention period in days (default: 90)"
    echo "  ENCRYPT_BACKUP          Enable encryption (default: true)"
    echo "  COMPRESSION_LEVEL       Compression level 1-9 (default: 6)"
    echo "  GPG_RECIPIENT           GPG recipient for encryption"
    echo "  BACKUP_NOTIFICATION_EMAIL Email for notifications"
    echo "  SLACK_WEBHOOK_URL      Slack webhook for notifications"
    echo
    echo "Examples:"
    echo "  $0                    # Create full backup with default settings"
    echo "  $0 differential       # Create differential backup"
    echo "  $0 --no-encrypt log   # Create log backup without encryption"
    echo "  $0 --cleanup-only     # Only cleanup old backups"
}

# Main execution function
main() {
    local backup_type="${1:-full}"
    local action="${1:-backup}"

    # Create required directories
    mkdir -p "$BACKUP_DIR" "${PROJECT_ROOT}/logs"

    case "$action" in
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        "cleanup"|"-c"|"--cleanup-only")
            cleanup_old_backups
            exit 0
            ;;
        "verify"|"-v"|"--verify-only")
            # Verify all recent backups
            log "Verifying recent backups..."
            find "$BACKUP_DIR" -name "*.bak*" -mtime -7 | while read -r backup_file; do
                verify_backup "$backup_file"
            done
            success "Backup verification completed"
            exit 0
            ;;
        "list"|"-l"|"--list")
            echo "Available Backups:"
            echo "=================="
            find "$BACKUP_DIR" -name "*.bak*" -exec ls -lh {} \; | sort -k6,7
            exit 0
            ;;
        "--no-encrypt")
            ENCRYPT_BACKUP=false
            shift
            backup_type="${1:-full}"
            ;;
        "--no-compress")
            COMPRESSION_LEVEL=0
            shift
            backup_type="${1:-full}"
            ;;
        "full"|"differential"|"log"|"")
            # Continue with backup process
            ;;
        *)
            error "Unknown backup type: $action. Use --help for usage information."
            ;;
    esac

    log "Starting Clinical AI Assistant database backup..."
    log "Backup type: ${backup_type:-full}"
    log "Retention period: $RETENTION_DAYS days"
    log "Encryption: $ENCRYPT_BACKUP"
    log "Compression level: $COMPRESSION_LEVEL"

    # Execute backup process
    check_database_connectivity

    local backup_path
    backup_path=$(create_backup_directory)

    local backup_file
    case "$backup_type" in
        "full")
            backup_file=$(create_full_backup "$backup_path")
            ;;
        "differential")
            backup_file=$(create_differential_backup "$backup_path")
            ;;
        "log")
            backup_file=$(create_log_backup "$backup_path")
            ;;
        "")
            backup_file=$(create_full_backup "$backup_path")
            ;;
        *)
            error "Unknown backup type: $backup_type"
            ;;
    esac

    # Process backup file
    if [[ $COMPRESSION_LEVEL -gt 0 ]]; then
        backup_file=$(compress_backup "$backup_file")
    fi

    backup_file=$(encrypt_backup "$backup_file")
    verify_backup "$backup_file"
    create_backup_metadata "$backup_file" "$backup_type"
    create_backup_report "$backup_file" "$backup_type"

    # Cleanup old backups
    cleanup_old_backups

    success "Database backup completed successfully!"
    success "Backup file: $backup_file"

    # Send notification
    send_notification "completed" "$backup_file" "$backup_type"
}

# Execute main function with error handling
if ! main "$@"; then
    send_notification "failed" "" "${1:-full}"
    error "Backup process failed. Check logs for details."
fi