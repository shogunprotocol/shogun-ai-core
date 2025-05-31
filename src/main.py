"""
Main orchestration module for the Shogun Agent.
Coordinates data fetching, strategy planning, risk assessment, and execution.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

from agent.llm_planner import LLMPlanner
from agent.risk_model import RiskModel
from agent.knowledge_box import KnowledgeBox
from execution.strategy_executor import StrategyExecutor
from data_providers.rootstock import RootstockProvider
from data_providers.blockscout import BlockscoutProvider
from data_providers.flow_strategy import FlowStrategyProvider
from data_providers.kitty_punch import KittyPunchProvider

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
            'rootstock': RootstockProvider(self.config['protocols']['rootstock']),
            'blockscout': BlockscoutProvider(self.config['providers']['blockscout']),
            'flow_strategy': FlowStrategyProvider(self.config['protocols']['flow_strategy']),
            'kitty_punch': KittyPunchProvider(self.config['protocols']['kitty_punch'])
        }
        
        # Initialize monitoring targets
        self.monitoring_targets = self.config.get('monitoring', {}).get('targets', [])

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

    def monitor_protocol_activity(self) -> List[Dict[str, Any]]:
        """
        Monitor protocol activity for unusual events and changes.
        
        Returns:
            List of detected unusual events
        """
        unusual_events = []
        
        for target in self.monitoring_targets:
            try:
                # Monitor liquidity events
                liquidity_events = self.data_providers['blockscout'].monitor_liquidity_events(
                    target['address'],
                    time_window=target.get('time_window', 3600)
                )
                
                # Detect unusual activity
                unusual_activity = self.data_providers['blockscout'].detect_unusual_activity(
                    target['address'],
                    threshold=target.get('threshold', 2.0)
                )
                
                if liquidity_events or unusual_activity:
                    unusual_events.append({
                        'target': target['address'],
                        'liquidity_events': liquidity_events,
                        'unusual_activity': unusual_activity
                    })
                    
            except Exception as e:
                logger.error(f"Error monitoring target {target['address']}: {e}")
                
        return unusual_events

    def run(self):
        """Main execution loop for the agent."""
        try:
            # 1. Fetch current market data
            market_data = self.fetch_market_data()
            
            # 2. Monitor protocol activity
            unusual_events = self.monitor_protocol_activity()
            if unusual_events:
                logger.warning(f"Detected unusual events: {unusual_events}")
                # Update market data with unusual events
                market_data['unusual_events'] = unusual_events
            
            # 3. Get historical context
            historical_context = self.knowledge_box.get_context()
            
            # 4. Generate strategy using LLM
            strategy = self.llm_planner.generate_strategy(
                market_data=market_data,
                historical_context=historical_context
            )
            
            # 5. Assess risk
            risk_score = self.risk_model.score_strategy(strategy)
            
            # 6. Execute if risk score is acceptable
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