# ATN Project Deployment Script
# Deploys to Railway or DigitalOcean

set -e

echo "🚀 ATN Project Deployment Script"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="atn-project"
BOT_DIR="src/bot"
CONTRACTS_DIR="src/contracts"
API_DIR="src/api"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed"
        exit 1
    fi
    
    log_info "All prerequisites met ✓"
}

# Deploy Telegram Bot
deploy_bot() {
    log_info "Deploying Telegram Bot..."
    
    cd $BOT_DIR
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create environment file if not exists
    if [ ! -f ".env" ]; then
        log_warn "Creating .env from template..."
        cat > .env << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
DATABASE_URL=sqlite:///atn.db
CONTRACT_ADDRESS=${CONTRACT_ADDRESS}
RPC_URL=${RPC_URL}
ADMIN_IDS=${ADMIN_IDS}
EOF
    fi
    
    # Test run (optional)
    # python3 -c "import main; print('Bot module OK')"
    
    log_info "Bot deployment complete ✓"
    cd ../..
}

# Deploy Smart Contracts
deploy_contracts() {
    log_info "Deploying Smart Contracts..."
    
    cd $CONTRACTS_DIR
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Compile contracts
    log_info "Compiling contracts..."
    npx hardhat compile
    
    # Deploy to network (default: hardhat local network)
    log_info "Deploying contracts..."
    npx hardhat run scripts/deploy.js --network ${NETWORK:-hardhat}
    
    log_info "Contract deployment complete ✓"
    cd ../..
}

# Deploy API
deploy_api() {
    log_info "Deploying API..."
    
    cd $API_DIR
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create environment file if not exists
    if [ ! -f ".env" ]; then
        log_warn "Creating .env from template..."
        cat > .env << EOF
DATABASE_URL=${DATABASE_URL:-sqlite:///atn.db}
CONTRACT_ADDRESS=${CONTRACT_ADDRESS}
RPC_URL=${RPC_URL}
API_PORT=${API_PORT:-8000}
EOF
    fi
    
    log_info "API deployment complete ✓"
    cd ../..
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."
    
    cd frontend
    npm install
    npm run build
    
    log_info "Frontend build complete ✓"
    cd ..
}

# Start all services
start_all() {
    log_info "Starting all services..."
    
    # Start Bot
    cd $BOT_DIR
    python3 main.py &
    BOT_PID=$!
    cd ../..
    
    # Start API
    cd $API_DIR
    python3 main.py &
    API_PID=$!
    cd ../..
    
    log_info "All services started"
    log_info "Bot PID: $BOT_PID"
    log_info "API PID: $API_PID"
    
    # Wait for processes
    wait
}

# Stop all services
stop_all() {
    log_info "Stopping all services..."
    
    pkill -f "python3.*main.py" || true
    
    log_info "All services stopped ✓"
}

# Show status
status() {
    echo "================================"
    echo "Service Status"
    echo "================================"
    
    echo -e "\n🤖 Telegram Bot:"
    if pgrep -f "src.bot.main" > /dev/null; then
        echo -e "   Status: Running ✓"
        ps aux | grep "src.bot.main" | grep -v grep
    else
        echo -e "   Status: Stopped ✗"
    fi
    
    echo -e "\n🌐 API Server:"
    if pgrep -f "src.api.main" > /dev/null; then
        echo -e "   Status: Running ✓"
        ps aux | grep "src.api.main" | grep -v grep
    else
        echo -e "   Status: Stopped ✗"
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  all         Deploy all components"
    echo "  bot         Deploy Telegram Bot"
    echo "  contracts   Deploy Smart Contracts"
    echo "  api         Deploy API Server"
    echo "  frontend    Build frontend"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  status      Show service status"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  TELEGRAM_BOT_TOKEN  - Telegram Bot API Token"
    echo "  DATABASE_URL       - Database connection string"
    echo "  CONTRACT_ADDRESS   - Deployed contract address"
    echo "  RPC_URL            - Blockchain RPC URL"
    echo "  NETWORK            - Network to deploy contracts (default: hardhat)"
}

# Main script
case "${1:-help}" in
    all)
        check_prerequisites
        deploy_bot
        deploy_contracts
        deploy_api
        ;;
    bot)
        check_prerequisites
        deploy_bot
        ;;
    contracts)
        deploy_contracts
        ;;
    api)
        deploy_api
        ;;
    frontend)
        build_frontend
        ;;
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac

echo ""
log_info "Done!"
