#!/bin/bash
# ATN Project Deployment Script - GitHub Push Mode
# No local CLI authentication required - uses GitHub Actions auto-deploy

set -e

echo "🚀 ATN Project Deployment Script"
echo "=================================="
echo "Mode: GitHub Push Auto-Deploy"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_NAME="atn-project"
BOT_DIR="src/bot"
API_DIR="src/api"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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
    
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check if inside git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    log_info "All prerequisites met ✓"
}

# Deploy to GitHub - triggers automatic deployment
deploy_github() {
    log_step "Deploying to GitHub (triggers auto-deploy)..."
    
    # Get current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $BRANCH"
    
    # Add all changes
    git add -A
    
    # Create commit message
    COMMIT_MSG="deploy: ATN project update $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Commit
    log_info "Committing changes..."
    git commit -m "$COMMIT_MSG" || log_warn "No changes to commit"
    
    # Push to trigger GitHub Actions
    log_info "Pushing to GitHub (this will trigger auto-deploy)..."
    git push origin $BRANCH
    
    log_info "✓ Code pushed to GitHub!"
    log_info "✓ GitHub Actions will auto-deploy to Railway/Render"
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Deployment Triggered!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Check GitHub Actions tab for build status"
    echo "2. Railway/Render will auto-deploy from main branch"
    echo "3. Visit: https://railway.app/dashboard or https://render.com"
}

# Show deployment status
status() {
    echo "================================"
    echo "Service Status"
    echo "================================"
    
    echo -e "\n🤖 Telegram Bot:"
    if pgrep -f "src.bot.main" > /dev/null; then
        echo -e "   Status: Running ✓"
    else
        echo -e "   Status: Stopped ✗"
    fi
    
    echo -e "\n🌐 API Server:"
    if pgrep -f "src.api.main" > /dev/null; then
        echo -e "   Status: Running ✓"
    else
        echo -e "   Status: Stopped ✗"
    fi
    
    echo -e "\n🔗 Deployment Links:"
    echo "   GitHub: https://github.com/themachinehf/openclaw-workspace"
    echo "   Railway: https://railway.app/dashboard"
    echo "   Render: https://render.com"
}

# Show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy      Deploy to GitHub (triggers auto-deploy)"
    echo "  status      Show service status"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  TELEGRAM_BOT_TOKEN  - Telegram Bot API Token"
    echo "  DATABASE_URL        - Database connection string"
    echo "  CONTRACT_ADDRESS   - Deployed contract address"
    echo ""
    echo "How it works:"
    echo "  1. Run 'deploy' to push code to GitHub"
    echo "  2. GitHub Actions automatically builds"
    echo "  3. Railway/Render auto-deploys from main branch"
    echo "  4. No local CLI authentication needed!"
}

# Main script
case "${1:-help}" in
    deploy)
        check_prerequisites
        deploy_github
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
