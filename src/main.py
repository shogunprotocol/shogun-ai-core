"""
Main orchestration module for the Shogun Agent.
Coordinates data fetching, strategy planning, risk assessment, and execution.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

from agent.llm_planner import LLMPlanner
from agent.risk_model import RiskModel
from agent.knowledge_box import KnowledgeBox
from execution.strategy_executor import StrategyExecutor
from data_providers.aave import AaveProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShogunAgent:
    def __init__(self, config_path: str = "configs/config.yaml"):
        """Initialize the Shogun Agent with configuration and components."""
        self.config = self._load_config(config_path)
        self.llm_planner = LLMPlanner(self.config['llm'])
        self.risk_model = RiskModel()
        self.knowledge_box = KnowledgeBox()
        self.strategy_executor = StrategyExecutor(self.config['execution'])
        
        # Initialize data providers
        self.data_providers = {
            'aave': AaveProvider(self.config['protocols']['aave']),
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def fetch_market_data(self) -> Dict[str, Any]:
        """Fetch current market data from all providers."""
        market_data = {}
        for provider_name, provider in self.data_providers.items():
            try:
                market_data[provider_name] = provider.fetch_data()
            except Exception as e:
                logger.error(f"Error fetching data from {provider_name}: {e}")
        return market_data

    def run(self):
        """Main execution loop for the agent."""
        try:
            # 1. Fetch current market data
            market_data = self.fetch_market_data()
            
            # 2. Get historical context
            historical_context = self.knowledge_box.get_context()
            
            # 3. Generate strategy using LLM
            strategy = self.llm_planner.generate_strategy(
                market_data=market_data,
                historical_context=historical_context
            )
            
            # 4. Assess risk
            risk_score = self.risk_model.score_strategy(strategy)
            
            # 5. Execute if risk score is acceptable
            if risk_score >= self.config['risk']['min_confidence_score']:
                self.strategy_executor.execute(strategy)
                logger.info(f"Strategy executed successfully with risk score: {risk_score}")
            else:
                logger.warning(f"Strategy rejected due to high risk. Score: {risk_score}")
                
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            raise

def main():
    """Entry point for the Shogun Agent."""
    agent = ShogunAgent()
    agent.run()

if __name__ == "__main__":
    main() 