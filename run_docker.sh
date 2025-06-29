#!/bin/bash

# Shogun AI Core - Docker Runner for Chainlink Functions
# This script makes it easy to run Chainlink Functions in Docker

set -e

echo "🐳 Shogun AI Core - Docker Chainlink Functions Runner"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 [OPTION]"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  build     - Build the Docker image"
    echo "  run       - Run the container (interactive)"
    echo "  test      - Run tests and exit"
    echo "  shell     - Open shell in container"
    echo "  deploy    - Deploy functions to Chainlink (requires subscription ID)"
    echo "  clean     - Remove containers and images"
    echo "  help      - Show this help"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 build"
    echo "  $0 test"
    echo "  $0 shell"
    echo "  CHAINLINK_SUBSCRIPTION_ID=your_id $0 deploy"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Build the image
build_image() {
    echo -e "${BLUE}🔨 Building Docker image...${NC}"
    docker compose build
    echo -e "${GREEN}✅ Image built successfully${NC}"
}

# Run the container
run_container() {
    echo -e "${BLUE}🚀 Starting container...${NC}"
    docker compose up -d
    echo -e "${GREEN}✅ Container started${NC}"
    echo -e "${YELLOW}To access the container:${NC}"
    echo "  docker exec -it shogun-chainlink-functions /bin/bash"
}

# Run tests
run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    docker compose run --rm shogun-chainlink-functions /app/test_functions.sh
}

# Open shell
open_shell() {
    echo -e "${BLUE}🐚 Opening shell in container...${NC}"
    docker compose run --rm shogun-chainlink-functions /bin/bash
}

# Deploy functions
deploy_functions() {
    if [ -z "$CHAINLINK_SUBSCRIPTION_ID" ]; then
        echo -e "${RED}❌ CHAINLINK_SUBSCRIPTION_ID environment variable is required${NC}"
        echo -e "${YELLOW}Set it like: CHAINLINK_SUBSCRIPTION_ID=your_id $0 deploy${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🚀 Deploying functions to Chainlink...${NC}"
    docker compose run --rm shogun-chainlink-functions bash -c "
        cd /app/functions
        npm install
        chainlink functions login
        chainlink functions deploy --source strategy_risk_scoring.js --name 'shogun-strategy-risk-scoring' --network avalanche --subscription-id $CHAINLINK_SUBSCRIPTION_ID
        chainlink functions deploy --source cross_chain_apy.js --name 'shogun-cross-chain-apy' --network avalanche --subscription-id $CHAINLINK_SUBSCRIPTION_ID
        chainlink functions deploy --source allocation_optimization.js --name 'shogun-allocation-optimization' --network avalanche --subscription-id $CHAINLINK_SUBSCRIPTION_ID
        chainlink functions deploy --source oracle_health_check.js --name 'shogun-oracle-health-check' --network avalanche --subscription-id $CHAINLINK_SUBSCRIPTION_ID
    "
}

# Clean up
clean_up() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    docker compose down --rmi all --volumes --remove-orphans
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main script logic
case "${1:-help}" in
    build)
        check_docker
        build_image
        ;;
    run)
        check_docker
        run_container
        ;;
    test)
        check_docker
        run_tests
        ;;
    shell)
        check_docker
        open_shell
        ;;
    deploy)
        check_docker
        deploy_functions
        ;;
    clean)
        check_docker
        clean_up
        ;;
    help|*)
        show_usage
        ;;
esac 