"""
Flow Strategy protocol data provider.
Fetches vault and protocol data from Flow Strategy.
"""

from typing import Dict, Any
import requests
from web3 import Web3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FlowStrategyProvider:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Flow Strategy data provider with configuration."""
        self.vault_address = config['vault_address']
        self.rpc_url = config.get('rpc_url', 'https://flow-mainnet.g.alchemy.com/v2/')
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Flow RPC")

    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch current data from Flow Strategy protocol.
        
        Returns:
            Dict containing vault data, APRs, and other relevant information
        """
        try:
            # Fetch vault data
            vault_data = self._fetch_vault_data()
            
            # Fetch strategy data
            strategy_data = self._fetch_strategy_data()
            
            # Calculate APRs
            aprs = self._calculate_aprs(vault_data, strategy_data)
            
            return {
                "vault_data": vault_data,
                "strategy_data": strategy_data,
                "aprs": aprs,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Flow Strategy data: {e}")
            raise

    def _fetch_vault_data(self) -> Dict[str, Any]:
        """Fetch vault-specific data from Flow Strategy."""
        try:
            # Get vault contract
            vault_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.vault_address),
                abi=self._get_vault_abi()
            )
            
            # Fetch vault state
            total_assets = vault_contract.functions.totalAssets().call()
            total_supply = vault_contract.functions.totalSupply().call()
            available_liquidity = vault_contract.functions.availableLiquidity().call()
            
            return {
                "total_assets": total_assets,
                "total_supply": total_supply,
                "available_liquidity": available_liquidity,
                "last_update_timestamp": self._get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error fetching vault data: {e}")
            return {}

    def _fetch_strategy_data(self) -> Dict[str, Any]:
        """Fetch strategy-specific data."""
        try:
            # Get strategy contract
            strategy_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.vault_address),
                abi=self._get_strategy_abi()
            )
            
            # Fetch strategy state
            total_value_locked = strategy_contract.functions.totalValueLocked().call()
            performance_fee = strategy_contract.functions.performanceFee().call()
            management_fee = strategy_contract.functions.managementFee().call()
            
            return {
                "total_value_locked": total_value_locked,
                "performance_fee": performance_fee,
                "management_fee": management_fee,
                "last_update_timestamp": self._get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error fetching strategy data: {e}")
            return {}

    def _calculate_aprs(self, vault_data: Dict[str, Any], strategy_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate APRs based on vault and strategy data."""
        try:
            # Base rates
            base_rate = 0.08  # 8% base rate
            tvl_multiplier = 0.0001  # 0.01% per $1M TVL
            
            # Calculate rates based on TVL
            tvl = strategy_data.get('total_value_locked', 0)
            tvl_bonus = tvl * tvl_multiplier
            
            # Calculate final rates
            apr = base_rate + tvl_bonus
            
            return {
                "base_apr": base_rate,
                "tvl_bonus": tvl_bonus,
                "total_apr": apr,
                "performance_fee": strategy_data.get('performance_fee', 0),
                "management_fee": strategy_data.get('management_fee', 0)
            }
        except Exception as e:
            logger.error(f"Error calculating APRs: {e}")
            return {}

    def _get_current_timestamp(self) -> int:
        """Get current block timestamp."""
        try:
            return self.w3.eth.get_block('latest')['timestamp']
        except Exception as e:
            logger.error(f"Error getting timestamp: {e}")
            return int(datetime.now().timestamp())

    def _get_vault_abi(self) -> list:
        """Get the ABI for the vault contract."""
        # TODO: Implement proper ABI loading
        return []

    def _get_strategy_abi(self) -> list:
        """Get the ABI for the strategy contract."""
        # TODO: Implement proper ABI loading
        return [] 