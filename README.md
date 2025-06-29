# shogun core ai

An AI-powered DeFi strategy agent that generates and executes vault strategies using LLM-based planning and risk assessment. shogun core ai specializes in cross-protocol yield optimization through a secure Multi-Token Vault system with **Chainlink Functions** integration for verifiable offchain computation.

## System Overview

```mermaid
graph TB
    subgraph ShogunCoreAI["shogun core ai"]
        LLM[LLM Planner]
        Risk[Risk Model]
        KB[Knowledge Box]
        Exec[Strategy Executor]
        
        subgraph Providers["Data Providers"]
            DL[DefiLlama Provider]
            BS[Blockscout Provider]
        end
        
        subgraph ChainlinkFunctions["Chainlink Functions"]
            CF[Chainlink Functions Client]
            CE[Compute Engine]
            VE[Verification Engine]
        end
        
        LLM --> Risk
        Risk --> Exec
        KB --> LLM
        Providers --> KB
        Risk --> CF
        CF --> CE
        CE --> VE
    end
    
    subgraph Vault["Multi-Token Vault"]
        MTV[MultiTokenVault.sol]
        ORACLE[Chainlink Oracle]
        STRATEGIES[Whitelisted Strategies]
        
        MTV --> ORACLE
        MTV --> STRATEGIES
    end
    
    Exec --> |Execute| MTV
    VE --> |Bridge Results| MTV
```

For a detailed view of the system architecture, including strategy flows, risk assessment, and monitoring parameters, see our [shogun core ai Architecture Documentation](docs/SHOGUN_CORE_AI_ARCHITECTURE.md).

## Overview

shogun core ai is a deterministic AI system that:
- Manages strategies through a secure Multi-Token Vault
- Implements cross-protocol yield optimization
- Uses LLM-based planning for strategy generation
- Employs multi-layered risk assessment
- Executes approved strategies through whitelisted contracts
- **Leverages Chainlink Functions for verifiable offchain computation**

## Core Components

### Multi-Token Vault (MultiTokenVault.sol)
- Accepts multiple ERC20 tokens (USDC, WBTC, WETH, LINK)
- Chainlink oracle integration for reliable price feeds
- Automatic token conversion to USDC equivalent
- Advanced multi-asset management with precise pricing

### Strategy System
- Whitelisted strategy contracts
- AI agent execution through secure interfaces
- Harvest and emergency exit capabilities
- Transparent fund management

### Chainlink Functions Integration
- **Strategy Risk Scoring**: Offchain ML model inference with verifiable proofs
- **Cross-Chain APY Aggregation**: Multi-chain data fetching and analysis
- **Vault Allocation Optimization**: Complex optimization algorithms with cryptographic verification
- **Oracle Health Monitoring**: Real-time Chainlink oracle health checks

## Project Structure

```
📁 shogun-core-ai/
├── 📂 src/                    # Source code
│   ├── 📂 agent/             # Core agent logic
│   │   ├── llm_planner.py    # Strategy generation
│   │   ├── risk_model.py     # Risk assessment
│   │   └── knowledge_box.py  # Historical data
│   ├── 📂 data_providers/    # Protocol integrations
│   │   ├── defillama_provider.py  # DefiLlama data
│   │   └── blockscout.py     # Event monitoring
│   ├── 📂 execution/         # On-chain execution
│   ├── 📂 serverless/        # Chainlink Functions integration
│   │   ├── functions_client.py    # Chainlink Functions client
│   │   ├── compute_engine.py      # Task orchestration
│   │   ├── verification.py        # Result verification
│   │   └── functions/             # JavaScript functions
│   └── main.py               # Main orchestration
├── 📂 docs/                  # Documentation
│   ├── SHOGUN_CORE_AI_ARCHITECTURE.md  # System architecture
│   └── SERVERLESS_INTEGRATION.md       # Chainlink Functions guide
├── 📂 configs/               # Configuration files
└── requirements.txt          # Dependencies
```

## Risk Assessment

shogun core ai employs a multi-layered risk assessment system:

1. **Protocol Risk**
   - TVL monitoring
   - Liquidity depth analysis
   - Smart contract risk scoring
   - Historical pattern matching

2. **Market Risk**
   - Volatility tracking
   - Price impact analysis
   - Slippage protection
   - Liquidation risk assessment

3. **Execution Risk**
   - Gas optimization
   - Transaction sequencing
   - Multi-sig verification
   - Rate limiting

4. **Chainlink Functions Risk**
   - Offchain computation verification
   - Cryptographic proof validation
   - Oracle health monitoring
   - Cross-chain data integrity

For detailed risk assessment flows and monitoring parameters, refer to the [Risk Assessment section](docs/SHOGUN_CORE_AI_ARCHITECTURE.md#risk-assessment) in our architecture documentation.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
- Copy `.env.example` to `.env`
- Add your API keys and RPC endpoints:
  - Ethereum RPC
  - DefiLlama API key
  - OpenRouter API key
  - **Chainlink Functions subscription ID**
  - **Private key for onchain bridging**

3. Configure protocols:
Edit `configs/config.yaml` to set:
- Vault addresses
- Strategy contract addresses
- Risk thresholds
- Monitoring parameters
- LLM settings
- **Chainlink Functions configuration**

4. Run the agent:
```bash
python src/main.py
```

## Chainlink Functions Integration

### What is Chainlink Functions?
Chainlink Functions is a serverless platform that allows you to run custom JavaScript code offchain with verifiable results that can be bridged back onchain.

### Use Cases in Shogun AI Core:

1. **Strategy Risk Scoring**
   ```python
   # Submit risk scoring to Chainlink Functions
   task_id = await chainlink_engine.submit_strategy_risk_scoring_task({
       'strategy_address': '0x1234...',
       'tokens': ['USDC', 'WETH', 'AVAX'],
       'current_allocation': 0.3,
       'max_allocation': 0.4,
       'risk_score': 0.25
   })
   ```

2. **Cross-Chain APY Aggregation**
   ```python
   # Fetch APY data from multiple chains
   response = await chainlink_engine.submit_cross_chain_apy_task([
       '0x794a61358D6845594F94dc1DB02A252b5b4814aD',  # Aave V3
       '0x5C0401e81Bc07Ca70fAD469b451682c0d747Ef1c',  # Benqi
       '0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10'   # Trader Joe
   ])
   ```

3. **Vault Allocation Optimization**
   ```python
   # Optimize vault allocation
   allocation = await chainlink_engine.submit_allocation_optimization_task({
       'current_allocations': {...},
       'strategy_constraints': {...},
       'total_value_locked': 1000000,
       'risk_tolerance': 0.3
   })
   ```

For detailed Chainlink Functions integration guide, see [Chainlink Functions Integration](docs/SERVERLESS_INTEGRATION.md).

## Security Features

- **Deterministic Execution**: No randomness in strategy generation
- **Multi-sig Protection**: All transactions require multiple signatures
- **Risk Scoring**: Every strategy is scored before execution
- **Real-time Monitoring**: Continuous protocol health checks
- **Emergency Shutdown**: Automatic response to unusual events
- **Whitelisted Strategies**: Only approved contracts can execute
- **Oracle Integration**: Reliable price feeds for accurate valuations
- **Chainlink Functions Verification**: Cryptographic proof validation for offchain computations
- **Cross-Chain Data Integrity**: Verifiable multi-chain data aggregation

For detailed security measures and implementation, see the [Security Measures section](docs/SHOGUN_CORE_AI_ARCHITECTURE.md#security-measures) in our architecture documentation.

## Vault Management

### Multi-Token Support
- USDC: Primary stablecoin for calculations
- WBTC: Bitcoin exposure with oracle pricing
- WETH: Ethereum exposure with real-time feeds
- LINK: Chainlink token integration

### Strategy Execution
- AI agent generates optimal strategies
- Risk model validates all proposals
- **Chainlink Functions provides offchain computation**
- Whitelisted contracts execute approved strategies
- Automatic harvesting and rebalancing
- Emergency exit capabilities for risk management

For detailed vault management flows and monitoring strategies, see the [Strategy Flow section](docs/SHOGUN_CORE_AI_ARCHITECTURE.md#strategy-flow) in our architecture documentation.

## Monitoring

shogun core ai monitors:
- Vault performance metrics
- Strategy execution status
- Oracle price feeds
- Liquidity events
- Volume spikes
- Rate changes
- Protocol health metrics
- Smart contract events
- Market conditions
- **Chainlink Functions task status**
- **Oracle health across networks**
- **Cross-chain data integrity**

For a comprehensive view of our monitoring system and real-time parameters, check the [Monitoring Parameters section](docs/SHOGUN_CORE_AI_ARCHITECTURE.md#monitoring-parameters) in our architecture documentation.

## License

MIT 
