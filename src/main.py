"""
Main orchestration module for the shogun core ai.
Coordinates data fetching, strategy planning, risk assessment, and execution for Avalanche DeFi protocols.
"""

import yaml
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from agent.llm_planner import LLMPlanner
from agent.risk_model import RiskModel
from agent.knowledge_box import KnowledgeBox
from execution.strategy_executor import StrategyExecutor
from data_providers.defillama_provider import DefiLlamaProvider
from serverless.compute_engine import ChainlinkComputeEngine
from serverless.verification import VerificationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShogunCoreAI:
    def __init__(self, config_path: str = "configs/config.yaml"):
        """Initialize the shogun core ai with configuration and components."""
        self.config = self._load_config(config_path)
        self.llm_planner = LLMPlanner(self.config['llm'])
        self.risk_model = RiskModel()
        self.knowledge_box = KnowledgeBox()
        self.strategy_executor = StrategyExecutor(self.config['execution'])
        
        # Initialize Chainlink Functions components
        self.chainlink_engine = ChainlinkComputeEngine(self.config.get('chainlink_functions', {}))
        self.verification_engine = VerificationEngine(self.config.get('chainlink_functions', {}))
        
        # Initialize data providers for Avalanche
        self.data_providers = {
            'defillama': DefiLlamaProvider(self.config['providers']['defillama']),
        }
        
        # Initialize monitoring targets for Avalanche protocols
        self.monitoring_targets = self.config.get('monitoring', {}).get('targets', [])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def fetch_market_data(self) -> Dict[str, Any]:
        """Fetch current market data from Avalanche DeFi protocols."""
        market_data = {}
        for provider_name, provider in self.data_providers.items():
            try:
                market_data[provider_name] = provider.fetch_data()
            except Exception as e:
                logger.error(f"Error fetching data from {provider_name}: {e}")
        return market_data

    def monitor_protocol_activity(self) -> List[Dict[str, Any]]:
        """
        Monitor Avalanche protocol activity for unusual events and changes.
        
        Returns:
            List of detected unusual events
        """
        unusual_events = []
        
        for target in self.monitoring_targets:
            try:
                # Monitor liquidity events on Avalanche
                liquidity_events = self.data_providers['defillama'].monitor_liquidity_events(
                    target['address'],
                    time_window=target.get('time_window', 3600)
                )
                
                # Detect unusual activity
                unusual_activity = self.data_providers['defillama'].detect_unusual_activity(
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

    async def assess_strategy_risk_chainlink(self, strategy_data: Dict[str, Any]) -> float:
        """
        Assess strategy risk using Chainlink Functions.
        
        Args:
            strategy_data: The strategy data to assess
            
        Returns:
            float: Risk score from Chainlink Functions
        """
        try:
            # Submit strategy risk scoring task to Chainlink Functions
            task_id = await self.chainlink_engine.submit_strategy_risk_scoring_task(
                strategy_data,
                callback=self._on_strategy_risk_complete
            )
            
            logger.info(f"Submitted Chainlink Functions strategy risk scoring task: {task_id}")
            
            # Wait for completion (in production, this would be async)
            # For now, we'll use a simple polling approach
            while True:
                status = self.chainlink_engine.get_task_status(task_id)
                if status['status'] == 'completed':
                    result_data = status['result']
                    if result_data:
                        import json
                        result = json.loads(result_data)
                        risk_score = result.get('risk_score', 0.5)
                        logger.info(f"Chainlink Functions risk score: {risk_score}")
                        return risk_score
                elif status['status'] == 'failed':
                    logger.warning("Chainlink Functions risk scoring failed, falling back to local model")
                    return self.risk_model.score_strategy(strategy_data)
                
                await asyncio.sleep(1)  # Poll every second
                
        except Exception as e:
            logger.error(f"Error in Chainlink Functions risk assessment: {e}")
            # Fallback to local risk model
            return self.risk_model.score_strategy(strategy_data)

    async def _on_strategy_risk_complete(self, response):
        """Callback when Chainlink Functions strategy risk scoring completes."""
        try:
            # Parse the Chainlink Functions response
            result_data = response.result.decode() if response.result else None
            if result_data:
                import json
                result = json.loads(result_data)
                risk_score = result.get('risk_score')
                verification_hash = result.get('verification_hash')
                
                if risk_score and verification_hash:
                    # Bridge the verified risk score onchain
                    strategy_address = result.get('strategy_address')
                    tx_hash = self.verification_engine.bridge_risk_score_onchain(
                        risk_score, verification_hash, {'strategy_address': strategy_address}
                    )
                    logger.info(f"Strategy risk score bridged onchain: {tx_hash}")
                
        except Exception as e:
            logger.error(f"Error in strategy risk completion callback: {e}")

    async def optimize_vault_allocation_chainlink(self, vault_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Optimize vault allocation using Chainlink Functions.
        
        Args:
            vault_data: Vault data including current allocations, constraints, etc.
            
        Returns:
            Dict: Optimal allocation proposal
        """
        try:
            # Submit allocation optimization task to Chainlink Functions
            task_id = await self.chainlink_engine.submit_allocation_optimization_task(
                vault_data,
                callback=self._on_allocation_complete
            )
            
            logger.info(f"Submitted Chainlink Functions allocation optimization task: {task_id}")
            
            # Wait for completion
            while True:
                status = self.chainlink_engine.get_task_status(task_id)
                if status['status'] == 'completed':
                    result_data = status['result']
                    if result_data:
                        import json
                        result = json.loads(result_data)
                        allocation = result.get('optimal_allocations', {})
                        logger.info(f"Chainlink Functions allocation optimization complete")
                        return allocation
                elif status['status'] == 'failed':
                    logger.warning("Chainlink Functions allocation optimization failed")
                    return {}
                
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in Chainlink Functions allocation optimization: {e}")
            return {}

    async def _on_allocation_complete(self, response):
        """Callback when Chainlink Functions allocation optimization completes."""
        try:
            result_data = response.result.decode() if response.result else None
            if result_data:
                import json
                result = json.loads(result_data)
                allocation = result.get('optimal_allocations', {})
                verification_hash = result.get('verification_hash')
                
                if allocation and verification_hash:
                    # Bridge allocation proposal onchain
                    tx_hash = self.verification_engine.bridge_allocation_proposal_onchain(
                        allocation, verification_hash, 'vault_001'
                    )
                    logger.info(f"Allocation proposal bridged onchain: {tx_hash}")
                
        except Exception as e:
            logger.error(f"Error in allocation completion callback: {e}")

    async def check_oracle_health_chainlink(self, oracle_addresses: List[str]) -> Dict[str, Any]:
        """
        Check oracle health using Chainlink Functions.
        
        Args:
            oracle_addresses: List of oracle addresses to check
            
        Returns:
            Dict: Oracle health status
        """
        try:
            # Submit oracle health check task to Chainlink Functions
            task_id = await self.chainlink_engine.submit_oracle_health_check_task(
                oracle_addresses
            )
            
            logger.info(f"Submitted Chainlink Functions oracle health check task: {task_id}")
            
            # Wait for completion
            while True:
                status = self.chainlink_engine.get_task_status(task_id)
                if status['status'] == 'completed':
                    result_data = status['result']
                    if result_data:
                        import json
                        result = json.loads(result_data)
                        logger.info(f"Chainlink Functions oracle health check complete")
                        return result
                elif status['status'] == 'failed':
                    logger.warning("Chainlink Functions oracle health check failed")
                    return {}
                
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in Chainlink Functions oracle health check: {e}")
            return {}

    async def run(self):
        """Main execution loop for the agent."""
        try:
            # 1. Fetch current market data from Avalanche
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
            
            # 5. Assess risk using Chainlink Functions
            risk_score = await self.assess_strategy_risk_chainlink(strategy)
            
            # 6. Execute if risk score is acceptable
            if risk_score >= self.config['risk']['min_confidence_score']:
                self.strategy_executor.execute(strategy)
                logger.info(f"Strategy executed successfully with risk score: {risk_score}")
            else:
                logger.warning(f"Strategy rejected due to high risk. Score: {risk_score}")
                
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            raise

    async def shutdown(self):
        """Shutdown the agent gracefully."""
        logger.info("Shutting down Shogun Core AI...")
        await self.chainlink_engine.shutdown()
        logger.info("Shutdown complete")

def main():
    """Entry point for the shogun core ai."""
    agent = ShogunCoreAI()
    
    try:
        # Run the agent
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        asyncio.run(agent.shutdown())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        asyncio.run(agent.shutdown())

if __name__ == "__main__":
    main() 