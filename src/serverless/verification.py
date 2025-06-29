"""
Verification engine for offchain computation results.
Handles cryptographic proof verification and onchain bridging.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

@dataclass
class VerificationResult:
    """Result of a verification operation."""
    verified: bool
    proof_hash: str
    timestamp: int
    details: Dict[str, Any]

@dataclass
class OnchainBridge:
    """Configuration for bridging results onchain."""
    contract_address: str
    abi: List[Dict[str, Any]]
    gas_limit: int = 500000
    gas_price: Optional[int] = None

class VerificationEngine:
    """
    Engine for verifying offchain computation results and bridging them onchain.
    
    Provides:
    - Cryptographic proof verification
    - Result integrity validation
    - Onchain bridging to smart contracts
    - Audit trail for computations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the verification engine."""
        self.config = config
        
        # Web3 setup for onchain operations
        self.w3 = Web3(Web3.HTTPProvider(config.get('rpc_url')))
        self.account = Account.from_key(config.get('private_key'))
        
        # Bridge contracts
        self.bridges = {
            'risk_scoring': OnchainBridge(
                contract_address=config.get('contracts', {}).get('risk_scoring'),
                abi=config.get('abis', {}).get('risk_scoring', [])
            ),
            'allocation': OnchainBridge(
                contract_address=config.get('contracts', {}).get('allocation'),
                abi=config.get('abis', {}).get('allocation', [])
            ),
            'market_data': OnchainBridge(
                contract_address=config.get('contracts', {}).get('market_data'),
                abi=config.get('abis', {}).get('market_data', [])
            )
        }
        
        # Verification settings
        self.verification_timeout = config.get('verification_timeout', 300)
        self.max_retries = config.get('max_retries', 3)
        
        # Audit trail
        self.verification_history: List[Dict[str, Any]] = []
    
    def verify_computation_proof(self, result: Dict[str, Any], proof: str) -> VerificationResult:
        """
        Verify the cryptographic proof of an offchain computation.
        
        Args:
            result: The computation result
            proof: The cryptographic proof
            
        Returns:
            VerificationResult with verification status
        """
        try:
            # Create hash of the result
            result_hash = self._hash_result(result)
            
            # Verify the proof matches the result
            if self._verify_proof_signature(result_hash, proof):
                verification_result = VerificationResult(
                    verified=True,
                    proof_hash=result_hash,
                    timestamp=int(time.time()),
                    details={
                        'result_type': result.get('type'),
                        'computation_id': result.get('computation_id'),
                        'model_version': result.get('model_version')
                    }
                )
                
                # Add to audit trail
                self.verification_history.append({
                    'timestamp': verification_result.timestamp,
                    'result_hash': result_hash,
                    'verified': True,
                    'details': verification_result.details
                })
                
                logger.info(f"Computation proof verified successfully: {result_hash}")
                return verification_result
            else:
                verification_result = VerificationResult(
                    verified=False,
                    proof_hash=result_hash,
                    timestamp=int(time.time()),
                    details={'error': 'Proof signature verification failed'}
                )
                
                logger.warning(f"Computation proof verification failed: {result_hash}")
                return verification_result
                
        except Exception as e:
            logger.error(f"Error verifying computation proof: {e}")
            return VerificationResult(
                verified=False,
                proof_hash='',
                timestamp=int(time.time()),
                details={'error': str(e)}
            )
    
    def bridge_risk_score_onchain(self, risk_score: float, proof: str, 
                                position_data: Dict[str, Any]) -> str:
        """
        Bridge a verified risk score to the onchain risk scoring contract.
        
        Args:
            risk_score: The verified risk score
            proof: The cryptographic proof
            position_data: Position data for context
            
        Returns:
            str: Transaction hash
        """
        try:
            # Verify the risk score first
            verification = self.verify_computation_proof(
                {'type': 'risk_score', 'score': risk_score, **position_data},
                proof
            )
            
            if not verification.verified:
                raise Exception("Risk score verification failed")
            
            # Bridge to onchain contract
            bridge = self.bridges['risk_scoring']
            contract = self.w3.eth.contract(
                address=bridge.contract_address,
                abi=bridge.abi
            )
            
            # Prepare transaction
            transaction = contract.functions.updateRiskScore(
                position_data.get('token_address'),
                int(risk_score * 10000),  # Convert to basis points
                proof,
                verification.proof_hash
            ).build_transaction({
                'from': self.account.address,
                'gas': bridge.gas_limit,
                'gasPrice': bridge.gas_price or self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Risk score bridged onchain: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error bridging risk score onchain: {e}")
            raise
    
    def bridge_allocation_proposal_onchain(self, allocation: Dict[str, float], 
                                         proof: str, portfolio_id: str) -> str:
        """
        Bridge an allocation proposal to the onchain allocation contract.
        
        Args:
            allocation: The allocation proposal
            proof: The cryptographic proof
            portfolio_id: Portfolio identifier
            
        Returns:
            str: Transaction hash
        """
        try:
            # Verify the allocation first
            verification = self.verify_computation_proof(
                {'type': 'allocation', 'allocation': allocation, 'portfolio_id': portfolio_id},
                proof
            )
            
            if not verification.verified:
                raise Exception("Allocation verification failed")
            
            # Bridge to onchain contract
            bridge = self.bridges['allocation']
            contract = self.w3.eth.contract(
                address=bridge.contract_address,
                abi=bridge.abi
            )
            
            # Convert allocation to onchain format
            tokens = list(allocation.keys())
            weights = [int(allocation[token] * 10000) for token in tokens]  # Basis points
            
            # Prepare transaction
            transaction = contract.functions.proposeAllocation(
                portfolio_id,
                tokens,
                weights,
                proof,
                verification.proof_hash
            ).build_transaction({
                'from': self.account.address,
                'gas': bridge.gas_limit,
                'gasPrice': bridge.gas_price or self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Allocation proposal bridged onchain: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error bridging allocation onchain: {e}")
            raise
    
    def bridge_market_data_onchain(self, market_data: Dict[str, Any], 
                                 proof: str) -> str:
        """
        Bridge market data to the onchain market data contract.
        
        Args:
            market_data: The market data
            proof: The cryptographic proof
            
        Returns:
            str: Transaction hash
        """
        try:
            # Verify the market data first
            verification = self.verify_computation_proof(
                {'type': 'market_data', 'data': market_data},
                proof
            )
            
            if not verification.verified:
                raise Exception("Market data verification failed")
            
            # Bridge to onchain contract
            bridge = self.bridges['market_data']
            contract = self.w3.eth.contract(
                address=bridge.contract_address,
                abi=bridge.abi
            )
            
            # Prepare transaction
            transaction = contract.functions.updateMarketData(
                json.dumps(market_data),
                proof,
                verification.proof_hash
            ).build_transaction({
                'from': self.account.address,
                'gas': bridge.gas_limit,
                'gasPrice': bridge.gas_price or self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Market data bridged onchain: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error bridging market data onchain: {e}")
            raise
    
    def _hash_result(self, result: Dict[str, Any]) -> str:
        """Create a hash of the computation result."""
        result_str = json.dumps(result, sort_keys=True)
        return hashlib.sha256(result_str.encode()).hexdigest()
    
    def _verify_proof_signature(self, result_hash: str, proof: str) -> bool:
        """
        Verify the cryptographic signature of the proof.
        
        This is a simplified verification - in production, you would:
        1. Verify the signature against the serverless platform's public key
        2. Check the proof format and structure
        3. Validate the timestamp and nonce
        """
        try:
            # For now, we'll do a basic format check
            # In production, implement proper cryptographic verification
            if not proof or len(proof) < 64:  # Minimum proof length
                return False
            
            # TODO: Implement proper signature verification
            # This would involve:
            # - Extracting the signature from the proof
            # - Verifying against the platform's public key
            # - Checking the signed message matches the result hash
            
            return True  # Placeholder - implement proper verification
            
        except Exception as e:
            logger.error(f"Error verifying proof signature: {e}")
            return False
    
    def get_verification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the verification history for audit purposes.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of verification records
        """
        return self.verification_history[-limit:]
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        total_verifications = len(self.verification_history)
        successful_verifications = sum(1 for v in self.verification_history if v['verified'])
        
        return {
            'total_verifications': total_verifications,
            'successful_verifications': successful_verifications,
            'success_rate': successful_verifications / max(total_verifications, 1),
            'last_verification': self.verification_history[-1] if self.verification_history else None
        } 