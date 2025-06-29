#!/bin/bash

# Shogun AI Core - Chainlink Functions Deployment Script
# This script automates the deployment of Chainlink Functions

set -e

echo "🚀 Shogun AI Core - Chainlink Functions Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

# Check if Chainlink CLI is installed
if ! command -v chainlink &> /dev/null; then
    echo -e "${YELLOW}⚠️  Chainlink CLI not found. Installing...${NC}"
    npm install -g @chainlink/functions-cli
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Get configuration
echo -e "${BLUE}Configuration${NC}"
echo "=================="

# Check if subscription ID is provided
if [ -z "$CHAINLINK_SUBSCRIPTION_ID" ]; then
    echo -e "${YELLOW}Please enter your Chainlink Functions subscription ID:${NC}"
    read -r CHAINLINK_SUBSCRIPTION_ID
fi

# Check if network is specified
NETWORK=${CHAINLINK_NETWORK:-"avalanche"}
echo -e "${BLUE}Network: ${NETWORK}${NC}"
echo -e "${BLUE}Subscription ID: ${CHAINLINK_SUBSCRIPTION_ID}${NC}"

# Navigate to functions directory
cd src/serverless/functions

echo -e "${BLUE}Installing dependencies...${NC}"
npm install

echo -e "${BLUE}Deploying Chainlink Functions...${NC}"
echo "=================================="

# Function deployment function
deploy_function() {
    local function_name=$1
    local source_file=$2
    local display_name=$3
    
    echo -e "${BLUE}Deploying ${display_name}...${NC}"
    
    if chainlink functions deploy \
        --source "$source_file" \
        --name "shogun-${function_name}" \
        --network "$NETWORK" \
        --subscription-id "$CHAINLINK_SUBSCRIPTION_ID"; then
        echo -e "${GREEN}✅ ${display_name} deployed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to deploy ${display_name}${NC}"
        return 1
    fi
}

# Deploy all functions
deploy_function "strategy-risk-scoring" "strategy_risk_scoring.js" "Strategy Risk Scoring"
deploy_function "cross-chain-apy" "cross_chain_apy.js" "Cross-Chain APY"
deploy_function "allocation-optimization" "allocation_optimization.js" "Allocation Optimization"
deploy_function "oracle-health-check" "oracle_health_check.js" "Oracle Health Check"

echo -e "${GREEN}🎉 All Chainlink Functions deployed successfully!${NC}"

# Get function IDs
echo -e "${BLUE}Getting function IDs...${NC}"
echo "========================"

# This would need to be updated based on actual CLI output format
echo -e "${YELLOW}Please note down the function IDs from the deployment output above.${NC}"
echo -e "${YELLOW}You'll need to update your configs/config.yaml with these IDs.${NC}"

# Create config template
echo -e "${BLUE}Creating configuration template...${NC}"
cat > ../../../chainlink_functions_config_template.yaml << EOF
# Chainlink Functions Configuration Template
# Update this with your actual function IDs and save as configs/config.yaml

chainlink_functions:
  # Network configuration
  network: "${NETWORK}"
  
  # Chainlink Functions subscription
  subscription_id: "${CHAINLINK_SUBSCRIPTION_ID}"
  
  # Function IDs (replace with actual IDs from deployment)
  function_ids:
    strategy_risk_scoring: "YOUR_STRATEGY_RISK_FUNCTION_ID"
    cross_chain_apy: "YOUR_CROSS_CHAIN_APY_FUNCTION_ID"
    allocation_optimization: "YOUR_ALLOCATION_OPT_FUNCTION_ID"
    oracle_health_check: "YOUR_ORACLE_HEALTH_FUNCTION_ID"
  
  # API credentials
  defillama_api_key: "\${DEFILLAMA_API_KEY}"
  
  # Oracle health monitoring
  oracle_deviation_threshold: 0.02
  
  # Compute engine settings
  max_concurrent_tasks: 5
  verification_timeout: 300
  max_retries: 3
  
  # Onchain bridging configuration
  rpc_url: "https://api.avax.network/ext/bc/C/rpc"
  private_key: "\${PRIVATE_KEY}"
  
  # Smart contract addresses for bridging results
  contracts:
    risk_scoring: "0x1234567890123456789012345678901234567890"
    allocation: "0x2345678901234567890123456789012345678901"
    market_data: "0x3456789012345678901234567890123456789012"
EOF

echo -e "${GREEN}✅ Configuration template created: chainlink_functions_config_template.yaml${NC}"

# Test functions
echo -e "${BLUE}Testing functions...${NC}"
echo "=================="

echo -e "${YELLOW}To test your functions, run:${NC}"
echo "cd src/serverless/functions"
echo "node -e \"const { execute } = require('./strategy_risk_scoring.js'); execute(['0x1234...', '[\"USDC\"]', '0.3', '0.4', '0.25']).then(console.log).catch(console.error);\""

# Final instructions
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Update configs/config.yaml with your function IDs"
echo "2. Set environment variables:"
echo "   export CHAINLINK_SUBSCRIPTION_ID=\"${CHAINLINK_SUBSCRIPTION_ID}\""
echo "   export DEFILLAMA_API_KEY=\"your_defillama_api_key\""
echo "   export PRIVATE_KEY=\"your_private_key\""
echo "3. Test the integration: python src/main.py"
echo ""
echo -e "${BLUE}For more information, see:${NC}"
echo "- src/serverless/functions/DEPLOYMENT.md"
echo "- docs/SERVERLESS_INTEGRATION.md" 