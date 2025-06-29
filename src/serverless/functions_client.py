"""
Chainlink Functions client for offchain computation.
Interfaces specifically with Chainlink Functions for verifiable offchain computation.
"""

import requests
import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChainlinkRequest:
    """Chainlink Functions request."""
    source: str  # JavaScript source code
    secrets: Dict[str, str]  # Encrypted secrets
    args: List[str]  # Function arguments
    subscription_id: int
    gas_limit: int = 300000
    gas_price: Optional[int] = None

@dataclass
class ChainlinkResponse:
    """Chainlink Functions response."""
    request_id: str
    result: bytes  # Encoded result
    error: Optional[str] = None
    status: str = 'pending'

class ChainlinkFunctionsClient:
    """
    Client for Chainlink Functions offchain computation.
    
    This integrates with Chainlink Functions to run:
    - Strategy risk scoring for multi-token vault
    - Cross-chain APY aggregation for strategy selection
    - Portfolio allocation optimization
    - Oracle health monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Chainlink Functions client."""
        self.config = config
        self.network = config.get('network', 'avalanche')
        
        # Chainlink Functions configuration
        self.functions_config = {
            'avalanche': {
                'router': '0x9f4b2c2380dd6f6d66c983f0c6b88b7a1b3c8d8c',
                'don_id': 'fun-avalanche-fuji-1'
            },
            'ethereum': {
                'router': '0x6E2dc0F9DB014aE19888F539E59285D2EA735a89',
                'don_id': 'fun-ethereum-mainnet-1'
            }
        }
        
        # Function source codes (in production, these would be deployed and referenced by ID)
        self.function_sources = {
            'strategy_risk_scoring': self._get_strategy_risk_scoring_source(),
            'cross_chain_apy': self._get_cross_chain_apy_source(),
            'allocation_optimization': self._get_allocation_optimization_source(),
            'oracle_health_check': self._get_oracle_health_check_source()
        }
    
    def run_strategy_risk_scoring(self, strategy_data: Dict[str, Any]) -> ChainlinkResponse:
        """
        Run risk scoring for a strategy using Chainlink Functions.
        
        Args:
            strategy_data: Strategy data including address, tokens, allocation, etc.
            
        Returns:
            ChainlinkResponse with risk score and verification
        """
        # Prepare arguments for Chainlink Functions
        args = [
            strategy_data.get('strategy_address', ''),
            json.dumps(strategy_data.get('tokens', [])),
            str(strategy_data.get('current_allocation', 0)),
            str(strategy_data.get('max_allocation', 0)),
            str(strategy_data.get('risk_score', 0))
        ]
        
        request = ChainlinkRequest(
            source=self.function_sources['strategy_risk_scoring'],
            secrets={},  # No secrets needed for this function
            args=args,
            subscription_id=self.config.get('subscription_id')
        )
        
        return self._execute_chainlink_function(request)
    
    def fetch_cross_chain_apy(self, strategy_addresses: List[str]) -> ChainlinkResponse:
        """
        Fetch APY data for strategies across multiple chains.
        
        Args:
            strategy_addresses: List of strategy contract addresses
            
        Returns:
            ChainlinkResponse with aggregated APY data
        """
        args = [
            json.dumps(strategy_addresses),
            json.dumps(['avalanche', 'ethereum', 'polygon']),  # Target chains
            str(int(time.time()))
        ]
        
        request = ChainlinkRequest(
            source=self.function_sources['cross_chain_apy'],
            secrets={
                'DEFILLAMA_API_KEY': self.config.get('defillama_api_key', '')
            },
            args=args,
            subscription_id=self.config.get('subscription_id')
        )
        
        return self._execute_chainlink_function(request)
    
    def optimize_vault_allocation(self, vault_data: Dict[str, Any]) -> ChainlinkResponse:
        """
        Optimize vault allocation across strategies using Chainlink Functions.
        
        Args:
            vault_data: Vault data including current allocations, constraints, etc.
            
        Returns:
            ChainlinkResponse with optimal allocation proposal
        """
        args = [
            json.dumps(vault_data.get('current_allocations', {})),
            json.dumps(vault_data.get('strategy_constraints', {})),
            str(vault_data.get('total_value_locked', 0)),
            str(vault_data.get('risk_tolerance', 0.3))
        ]
        
        request = ChainlinkRequest(
            source=self.function_sources['allocation_optimization'],
            secrets={},
            args=args,
            subscription_id=self.config.get('subscription_id')
        )
        
        return self._execute_chainlink_function(request)
    
    def check_oracle_health(self, oracle_addresses: List[str]) -> ChainlinkResponse:
        """
        Check health of Chainlink oracles used by the vault.
        
        Args:
            oracle_addresses: List of oracle addresses to check
            
        Returns:
            ChainlinkResponse with oracle health status
        """
        args = [
            json.dumps(oracle_addresses),
            str(int(time.time())),
            str(self.config.get('oracle_deviation_threshold', 0.02))
        ]
        
        request = ChainlinkRequest(
            source=self.function_sources['oracle_health_check'],
            secrets={},
            args=args,
            subscription_id=self.config.get('subscription_id')
        )
        
        return self._execute_chainlink_function(request)
    
    def _execute_chainlink_function(self, request: ChainlinkRequest) -> ChainlinkResponse:
        """
        Execute a Chainlink Functions request.
        
        Args:
            request: The Chainlink Functions request
            
        Returns:
            ChainlinkResponse with results
        """
        try:
            # In production, this would use the Chainlink Functions SDK
            # For now, we'll simulate the API call
            
            # Prepare the request payload for Chainlink Functions
            payload = {
                'source': request.source,
                'secrets': request.secrets,
                'args': request.args,
                'subscriptionId': request.subscription_id,
                'gasLimit': request.gas_limit
            }
            
            if request.gas_price:
                payload['gasPrice'] = request.gas_price
            
            # Simulate Chainlink Functions execution
            # In production, this would be a real API call to Chainlink Functions
            logger.info(f"Executing Chainlink Function with {len(request.args)} arguments")
            
            # Simulate processing time
            time.sleep(0.1)
            
            # Generate a mock response (in production, this would come from Chainlink)
            request_id = f"req_{int(time.time() * 1000)}"
            
            # Parse the result based on function type
            if 'strategy_risk_scoring' in request.source:
                result = self._parse_risk_scoring_result(request.args)
            elif 'cross_chain_apy' in request.source:
                result = self._parse_apy_result(request.args)
            elif 'allocation_optimization' in request.source:
                result = self._parse_allocation_result(request.args)
            elif 'oracle_health_check' in request.source:
                result = self._parse_oracle_health_result(request.args)
            else:
                result = b'{"status": "unknown_function"}'
            
            return ChainlinkResponse(
                request_id=request_id,
                result=result,
                status='completed'
            )
            
        except Exception as e:
            logger.error(f"Error executing Chainlink Function: {e}")
            return ChainlinkResponse(
                request_id=f"error_{int(time.time() * 1000)}",
                result=b'{}',
                error=str(e),
                status='failed'
            )
    
    def _parse_risk_scoring_result(self, args: List[str]) -> bytes:
        """Parse risk scoring result."""
        strategy_address = args[0]
        tokens = json.loads(args[1])
        current_allocation = float(args[2])
        max_allocation = float(args[3])
        base_risk_score = float(args[4])
        
        # Calculate enhanced risk score based on allocation and tokens
        allocation_risk = min(current_allocation / max_allocation, 1.0) if max_allocation > 0 else 0
        token_diversity_risk = 1.0 - (len(tokens) / 10.0)  # More tokens = lower risk
        
        final_risk_score = (base_risk_score * 0.6 + allocation_risk * 0.3 + token_diversity_risk * 0.1)
        
        result = {
            'strategy_address': strategy_address,
            'risk_score': min(final_risk_score, 1.0),
            'risk_factors': {
                'base_risk': base_risk_score,
                'allocation_risk': allocation_risk,
                'diversity_risk': token_diversity_risk
            },
            'timestamp': int(time.time()),
            'verification_hash': hashlib.sha256(str(final_risk_score).encode()).hexdigest()
        }
        
        return json.dumps(result).encode()
    
    def _parse_apy_result(self, args: List[str]) -> bytes:
        """Parse cross-chain APY result."""
        strategy_addresses = json.loads(args[0])
        chains = json.loads(args[1])
        
        # Simulate APY data from multiple chains
        apy_data = {}
        for strategy in strategy_addresses:
            apy_data[strategy] = {
                'avalanche': 0.08 + (hash(strategy) % 100) / 1000,  # 8-18% APY
                'ethereum': 0.06 + (hash(strategy) % 80) / 1000,   # 6-14% APY
                'polygon': 0.10 + (hash(strategy) % 120) / 1000    # 10-22% APY
            }
        
        result = {
            'apy_data': apy_data,
            'aggregated_apy': {chain: sum(data[chain] for data in apy_data.values()) / len(apy_data) for chain in chains},
            'timestamp': int(time.time()),
            'verification_hash': hashlib.sha256(json.dumps(apy_data, sort_keys=True).encode()).hexdigest()
        }
        
        return json.dumps(result).encode()
    
    def _parse_allocation_result(self, args: List[str]) -> bytes:
        """Parse allocation optimization result."""
        current_allocations = json.loads(args[0])
        constraints = json.loads(args[1])
        tvl = float(args[2])
        risk_tolerance = float(args[3])
        
        # Simulate optimization algorithm
        strategies = list(constraints.keys())
        optimal_allocations = {}
        
        for strategy in strategies:
            max_alloc = constraints[strategy].get('max_allocation', 0.4)
            risk_score = constraints[strategy].get('risk_score', 0.3)
            
            # Adjust allocation based on risk tolerance
            optimal_alloc = max_alloc * (1 - risk_score * risk_tolerance)
            optimal_allocations[strategy] = min(optimal_alloc, max_alloc)
        
        result = {
            'optimal_allocations': optimal_allocations,
            'expected_return': sum(alloc * 0.08 for alloc in optimal_allocations.values()),  # 8% avg return
            'risk_score': sum(alloc * constraints[strategy].get('risk_score', 0.3) for strategy, alloc in optimal_allocations.items()),
            'timestamp': int(time.time()),
            'verification_hash': hashlib.sha256(json.dumps(optimal_allocations, sort_keys=True).encode()).hexdigest()
        }
        
        return json.dumps(result).encode()
    
    def _parse_oracle_health_result(self, args: List[str]) -> bytes:
        """Parse oracle health check result."""
        oracle_addresses = json.loads(args[0])
        timestamp = int(args[1])
        deviation_threshold = float(args[2])
        
        # Simulate oracle health checks
        oracle_status = {}
        for oracle in oracle_addresses:
            # Simulate price deviation check
            deviation = (hash(oracle) % 100) / 10000  # 0-1% deviation
            oracle_status[oracle] = {
                'healthy': deviation < deviation_threshold,
                'deviation': deviation,
                'last_update': timestamp - (hash(oracle) % 300),  # Within 5 minutes
                'confidence': 0.95 + (hash(oracle) % 50) / 1000  # 95-100% confidence
            }
        
        result = {
            'oracle_status': oracle_status,
            'overall_health': all(status['healthy'] for status in oracle_status.values()),
            'timestamp': timestamp,
            'verification_hash': hashlib.sha256(json.dumps(oracle_status, sort_keys=True).encode()).hexdigest()
        }
        
        return json.dumps(result).encode()
    
    def _get_strategy_risk_scoring_source(self) -> str:
        """Get the JavaScript source code for strategy risk scoring."""
        return '''
        const { Functions } = require("@chainlink/functions-toolkit");
        
        const execute = async (args) => {
            const strategyAddress = args[0];
            const tokens = JSON.parse(args[1]);
            const currentAllocation = parseFloat(args[2]);
            const maxAllocation = parseFloat(args[3]);
            const baseRiskScore = parseFloat(args[4]);
            
            // Calculate risk factors
            const allocationRisk = Math.min(currentAllocation / maxAllocation, 1.0);
            const tokenDiversityRisk = 1.0 - (tokens.length / 10.0);
            
            // Weighted risk calculation
            const finalRiskScore = (baseRiskScore * 0.6 + allocationRisk * 0.3 + tokenDiversityRisk * 0.1);
            
            return Functions.encodeString(JSON.stringify({
                strategy_address: strategyAddress,
                risk_score: Math.min(finalRiskScore, 1.0),
                risk_factors: {
                    base_risk: baseRiskScore,
                    allocation_risk: allocationRisk,
                    diversity_risk: tokenDiversityRisk
                },
                timestamp: Date.now()
            }));
        };
        '''
    
    def _get_cross_chain_apy_source(self) -> str:
        """Get the JavaScript source code for cross-chain APY fetching."""
        return '''
        const { Functions } = require("@chainlink/functions-toolkit");
        
        const execute = async (args) => {
            const strategyAddresses = JSON.parse(args[0]);
            const chains = JSON.parse(args[1]);
            const timestamp = parseInt(args[2]);
            
            // Fetch APY data from DeFiLlama API
            const apyData = {};
            for (const strategy of strategyAddresses) {
                apyData[strategy] = {};
                for (const chain of chains) {
                    // In production, this would make real API calls
                    const response = await Functions.makeHttpRequest({
                        url: `https://api.llama.fi/protocol/${strategy}`,
                        method: "GET"
                    });
                    
                    if (response.data && response.data.apy) {
                        apyData[strategy][chain] = response.data.apy;
                    } else {
                        apyData[strategy][chain] = 0.08; // Default 8% APY
                    }
                }
            }
            
            return Functions.encodeString(JSON.stringify({
                apy_data: apyData,
                timestamp: timestamp
            }));
        };
        '''
    
    def _get_allocation_optimization_source(self) -> str:
        """Get the JavaScript source code for allocation optimization."""
        return '''
        const { Functions } = require("@chainlink/functions-toolkit");
        
        const execute = async (args) => {
            const currentAllocations = JSON.parse(args[0]);
            const constraints = JSON.parse(args[1]);
            const tvl = parseFloat(args[2]);
            const riskTolerance = parseFloat(args[3]);
            
            // Simple optimization algorithm
            const strategies = Object.keys(constraints);
            const optimalAllocations = {};
            
            for (const strategy of strategies) {
                const maxAlloc = constraints[strategy].max_allocation || 0.4;
                const riskScore = constraints[strategy].risk_score || 0.3;
                
                // Adjust allocation based on risk tolerance
                const optimalAlloc = maxAlloc * (1 - riskScore * riskTolerance);
                optimalAllocations[strategy] = Math.min(optimalAlloc, maxAlloc);
            }
            
            return Functions.encodeString(JSON.stringify({
                optimal_allocations: optimalAllocations,
                expected_return: Object.values(optimalAllocations).reduce((sum, alloc) => sum + alloc * 0.08, 0),
                timestamp: Date.now()
            }));
        };
        '''
    
    def _get_oracle_health_check_source(self) -> str:
        """Get the JavaScript source code for oracle health checking."""
        return '''
        const { Functions } = require("@chainlink/functions-toolkit");
        
        const execute = async (args) => {
            const oracleAddresses = JSON.parse(args[0]);
            const timestamp = parseInt(args[1]);
            const deviationThreshold = parseFloat(args[2]);
            
            const oracleStatus = {};
            
            for (const oracle of oracleAddresses) {
                // Check oracle health by comparing recent prices
                // In production, this would query the actual oracle contracts
                const response = await Functions.makeHttpRequest({
                    url: `https://api.chainlink.com/oracle/${oracle}/latest`,
                    method: "GET"
                });
                
                if (response.data) {
                    const deviation = response.data.deviation || 0;
                    oracleStatus[oracle] = {
                        healthy: deviation < deviationThreshold,
                        deviation: deviation,
                        last_update: response.data.timestamp,
                        confidence: response.data.confidence || 0.95
                    };
                }
            }
            
            return Functions.encodeString(JSON.stringify({
                oracle_status: oracleStatus,
                overall_health: Object.values(oracleStatus).every(status => status.healthy),
                timestamp: timestamp
            }));
        };
        '''
    
    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the status of a Chainlink Functions request.
        
        Args:
            request_id: The request ID to check
            
        Returns:
            Dict with request status information
        """
        # In production, this would query the Chainlink Functions API
        return {
            'request_id': request_id,
            'status': 'completed',
            'timestamp': int(time.time())
        } 