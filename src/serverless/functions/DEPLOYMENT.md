# Chainlink Functions Deployment Guide

This guide walks you through deploying the Shogun AI Core Chainlink Functions to the Chainlink network.

## Prerequisites

1. **Chainlink Functions Account**
   - Sign up at [functions.chain.link](https://functions.chain.link)
   - Create a subscription and get your subscription ID
   - Add LINK tokens to your subscription for gas fees

2. **Node.js Environment**
   - Node.js 18+ installed
   - npm or yarn package manager

3. **Chainlink CLI** (Optional)
   - Install Chainlink CLI for easier deployment
   ```bash
   npm install -g @chainlink/functions-cli
   ```

## Step 1: Setup Project

1. **Navigate to functions directory:**
   ```bash
   cd src/serverless/functions
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Verify functions are ready:**
   ```bash
   node -e "console.log('Functions ready for deployment')"
   ```

## Step 2: Deploy Functions

### Option A: Using Chainlink CLI (Recommended)

1. **Login to Chainlink Functions:**
   ```bash
   chainlink functions login
   ```

2. **Deploy each function:**
   ```bash
   # Deploy strategy risk scoring function
   chainlink functions deploy \
     --source strategy_risk_scoring.js \
     --name "shogun-strategy-risk-scoring" \
     --network avalanche \
     --subscription-id YOUR_SUBSCRIPTION_ID

   # Deploy cross-chain APY function
   chainlink functions deploy \
     --source cross_chain_apy.js \
     --name "shogun-cross-chain-apy" \
     --network avalanche \
     --subscription-id YOUR_SUBSCRIPTION_ID

   # Deploy allocation optimization function
   chainlink functions deploy \
     --source allocation_optimization.js \
     --name "shogun-allocation-optimization" \
     --network avalanche \
     --subscription-id YOUR_SUBSCRIPTION_ID

   # Deploy oracle health check function
   chainlink functions deploy \
     --source oracle_health_check.js \
     --name "shogun-oracle-health-check" \
     --network avalanche \
     --subscription-id YOUR_SUBSCRIPTION_ID
   ```

### Option B: Using Web Interface

1. **Go to [functions.chain.link](https://functions.chain.link)**

2. **Create a new function:**
   - Click "Create Function"
   - Select your subscription
   - Choose "JavaScript" as the runtime

3. **Upload function code:**
   - Copy the content of each `.js` file
   - Paste into the code editor
   - Set function name and description

4. **Deploy:**
   - Click "Deploy Function"
   - Note the function ID for configuration

## Step 3: Test Functions

### Test Strategy Risk Scoring

```bash
# Test with sample data
chainlink functions test \
  --function-id YOUR_FUNCTION_ID \
  --args '["0x1234567890123456789012345678901234567890", "[\"USDC\", \"WETH\", \"AVAX\"]", "0.3", "0.4", "0.25"]'
```

### Test Cross-Chain APY

```bash
# Test with sample strategy addresses
chainlink functions test \
  --function-id YOUR_FUNCTION_ID \
  --args '["[\"0x794a61358D6845594F94dc1DB02A252b5b4814aD\", \"0x5C0401e81Bc07Ca70fAD469b451682c0d747Ef1c\"]", "[\"avalanche\", \"ethereum\"]", "1640995200"]'
```

### Test Allocation Optimization

```bash
# Test with sample vault data
chainlink functions test \
  --function-id YOUR_FUNCTION_ID \
  --args '["{\"strategy_1\": 0.3, \"strategy_2\": 0.4}", "{\"strategy_1\": {\"max_allocation\": 0.4, \"risk_score\": 0.2}}", "1000000", "0.3"]'
```

### Test Oracle Health Check

```bash
# Test with sample oracle addresses
chainlink functions test \
  --function-id YOUR_FUNCTION_ID \
  --args '["[\"0x1234567890123456789012345678901234567890\"]", "1640995200", "0.02"]'
```

## Step 4: Update Configuration

1. **Get your function IDs** from the deployment output

2. **Update `configs/config.yaml`:**
   ```yaml
   chainlink_functions:
     subscription_id: "YOUR_SUBSCRIPTION_ID"
     function_ids:
       strategy_risk_scoring: "YOUR_STRATEGY_RISK_FUNCTION_ID"
       cross_chain_apy: "YOUR_CROSS_CHAIN_APY_FUNCTION_ID"
       allocation_optimization: "YOUR_ALLOCATION_OPT_FUNCTION_ID"
       oracle_health_check: "YOUR_ORACLE_HEALTH_FUNCTION_ID"
   ```

3. **Set environment variables:**
   ```bash
   export CHAINLINK_SUBSCRIPTION_ID="YOUR_SUBSCRIPTION_ID"
   export CHAINLINK_FUNCTION_IDS="YOUR_FUNCTION_IDS"
   ```

## Step 5: Deploy Smart Contracts (Optional)

If you want to bridge results onchain, deploy these contracts:

### Risk Scoring Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract RiskScoringContract {
    mapping(address => uint256) public riskScores;
    mapping(bytes32 => bool) public verifiedHashes;
    
    event RiskScoreUpdated(address indexed strategy, uint256 score, bytes32 verificationHash);
    
    function updateRiskScore(
        address strategy,
        uint256 riskScore,
        bytes32 verificationHash
    ) external {
        require(!verifiedHashes[verificationHash], "Hash already used");
        require(riskScore <= 1e18, "Invalid risk score"); // 18 decimals
        
        verifiedHashes[verificationHash] = true;
        riskScores[strategy] = riskScore;
        
        emit RiskScoreUpdated(strategy, riskScore, verificationHash);
    }
    
    function getRiskScore(address strategy) external view returns (uint256) {
        return riskScores[strategy];
    }
}
```

### Allocation Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AllocationContract {
    mapping(bytes32 => mapping(address => uint256)) public allocations;
    mapping(bytes32 => bool) public verifiedHashes;
    
    event AllocationProposed(bytes32 indexed vaultId, address[] strategies, uint256[] weights, bytes32 verificationHash);
    
    function proposeAllocation(
        bytes32 vaultId,
        address[] calldata strategies,
        uint256[] calldata weights,
        bytes32 verificationHash
    ) external {
        require(!verifiedHashes[verificationHash], "Hash already used");
        require(strategies.length == weights.length, "Array length mismatch");
        
        verifiedHashes[verificationHash] = true;
        
        for (uint256 i = 0; i < strategies.length; i++) {
            allocations[vaultId][strategies[i]] = weights[i];
        }
        
        emit AllocationProposed(vaultId, strategies, weights, verificationHash);
    }
    
    function getAllocation(bytes32 vaultId, address strategy) external view returns (uint256) {
        return allocations[vaultId][strategy];
    }
}
```

## Step 6: Verify Deployment

1. **Test the integration:**
   ```bash
   cd ../../..  # Back to project root
   python src/main.py
   ```

2. **Check function logs:**
   - Go to [functions.chain.link](https://functions.chain.link)
   - View your function executions
   - Check for any errors or issues

3. **Monitor gas usage:**
   - Track LINK consumption
   - Optimize function efficiency if needed

## Troubleshooting

### Common Issues

1. **Function deployment fails:**
   - Check syntax errors in JavaScript code
   - Verify all dependencies are included
   - Ensure subscription has sufficient LINK

2. **Function execution fails:**
   - Check input parameter format
   - Verify API endpoints are accessible
   - Review function logs for errors

3. **High gas costs:**
   - Optimize function code
   - Reduce HTTP requests
   - Use efficient data structures

### Debugging

1. **Local testing:**
   ```bash
   # Test function locally
   node -e "
   const { execute } = require('./strategy_risk_scoring.js');
   execute(['0x1234...', '[\"USDC\"]', '0.3', '0.4', '0.25'])
     .then(console.log)
     .catch(console.error);
   "
   ```

2. **Check function logs:**
   - Use `console.log()` for debugging
   - Check execution history in Chainlink Functions dashboard

## Security Considerations

1. **Input validation:** All functions validate inputs
2. **Error handling:** Comprehensive error handling in place
3. **Verification hashes:** Cryptographic verification for results
4. **Rate limiting:** Respect API rate limits
5. **Fallback mechanisms:** Graceful degradation on failures

## Cost Optimization

1. **Gas efficiency:** Minimize computation in functions
2. **Batch processing:** Combine multiple operations
3. **Caching:** Cache frequently accessed data
4. **Optimization:** Use efficient algorithms and data structures

## Next Steps

1. **Monitor function performance**
2. **Optimize based on usage patterns**
3. **Add more sophisticated algorithms**
4. **Implement advanced error handling**
5. **Scale to additional networks**

For more information, see the [Chainlink Functions documentation](https://docs.chain.link/chainlink-functions). 