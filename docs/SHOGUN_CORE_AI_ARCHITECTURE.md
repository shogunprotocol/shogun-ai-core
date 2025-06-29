# shogun core ai Architecture

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
        
        LLM --> Risk
        Risk --> Exec
        KB --> LLM
        Providers --> KB
    end
    
    subgraph Vault["Multi-Token Vault System"]
        MTV[MultiTokenVault.sol]
        ORACLE[Chainlink Oracle]
        STRATEGIES[Whitelisted Strategies]
        
        MTV --> ORACLE
        MTV --> STRATEGIES
    end
    
    Exec --> |Execute| MTV
```

## Strategy Flow

```mermaid
graph LR
    subgraph Vault["Multi-Token Vault"]
        USDC[USDC] --> |Deposit| MTV[MultiTokenVault]
        WBTC[WBTC] --> |Deposit| MTV
        WETH[WETH] --> |Deposit| MTV
        LINK[LINK] --> |Deposit| MTV
        
        MTV --> |Convert| USDC_EQ[USDC Equivalent]
    end
    
    subgraph Strategies["Whitelisted Strategies"]
        STRAT1[Strategy Contract 1]
        STRAT2[Strategy Contract 2]
        STRAT3[Strategy Contract 3]
        
        USDC_EQ --> |Allocate| STRAT1
        USDC_EQ --> |Allocate| STRAT2
        USDC_EQ --> |Allocate| STRAT3
    end
    
    subgraph AI["AI Agent"]
        LLM[LLM Planner]
        Risk[Risk Model]
        
        LLM --> |Generate| Strategy
        Risk --> |Validate| Strategy
    end
    
    AI --> |Execute| Strategies
```

## Data Flow

```mermaid
sequenceDiagram
    participant ShogunCoreAI as shogun core ai
    participant DL as DefiLlama Provider
    participant Vault as MultiTokenVault
    participant Oracle as Chainlink Oracle
    
    loop Every Block
        ShogunCoreAI->>DL: Fetch DeFi Market Data
        ShogunCoreAI->>Vault: Monitor Vault Status
        
        DL-->>ShogunCoreAI: Market Data
        Vault-->>ShogunCoreAI: Vault Metrics
        
        ShogunCoreAI->>Oracle: Get Token Prices
        Oracle-->>ShogunCoreAI: Price Feeds
        
        ShogunCoreAI->>ShogunCoreAI: Generate Strategy
        ShogunCoreAI->>ShogunCoreAI: Assess Risk
        ShogunCoreAI->>Vault: Execute if Safe
    end
```

## Risk Assessment

```mermaid
graph TD
    subgraph Risk["Risk Assessment"]
        TVL[TVL Check]
        LIQ[Liquidity Check]
        VOL[Volatility Check]
        EXP[Exposure Check]
        ORACLE[Oracle Health]
        
        TVL --> Score[Risk Score]
        LIQ --> Score
        VOL --> Score
        EXP --> Score
        ORACLE --> Score
        
        Score --> Decision{Execute?}
        Decision -->|Safe| Execute
        Decision -->|Risky| Reject
    end
```

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

### Token Management
- **USDC**: Primary stablecoin for calculations and pricing
- **WBTC**: Bitcoin exposure with real-time oracle pricing
- **WETH**: Ethereum exposure with reliable price feeds
- **LINK**: Chainlink token integration for oracle operations

## Monitoring Parameters

```mermaid
graph LR
    subgraph Monitoring["Real-time Monitoring"]
        VAULT[Vault Performance]
        STRATEGY[Strategy Status]
        ORACLE[Oracle Health]
        LIQ[Liquidity Events]
        VOL[Volume Spikes]
        RATE[Rate Changes]
        HEALTH[Protocol Health]
        
        VAULT --> Alert[Alert System]
        STRATEGY --> Alert
        ORACLE --> Alert
        LIQ --> Alert
        VOL --> Alert
        RATE --> Alert
        HEALTH --> Alert
    end
```

## Configuration

The shogun core ai is configured through `configs/config.yaml` with the following key components:

- RPC endpoints for Ethereum mainnet
- MultiTokenVault contract address
- Whitelisted strategy contract addresses
- Chainlink oracle addresses
- Risk parameters and thresholds
- Monitoring configurations
- LLM settings for strategy generation

## Security Measures

```mermaid
graph TD
    subgraph Security["Security Measures"]
        WHITELIST[Whitelisted Strategies]
        ORACLE[Oracle Integration]
        RATE[Rate Limiting]
        SLIP[Slippage Protection]
        GAS[Gas Optimization]
        MULTI[Multi-sig Execution]
        
        WHITELIST --> Safe[Safe Execution]
        ORACLE --> Safe
        RATE --> Safe
        SLIP --> Safe
        GAS --> Safe
        MULTI --> Safe
    end
``` 