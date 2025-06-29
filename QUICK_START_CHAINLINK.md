# 🚀 Quick Start: Deploy Chainlink Functions

This guide will get you up and running with Chainlink Functions for Shogun AI Core in under 10 minutes!

## Prerequisites

- Node.js 18+ installed
- Chainlink Functions account at [functions.chain.link](https://functions.chain.link)
- Chainlink Functions subscription with LINK tokens

## Step 1: Get Your Subscription ID

1. Go to [functions.chain.link](https://functions.chain.link)
2. Sign up/login to your account
3. Create a subscription (if you don't have one)
4. Copy your subscription ID

## Step 2: Deploy Functions (Automated)

Run the deployment script:

```bash
# Option 1: Set subscription ID as environment variable
export CHAINLINK_SUBSCRIPTION_ID="your_subscription_id_here"
./deploy_chainlink_functions.sh

# Option 2: Enter subscription ID when prompted
./deploy_chainlink_functions.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Install dependencies
- ✅ Deploy all 4 functions
- ✅ Create configuration template
- ✅ Provide next steps

## Step 3: Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# 1. Navigate to functions directory
cd src/serverless/functions

# 2. Install dependencies
npm install

# 3. Install Chainlink CLI
npm install -g @chainlink/functions-cli

# 4. Login to Chainlink Functions
chainlink functions login

# 5. Deploy each function
chainlink functions deploy \
  --source strategy_risk_scoring.js \
  --name "shogun-strategy-risk-scoring" \
  --network avalanche \
  --subscription-id YOUR_SUBSCRIPTION_ID

chainlink functions deploy \
  --source cross_chain_apy.js \
  --name "shogun-cross-chain-apy" \
  --network avalanche \
  --subscription-id YOUR_SUBSCRIPTION_ID

chainlink functions deploy \
  --source allocation_optimization.js \
  --name "shogun-allocation-optimization" \
  --network avalanche \
  --subscription-id YOUR_SUBSCRIPTION_ID

chainlink functions deploy \
  --source oracle_health_check.js \
  --name "shogun-oracle-health-check" \
  --network avalanche \
  --subscription-id YOUR_SUBSCRIPTION_ID
```

## Step 4: Update Configuration

1. **Get function IDs** from the deployment output
2. **Update your config:**

```bash
# Copy the template
cp chainlink_functions_config_template.yaml configs/config.yaml

# Edit with your function IDs
nano configs/config.yaml
```

3. **Set environment variables:**

```bash
export CHAINLINK_SUBSCRIPTION_ID="your_subscription_id"
export DEFILLAMA_API_KEY="your_defillama_api_key"
export PRIVATE_KEY="your_private_key"
```

## Step 5: Test the Integration

```bash
# Test locally first
cd src/serverless/functions
node -e "
const { execute } = require('./strategy_risk_scoring.js');
execute(['0x1234567890123456789012345678901234567890', '[\"USDC\", \"WETH\"]', '0.3', '0.4', '0.25'])
  .then(console.log)
  .catch(console.error);
"

# Test the full integration
cd ../../..
python src/main.py
```

## Step 6: Monitor and Verify

1. **Check function logs:**
   - Go to [functions.chain.link](https://functions.chain.link)
   - View your function executions
   - Check for any errors

2. **Monitor gas usage:**
   - Track LINK consumption
   - Optimize if needed

## Troubleshooting

### Common Issues

**❌ "Node.js not found"**
```bash
# Install Node.js 18+
brew install node  # macOS
# or download from nodejs.org
```

**❌ "Chainlink CLI not found"**
```bash
npm install -g @chainlink/functions-cli
```

**❌ "Subscription ID required"**
- Make sure you have a Chainlink Functions subscription
- Add LINK tokens to your subscription

**❌ "Function deployment failed"**
- Check your subscription has sufficient LINK
- Verify JavaScript syntax
- Check network connectivity

### Getting Help

- 📖 [Full Deployment Guide](src/serverless/functions/DEPLOYMENT.md)
- 📖 [Integration Documentation](docs/SERVERLESS_INTEGRATION.md)
- 🔗 [Chainlink Functions Docs](https://docs.chain.link/chainlink-functions)

## What's Next?

Once deployed, your Shogun AI Core will:

1. **Run ML risk scoring** via Chainlink Functions
2. **Fetch cross-chain APY data** with verification
3. **Optimize vault allocations** offchain
4. **Monitor oracle health** in real-time
5. **Bridge verified results** onchain

## Cost Estimation

- **Deployment:** ~0.1 LINK per function
- **Execution:** ~0.01-0.05 LINK per call
- **Monthly:** ~1-5 LINK depending on usage

---

🎉 **You're all set!** Your Shogun AI Core now has verifiable offchain computation via Chainlink Functions! 