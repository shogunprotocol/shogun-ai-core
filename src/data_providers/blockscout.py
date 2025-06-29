"""
Blockscout data provider.
Fetches transaction and contract interaction data from Blockscout.
"""

from typing import Dict, Any, List, Optional
import requests
from web3 import Web3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BlockscoutProvider:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Blockscout data provider with configuration."""
        self.api_url = config.get('api_url', 'https://api.snowtrace.io/api')
        self.web3 = Web3()
        
    def fetch_transaction_data(self, address: str) -> List[Dict[str, Any]]:
        """
        Fetch transaction history for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            List of transactions
        """
        endpoint = f"{self.api_url}/addresses/{address}/transactions"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []

    def fetch_contract_interactions(self, address: str) -> List[Dict[str, Any]]:
        """
        Fetch contract interaction history.
        
        Args:
            address: Contract address
            
        Returns:
            List of contract interactions
        """
        endpoint = f"{self.api_url}/addresses/{address}/transactions"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            logger.error(f"Error fetching contract interactions: {e}")
            return []

    def get_transaction_details(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details including internal transactions and logs
        """
        try:
            # Get basic transaction info
            tx_endpoint = f"{self.api_url}/transactions/{tx_hash}"
            tx_response = requests.get(tx_endpoint)
            tx_response.raise_for_status()
            tx_data = tx_response.json()

            # Get internal transactions
            internal_tx_endpoint = f"{self.api_url}/transactions/{tx_hash}/internal-transactions"
            internal_tx_response = requests.get(internal_tx_endpoint)
            internal_tx_response.raise_for_status()
            internal_txs = internal_tx_response.json().get('items', [])

            # Get transaction logs
            logs_endpoint = f"{self.api_url}/transactions/{tx_hash}/logs"
            logs_response = requests.get(logs_endpoint)
            logs_response.raise_for_status()
            logs = logs_response.json().get('items', [])

            return {
                'transaction': tx_data,
                'internal_transactions': internal_txs,
                'logs': logs
            }
        except Exception as e:
            logger.error(f"Error fetching transaction details: {e}")
            return None

    def monitor_liquidity_events(self, contract_address: str, time_window: int = 3600) -> List[Dict[str, Any]]:
        """
        Monitor liquidity-related events for a contract.
        
        Args:
            contract_address: Contract address to monitor
            time_window: Time window in seconds to look back
            
        Returns:
            List of liquidity events
        """
        try:
            # Get recent transactions
            endpoint = f"{self.api_url}/addresses/{contract_address}/transactions"
            response = requests.get(endpoint)
            response.raise_for_status()
            transactions = response.json().get('items', [])

            # Filter for liquidity events
            liquidity_events = []
            for tx in transactions:
                # Check if transaction is within time window
                tx_time = datetime.fromtimestamp(tx.get('timestamp', 0))
                if datetime.now() - tx_time > timedelta(seconds=time_window):
                    continue

                # Get detailed transaction info
                tx_details = self.get_transaction_details(tx['hash'])
                if not tx_details:
                    continue

                # Look for liquidity-related events in logs
                for log in tx_details.get('logs', []):
                    if any(keyword in log.get('topics', [])[0].lower() for keyword in 
                          ['liquidity', 'addliquidity', 'removeliquidity', 'swap']):
                        liquidity_events.append({
                            'transaction': tx,
                            'log': log,
                            'timestamp': tx_time
                        })

            return liquidity_events
        except Exception as e:
            logger.error(f"Error monitoring liquidity events: {e}")
            return []

    def detect_unusual_activity(self, address: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect unusual transaction patterns.
        
        Args:
            address: Address to monitor
            threshold: Standard deviations threshold for unusual activity
            
        Returns:
            List of unusual transactions
        """
        try:
            transactions = self.fetch_transaction_data(address)
            if not transactions:
                return []

            # Calculate transaction value statistics
            values = [float(tx.get('value', 0)) for tx in transactions]
            mean = sum(values) / len(values)
            std_dev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

            # Find unusual transactions
            unusual_txs = []
            for tx in transactions:
                value = float(tx.get('value', 0))
                if abs(value - mean) > threshold * std_dev:
                    unusual_txs.append({
                        'transaction': tx,
                        'deviation': abs(value - mean) / std_dev
                    })

            return unusual_txs
        except Exception as e:
            logger.error(f"Error detecting unusual activity: {e}")
            return [] 