#!/bin/bash
# Clinical AI Assistant - Ollama Model Installation Script
# Downloads and configures local AI models for offline use

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
LOG_FILE="${PROJECT_ROOT}/logs/ollama-install.log"

# Models to install for clinical use
CLINICAL_MODELS=(
    "gemma:7b"           # Google's Gemma 7B - Good general reasoning
    "llama2:7b"          # Meta's Llama 2 7B - Strong clinical reasoning
    "mistral:7b"         # Mistral 7B - Fast and efficient
    "qwen:7b"            # Qwen 7B - Multilingual support including Turkish
)

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

# Function to check Ollama connectivity
check_ollama_connectivity() {
    log "Checking Ollama connectivity..."

    if ! curl -f -s "$OLLAMA_BASE_URL/api/tags" > /dev/null; then
        error "Cannot connect to Ollama at $OLLAMA_BASE_URL. Please ensure Ollama is running."
    fi

    success "Ollama is accessible at $OLLAMA_BASE_URL"
}

# Function to check available disk space
check_disk_space() {
    log "Checking available disk space..."

    local available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    local required_space=10  # Minimum 10GB required

    if [[ $available_space -lt $required_space ]]; then
        error "Insufficient disk space. Required: ${required_space}GB, Available: ${available_space}GB"
    fi

    success "Sufficient disk space available (${available_space}GB)"
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."

    # Check available memory
    local total_memory=$(free -g | awk 'NR==2{print $2}')
    local required_memory=8  # Minimum 8GB RAM recommended

    if [[ $total_memory -lt $required_memory ]]; then
        warning "System has less than ${required_memory}GB RAM (${total_memory}GB). Performance may be degraded."
    fi

    # Check CPU cores
    local cpu_cores=$(nproc)
    if [[ $cpu_cores -lt 4 ]]; then
        warning "System has fewer than 4 CPU cores (${cpu_cores} cores). Performance may be degraded."
    fi

    success "System requirements check completed"
}

# Function to download a single model
download_model() {
    local model="$1"
    log "Downloading model: $model"

    # Start download with progress tracking
    local start_time=$(date +%s)

    if curl -f -s -X POST "$OLLAMA_BASE_URL/api/pull" -d "{\"name\": \"$model\"}" | tee -a "$LOG_FILE"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        success "Model $model downloaded successfully in ${duration}s"
    else
        error "Failed to download model $model"
    fi
}

# Function to verify model installation
verify_model() {
    local model="$1"
    log "Verifying model installation: $model"

    # Check if model appears in installed models list
    if curl -f -s "$OLLAMA_BASE_URL/api/tags" | grep -q "\"name\": \"$model\""; then
        success "Model $model is installed and accessible"
    else
        error "Model $model verification failed"
    fi
}

# Function to test model functionality
test_model() {
    local model="$1"
    log "Testing model functionality: $model"

    # Simple test prompt
    local test_prompt="What is the capital of Turkey?"

    local response=$(curl -f -s -X POST "$OLLAMA_BASE_URL/api/generate" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$model\", \"prompt\": \"$test_prompt\", \"stream\": false}" \
        | jq -r '.response' 2>/dev/null)

    if [[ -n "$response" ]] && [[ "$response" != "null" ]]; then
        success "Model $model is responding correctly"
    else
        warning "Model $model test failed - may need additional configuration"
    fi
}

# Function to install all models
install_models() {
    log "Starting model installation process..."
    log "Models to install: ${CLINICAL_MODELS[*]}"

    local total_models=${#CLINICAL_MODELS[@]}
    local installed_count=0

    for model in "${CLINICAL_MODELS[@]}"; do
        echo
        log "Processing model $((installed_count + 1))/$total_models: $model"

        # Check if model already exists
        if curl -f -s "$OLLAMA_BASE_URL/api/tags" | grep -q "\"name\": \"$model\""; then
            log "Model $model is already installed"
            verify_model "$model"
            ((installed_count++))
            continue
        fi

        # Download model
        download_model "$model"

        # Verify installation
        verify_model "$model"

        # Test functionality
        test_model "$model"

        ((installed_count++))

        # Brief pause between models
        sleep 2
    done

    echo
    success "Model installation completed: $installed_count/$total_models models installed"
}

# Function to display installed models
display_installed_models() {
    log "Installed Models:"
    echo

    if curl -f -s "$OLLAMA_BASE_URL/api/tags" | jq -r '.models[] | "  • \(.name) (\(.size // "Unknown size"))"' 2>/dev/null; then
        echo
    else
        warning "Could not retrieve model list. API response:"
        curl -s "$OLLAMA_BASE_URL/api/tags" | tee -a "$LOG_FILE"
        echo
    fi
}

# Function to show model information
show_model_info() {
    local model="$1"
    log "Model information for: $model"

    if curl -f -s "$OLLAMA_BASE_URL/api/show" -d "{\"name\": \"$model\"}" | jq '.' 2>/dev/null; then
        echo
    else
        warning "Could not retrieve detailed information for $model"
    fi
}

# Function to cleanup old models
cleanup_old_models() {
    log "Cleaning up old models..."

    # Get list of installed models
    local installed_models=$(curl -s "$OLLAMA_BASE_URL/api/tags" | jq -r '.models[].name' 2>/dev/null || true)

    if [[ -z "$installed_models" ]]; then
        log "No models found to cleanup"
        return
    fi

    # Remove models not in our clinical list
    while IFS= read -r model; do
        if [[ ! " ${CLINICAL_MODELS[*]} " =~ " ${model} " ]]; then
            log "Removing old model: $model"
            curl -f -s -X DELETE "$OLLAMA_BASE_URL/api/delete" -d "{\"name\": \"$model\"}" || warning "Failed to remove model $model"
        fi
    done <<< "$installed_models"

    success "Cleanup completed"
}

# Function to generate model configuration
generate_model_config() {
    log "Generating model configuration..."

    local config_file="${PROJECT_ROOT}/config/ollama-models.json"
    mkdir -p "$(dirname "$config_file")"

    cat > "$config_file" << EOF
{
    "installed_models": [
EOF

    local first=true
    for model in "${CLINICAL_MODELS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$config_file"
        fi

        echo "        \"$model\"" >> "$config_file"
    done

    cat >> "$config_file" << EOF
    ],
    "default_model": "gemma:7b",
    "fallback_model": "mistral:7b",
    "clinical_models": {
        "general": "gemma:7b",
        "reasoning": "llama2:7b",
        "multilingual": "qwen:7b",
        "fast": "mistral:7b"
    },
    "installation_date": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
    "ollama_base_url": "$OLLAMA_BASE_URL"
}
EOF

    success "Model configuration saved to $config_file"
}

# Function to display usage information
show_usage() {
    echo "Clinical AI Assistant - Ollama Model Installation Script"
    echo
    echo "Usage: $0 [options] [model]"
    echo
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -c, --check         Check Ollama connectivity only"
    echo "  -l, --list          List installed models"
    echo "  -i, --info MODEL    Show information about a specific model"
    echo "  -t, --test MODEL    Test a specific model"
    echo "  --cleanup           Remove old models not in clinical list"
    echo "  --config-only       Generate configuration only"
    echo
    echo "Examples:"
    echo "  $0                           # Install all clinical models"
    echo "  $0 --check                   # Check Ollama connectivity"
    echo "  $0 --list                    # List installed models"
    echo "  $0 --info gemma:7b           # Show model information"
    echo "  $0 --test llama2:7b          # Test specific model"
    echo "  $0 --cleanup                 # Clean up old models"
    echo
    echo "Environment Variables:"
    echo "  OLLAMA_BASE_URL    Ollama server URL (default: http://localhost:11434)"
}

# Main execution function
main() {
    local action="${1:-install}"
    local target_model="${2:-}"

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    case "$action" in
        "install"|"")
            check_ollama_connectivity
            check_system_requirements
            check_disk_space
            install_models
            cleanup_old_models
            display_installed_models
            generate_model_config
            success "Ollama model installation completed successfully!"
            ;;
        "check"|"-c"|"--check")
            check_ollama_connectivity
            ;;
        "list"|"-l"|"--list")
            check_ollama_connectivity
            display_installed_models
            ;;
        "info"|"-i"|"--info")
            if [[ -z "$target_model" ]]; then
                error "Model name is required for info command"
            fi
            check_ollama_connectivity
            show_model_info "$target_model"
            ;;
        "test"|"-t"|"--test")
            if [[ -z "$target_model" ]]; then
                error "Model name is required for test command"
            fi
            check_ollama_connectivity
            test_model "$target_model"
            ;;
        "cleanup"|"--cleanup")
            check_ollama_connectivity
            cleanup_old_models
            ;;
        "config-only"|"--config-only")
            generate_model_config
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            error "Unknown action: $action. Use --help for usage information."
            ;;
    esac
}

# Execute main function with all arguments
main "$@"