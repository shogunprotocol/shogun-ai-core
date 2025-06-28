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
        end
        
        LLM --> Risk
        Risk --> Exec
        KB --> LLM
        Providers --> KB
    end
    
    subgraph Markets["Avalanche DeFi Markets"]
        DL --> |Monitor| AAVE[Aave V3]
        DL --> |Monitor| BENQI[Benqi]
        DL --> |Monitor| TJ[Trader Joe]
    end
```

## Strategy Flow

```mermaid
graph LR
    subgraph AaveV3["Aave V3 Strategy"]
        USDC[USDC] --> |Supply| AAVE_POOL[Aave Pool]
        AAVE_POOL --> |Borrow| WETH[WETH]
        WETH --> |Swap| USDC
    end
    
    subgraph Benqi["Benqi Strategy"]
        AVAX[AVAX] --> |Supply| BENQI_POOL[Benqi Pool]
        BENQI_POOL --> |Earn| QI[QI Tokens]
    end
    
    subgraph TraderJoe["Trader Joe Strategy"]
        USDC --> |Add Liquidity| TJ_POOL[Trader Joe Pool]
        TJ_POOL --> |Earn| JOE[JOE Tokens]
    end
    
    ShogunCoreAI[shogun core ai] --> |Execute| AaveV3
    ShogunCoreAI --> |Execute| Benqi
    ShogunCoreAI --> |Execute| TraderJoe
```

## Data Flow

```mermaid
sequenceDiagram
    participant ShogunCoreAI as shogun core ai
    participant DL as DefiLlama Provider
    
    loop Every Block
        ShogunCoreAI->>DL: Fetch Avalanche DeFi Data
        ShogunCoreAI->>DL: Monitor Protocol Events
        
        DL-->>ShogunCoreAI: Market Data
        DL-->>ShogunCoreAI: Unusual Events
        
        ShogunCoreAI->>ShogunCoreAI: Generate Strategy
        ShogunCoreAI->>ShogunCoreAI: Assess Risk
        ShogunCoreAI->>ShogunCoreAI: Execute if Safe
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
        
        TVL --> Score[Risk Score]
        LIQ --> Score
        VOL --> Score
        EXP --> Score
        
        Score --> Decision{Execute?}
        Decision -->|Safe| Execute
        Decision -->|Risky| Reject
    end
```

## Strategy Components

### Aave V3 Strategy
- Monitor lending and borrowing rates on Aave V3
- Track liquidity utilization across pools
- Calculate optimal supply/borrow ratios
- Monitor liquidation risks

### Benqi Strategy
- Monitor Benqi lending protocol rates
- Track QI token rewards and emissions
- Calculate optimal lending positions
- Monitor protocol health metrics

### Trader Joe Strategy
- Monitor Trader Joe DEX liquidity pools
- Track JOE token rewards and farming
- Calculate optimal liquidity provision
- Monitor impermanent loss risks

## Monitoring Parameters

```mermaid
graph LR
    subgraph Monitoring["Real-time Monitoring"]
        LIQ[Liquidity Events]
        VOL[Volume Spikes]
        RATE[Rate Changes]
        HEALTH[Protocol Health]
        
        LIQ --> Alert[Alert System]
        VOL --> Alert
        RATE --> Alert
        HEALTH --> Alert
    end
```

## Configuration

The shogun core ai is configured through `configs/config.yaml` with the following key components:

- RPC endpoints for Avalanche mainnet and Fuji testnet
- Protocol addresses for Aave V3, Benqi, and Trader Joe
- Risk parameters and thresholds
- Monitoring configurations
- LLM settings for strategy generation

## Security Measures

```mermaid
graph TD
    subgraph Security["Security Measures"]
        RATE[Rate Limiting]
        SLIP[Slippage Protection]
        GAS[Gas Optimization]
        MULTI[Multi-sig Execution]
        
        RATE --> Safe[Safe Execution]
        SLIP --> Safe
        GAS --> Safe
        MULTI --> Safe
    end
``` 