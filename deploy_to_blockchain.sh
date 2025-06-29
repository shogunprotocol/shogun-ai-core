#!/bin/bash

# 🚀 Shogun AI Core - Real Blockchain Deployment
# This script helps you deploy Chainlink Functions to actual blockchain networks

set -e

echo "🔥 Shogun AI Core - Real Blockchain Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0 [NETWORK] [SUBSCRIPTION_ID]"
    echo ""
    echo -e "${BLUE}Networks:${NC}"
    echo "  avalanche    - Avalanche C-Chain (Recommended for DeFi)"
    echo "  ethereum     - Ethereum Mainnet"
    echo "  polygon      - Polygon"
    echo "  bsc          - Binance Smart Chain"
    echo "  sepolia      - Ethereum Testnet (Free)"
    echo "  mumbai       - Polygon Testnet (Free)"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 avalanche 1234567890abcdef"
    echo "  $0 sepolia 1234567890abcdef"
    echo ""
    echo -e "${YELLOW}Costs:${NC}"
    echo "  Mainnet: ~0.1-0.5 LINK per function"
    echo "  Testnet: FREE (limited usage)"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if subscription ID is provided
    if [ -z "$SUBSCRIPTION_ID" ]; then
        echo -e "${RED}❌ Subscription ID is required${NC}"
        echo -e "${YELLOW}Get one from: https://functions.chain.link${NC}"
        exit 1
    fi
    
    # Check if network is valid
    case "$NETWORK" in
        avalanche|ethereum|polygon|bsc|sepolia|mumbai)
            echo -e "${GREEN}✅ Network: $NETWORK${NC}"
            ;;
        *)
            echo -e "${RED}❌ Invalid network: $NETWORK${NC}"
            show_usage
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Prepare functions for deployment
prepare_functions() {
    echo -e "${BLUE}📦 Preparing functions for deployment...${NC}"
    echo "============================================="
    
    # Create deployment directory
    mkdir -p deployment_functions
    
    # Copy and prepare each function
    prepare_single_function() {
        local function_name=$1
        local source_file=$2
        local display_name=$3
        
        echo -e "${BLUE}📝 Preparing ${display_name}...${NC}"
        
        # Copy function to deployment directory
        cp "src/serverless/functions/$source_file" "deployment_functions/"
        
        echo -e "${GREEN}✅ ${display_name} prepared${NC}"
    }
    
    # Prepare all functions
    prepare_single_function "strategy-risk-scoring" "strategy_risk_scoring.js" "Strategy Risk Scoring"
    prepare_single_function "cross-chain-apy" "cross_chain_apy.js" "Cross-Chain APY"
    prepare_single_function "allocation-optimization" "allocation_optimization.js" "Allocation Optimization"
    prepare_single_function "oracle-health-check" "oracle_health_check.js" "Oracle Health Check"
    
    echo -e "${GREEN}✅ All functions prepared for deployment${NC}"
}

# Show deployment instructions
show_deployment_instructions() {
    echo -e "${BLUE}🚀 Deployment Instructions${NC}"
    echo "=============================="
    echo ""
    echo -e "${YELLOW}Step 1: Go to Chainlink Functions Dashboard${NC}"
    echo "  🌐 https://functions.chain.link"
    echo "  🔑 Login to your account"
    echo ""
    echo -e "${YELLOW}Step 2: Create Functions${NC}"
    echo "  📝 Click 'Create Function'"
    echo "  🌐 Select Network: $NETWORK"
    echo "  💰 Select Subscription: $SUBSCRIPTION_ID"
    echo ""
    echo -e "${YELLOW}Step 3: Deploy Each Function${NC}"
    echo ""
    
    # Function deployment instructions
    show_function_instructions() {
        local function_name=$1
        local source_file=$2
        local display_name=$3
        
        echo -e "${BLUE}📦 ${display_name}${NC}"
        echo "  📄 Function Name: shogun-$function_name"
        echo "  📁 Source File: deployment_functions/$source_file"
        echo "  📋 Steps:"
        echo "    1. Copy content from deployment_functions/$source_file"
        echo "    2. Paste into the Functions editor"
        echo "    3. Click 'Deploy'"
        echo "    4. Note down the Function ID"
        echo ""
    }
    
    show_function_instructions "strategy-risk-scoring" "strategy_risk_scoring.js" "Strategy Risk Scoring"
    show_function_instructions "cross-chain-apy" "cross_chain_apy.js" "Cross-Chain APY"
    show_function_instructions "allocation-optimization" "allocation_optimization.js" "Allocation Optimization"
    show_function_instructions "oracle-health-check" "oracle_health_check.js" "Oracle Health Check"
}

# Create configuration template
create_config_template() {
    echo -e "${BLUE}📋 Creating configuration template...${NC}"
    
    cat > chainlink_functions_deployed.yaml << EOF
# Chainlink Functions Configuration - DEPLOYED
# Network: $NETWORK
# Subscription ID: $SUBSCRIPTION_ID
# Deployed at: $(date)

chainlink_functions:
  network: "$NETWORK"
  subscription_id: "$SUBSCRIPTION_ID"
  
  # Function IDs (replace with actual IDs from deployment)
  function_ids:
    strategy_risk_scoring: "YOUR_STRATEGY_RISK_FUNCTION_ID"
    cross_chain_apy: "YOUR_CROSS_CHAIN_APY_FUNCTION_ID"
    allocation_optimization: "YOUR_ALLOCATION_OPT_FUNCTION_ID"
    oracle_health_check: "YOUR_ORACLE_HEALTH_FUNCTION_ID"
  
  # RPC URLs for different networks
  rpc_urls:
    avalanche: "https://api.avax.network/ext/bc/C/rpc"
    ethereum: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
    polygon: "https://polygon-rpc.com"
    bsc: "https://bsc-dataseed.binance.org"
    sepolia: "https://sepolia.infura.io/v3/YOUR_KEY"
    mumbai: "https://polygon-mumbai.infura.io/v3/YOUR_KEY"
  
  # Gas settings
  gas_limit: 300000
  gas_price: "auto"
  
  # Verification settings
  verification_timeout: 300
  max_retries: 3
EOF

    echo -e "${GREEN}✅ Configuration template created: chainlink_functions_deployed.yaml${NC}"
}

# Show testing instructions
show_testing_instructions() {
    echo -e "${BLUE}🧪 Testing Instructions${NC}"
    echo "========================"
    echo ""
    echo -e "${YELLOW}After deployment, test your functions:${NC}"
    echo "1. Go to https://functions.chain.link"
    echo "2. Find your deployed functions"
    echo "3. Click 'Execute' to test"
    echo ""
    echo -e "${BLUE}Example test parameters:${NC}"
    echo "Strategy Risk Scoring:"
    echo "  [\"0x1234567890123456789012345678901234567890\", \"[\\\"USDC\\\", \\\"WETH\\\"]\", \"0.3\", \"0.4\", \"0.25\"]"
    echo ""
    echo -e "${PURPLE}💡 Pro tip: Use the Chainlink Functions dashboard to monitor gas usage and execution logs${NC}"
}

# Show next steps
show_next_steps() {
    echo -e "${GREEN}🎉 Deployment preparation complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. 📝 Follow the deployment instructions above"
    echo "2. 🔗 Update chainlink_functions_deployed.yaml with your function IDs"
    echo "3. 💰 Monitor LINK consumption"
    echo "4. 📊 Set up monitoring and alerts"
    echo ""
    echo -e "${BLUE}Smart Contract Integration:${NC}"
    echo "```solidity"
    echo "// Example: Call your deployed function"
    echo "FunctionsConsumer consumer = FunctionsConsumer(0x...);"
    echo "consumer.executeRequest("
    echo "    YOUR_FUNCTION_ID,"
    echo "    source,"
    echo "    secrets,"
    echo "    args"
    echo ");"
    echo "```"
    echo ""
    echo -e "${BLUE}Costs:${NC}"
    if [[ "$NETWORK" == *"testnet"* ]]; then
        echo "  ✅ Testnet: FREE (limited usage)"
    else
        echo "  💰 Mainnet: ~0.01-0.05 LINK per execution"
        echo "  💰 Monthly: ~1-10 LINK depending on usage"
    fi
    echo ""
    echo -e "${YELLOW}📁 Your functions are ready in: deployment_functions/${NC}"
}

# Main script logic
NETWORK=${1:-"avalanche"}
SUBSCRIPTION_ID=${2:-""}

if [ "$1" = "help" ] || [ -z "$SUBSCRIPTION_ID" ]; then
    show_usage
    exit 0
fi

check_prerequisites
prepare_functions
show_deployment_instructions
create_config_template
show_testing_instructions
show_next_steps 