# AI vaults Agent

An AI-powered DeFi strategy agent that generates and executes vault strategies using LLM-based planning and risk assessment.

## Overview

AI vault Agent is a deterministic AI system that:
- Fetches real-time data from multiple DeFi protocols (Aave, Pendle, Lybra)
- Uses LLM-based planning to generate strategy recommendations
- Assesses risk using a trained machine learning model
- Executes approved strategies on-chain

## Project Structure

```
📁 ai-agent/
├── 📂 src/                    # Source code
│   ├── 📂 agent/             # Core agent logic
│   ├── 📂 data_providers/    # Protocol data fetching
│   ├── 📂 execution/         # On-chain execution
│   └── main.py               # Main orchestration
├── 📂 data/                  # Historical data
├── configs/                  # Configuration files
└── requirements.txt          # Dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
- Copy `.env.example` to `.env`
- Add your API keys and RPC endpoints

3. Run the agent:
```bash
python src/main.py
```

## Configuration

Edit `configs/config.yaml` to configure:
- RPC endpoints
- Vault addresses
- Risk thresholds
- Strategy parameters

## Security

- The agent uses deterministic logic with no randomness
- All strategies are risk-scored before execution
- Historical pattern matching helps prevent known risky scenarios

## License

MIT 
