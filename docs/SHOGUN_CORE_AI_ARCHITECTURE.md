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
            RS[Rootstock Provider]
            FS[Flow Strategy Provider]
            KP[KittyPunch Provider]
            BS[Blockscout Provider]
        end
        
        LLM --> Risk
        Risk --> Exec
        KB --> LLM
        Providers --> KB
    end
    
    subgraph Markets["DeFi Markets"]
        RS --> |Monitor| Rootstock
        FS --> |Monitor| Flow
        KP --> |Monitor| KittyPunch
    end
```

## Strategy Flow

```mermaid
graph LR
    subgraph Rootstock["Rootstock Strategy"]
        BTC[BTC] --> |Lend| SOV[Sovryn]
        SOV --> |Deposit| DLLR[DLLR/BTC Pool]
    end
    
    subgraph Flow["Flow Strategy"]
        FLOW[FLOW] --> |Borrow| MORE[MORE Markets]
        MORE --> |Lend| KP[KittyPunch]
        KP --> |Earn| KPTOKENS[KittyPunch Tokens]
    end
    
    ShogunCoreAI[shogun core ai] --> |Execute| Rootstock
    ShogunCoreAI --> |Execute| Flow
```

## Data Flow

```mermaid
sequenceDiagram
    participant ShogunCoreAI as shogun core ai
    participant RS as Rootstock Provider
    participant FS as Flow Strategy Provider
    participant KP as KittyPunch Provider
    participant BS as Blockscout Provider
    
    loop Every Block
        ShogunCoreAI->>RS: Fetch Rootstock Data
        ShogunCoreAI->>FS: Fetch Flow Strategy Data
        ShogunCoreAI->>KP: Fetch KittyPunch Data
        ShogunCoreAI->>BS: Monitor Events
        
        BS-->>ShogunCoreAI: Unusual Events
        RS-->>ShogunCoreAI: Pool Data
        FS-->>ShogunCoreAI: Vault Data
        KP-->>ShogunCoreAI: Lending Data
        
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

### Rootstock Strategy
- Monitor BTC lending rates on Sovryn
- Track DLLR/BTC pool liquidity
- Calculate optimal leverage ratios
- Monitor liquidation risks

### Flow Strategy
- Monitor MORE Markets borrowing rates
- Track KittyPunch lending pools
- Calculate token rewards
- Monitor protocol health

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

- RPC endpoints for Rootstock and Flow
- Protocol addresses for all integrations
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