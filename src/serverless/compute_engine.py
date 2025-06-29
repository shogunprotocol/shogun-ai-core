"""
Compute engine for orchestrating Chainlink Functions computations.
Manages the integration between Chainlink Functions and Shogun AI Core.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor

from .functions_client import ChainlinkFunctionsClient, ChainlinkResponse

logger = logging.getLogger(__name__)

@dataclass
class ChainlinkTask:
    """A Chainlink Functions task to be executed offchain."""
    task_id: str
    task_type: str  # 'strategy_risk_scoring', 'cross_chain_apy', 'allocation_optimization', 'oracle_health_check'
    input_data: Dict[str, Any]
    priority: int = 1  # 1 = highest, 5 = lowest
    callback: Optional[callable] = None
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class ChainlinkComputeEngine:
    """
    Engine for managing Chainlink Functions computations.
    
    Integrates with the main Shogun system to:
    - Queue Chainlink Functions tasks
    - Execute them on the Chainlink network
    - Verify results and proofs
    - Feed results back to onchain contracts
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Chainlink compute engine."""
        self.config = config
        self.chainlink_client = ChainlinkFunctionsClient(config.get('chainlink_functions', {}))
        
        # Task management
        self.task_queue: List[ChainlinkTask] = []
        self.active_tasks: Dict[str, ChainlinkTask] = {}
        self.completed_tasks: Dict[str, ChainlinkResponse] = {}
        
        # Execution settings
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 5)
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        
        # Performance tracking
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_compute_time': 0
        }
    
    async def submit_strategy_risk_scoring_task(self, strategy_data: Dict[str, Any], 
                                              callback: Optional[callable] = None) -> str:
        """
        Submit a strategy risk scoring task to Chainlink Functions.
        
        Args:
            strategy_data: Strategy data including address, tokens, allocation, etc.
            callback: Optional callback function when task completes
            
        Returns:
            str: Task ID
        """
        task = ChainlinkTask(
            task_id=f"strategy_risk_{int(time.time() * 1000)}",
            task_type='strategy_risk_scoring',
            input_data=strategy_data,
            priority=1,  # High priority for risk scoring
            callback=callback
        )
        
        return await self._submit_task(task)
    
    async def submit_cross_chain_apy_task(self, strategy_addresses: List[str], 
                                        callback: Optional[callable] = None) -> str:
        """
        Submit a cross-chain APY fetch task to Chainlink Functions.
        
        Args:
            strategy_addresses: List of strategy contract addresses
            callback: Optional callback function when task completes
            
        Returns:
            str: Task ID
        """
        task = ChainlinkTask(
            task_id=f"cross_chain_apy_{int(time.time() * 1000)}",
            task_type='cross_chain_apy',
            input_data={'strategy_addresses': strategy_addresses},
            priority=2,
            callback=callback
        )
        
        return await self._submit_task(task)
    
    async def submit_allocation_optimization_task(self, vault_data: Dict[str, Any],
                                                callback: Optional[callable] = None) -> str:
        """
        Submit a vault allocation optimization task to Chainlink Functions.
        
        Args:
            vault_data: Vault data including current allocations, constraints, etc.
            callback: Optional callback function when task completes
            
        Returns:
            str: Task ID
        """
        task = ChainlinkTask(
            task_id=f"allocation_opt_{int(time.time() * 1000)}",
            task_type='allocation_optimization',
            input_data=vault_data,
            priority=3,
            callback=callback
        )
        
        return await self._submit_task(task)
    
    async def submit_oracle_health_check_task(self, oracle_addresses: List[str],
                                            callback: Optional[callable] = None) -> str:
        """
        Submit an oracle health check task to Chainlink Functions.
        
        Args:
            oracle_addresses: List of oracle addresses to check
            callback: Optional callback function when task completes
            
        Returns:
            str: Task ID
        """
        task = ChainlinkTask(
            task_id=f"oracle_health_{int(time.time() * 1000)}",
            task_type='oracle_health_check',
            input_data={'oracle_addresses': oracle_addresses},
            priority=2,
            callback=callback
        )
        
        return await self._submit_task(task)
    
    async def _submit_task(self, task: ChainlinkTask) -> str:
        """Submit a task to the queue."""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x.priority)  # Sort by priority
        self.stats['tasks_submitted'] += 1
        
        logger.info(f"Submitted Chainlink Functions task {task.task_id} of type {task.task_type}")
        
        # Start processing if not already running
        asyncio.create_task(self._process_queue())
        
        return task.task_id
    
    async def _process_queue(self):
        """Process the task queue."""
        while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
            task = self.task_queue.pop(0)
            self.active_tasks[task.task_id] = task
            
            # Execute task in thread pool
            asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: ChainlinkTask):
        """Execute a single Chainlink Functions task."""
        start_time = time.time()
        
        try:
            logger.info(f"Executing Chainlink Functions task {task.task_id}")
            
            # Execute based on task type
            if task.task_type == 'strategy_risk_scoring':
                response = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.chainlink_client.run_strategy_risk_scoring,
                    task.input_data
                )
            elif task.task_type == 'cross_chain_apy':
                response = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.chainlink_client.fetch_cross_chain_apy,
                    task.input_data['strategy_addresses']
                )
            elif task.task_type == 'allocation_optimization':
                response = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.chainlink_client.optimize_vault_allocation,
                    task.input_data
                )
            elif task.task_type == 'oracle_health_check':
                response = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.chainlink_client.check_oracle_health,
                    task.input_data['oracle_addresses']
                )
            else:
                raise ValueError(f"Unknown Chainlink Functions task type: {task.task_type}")
            
            # Verify the Chainlink Functions response
            if response.status == 'completed' and not response.error:
                self.completed_tasks[task.task_id] = response
                self.stats['tasks_completed'] += 1
                
                # Execute callback if provided
                if task.callback:
                    try:
                        await task.callback(response)
                    except Exception as e:
                        logger.error(f"Error in Chainlink Functions task callback: {e}")
                
                logger.info(f"Chainlink Functions task {task.task_id} completed successfully")
            else:
                raise Exception(f"Chainlink Functions task failed: {response.error}")
                
        except Exception as e:
            logger.error(f"Chainlink Functions task {task.task_id} failed: {e}")
            self.stats['tasks_failed'] += 1
        
        finally:
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            # Update stats
            compute_time = time.time() - start_time
            self.stats['total_compute_time'] += compute_time
            
            # Continue processing queue
            asyncio.create_task(self._process_queue())
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a Chainlink Functions task.
        
        Args:
            task_id: The task ID to check
            
        Returns:
            Dict with task status information
        """
        if task_id in self.completed_tasks:
            response = self.completed_tasks[task_id]
            return {
                'status': 'completed',
                'result': response.result.decode() if response.result else None,
                'error': response.error,
                'request_id': response.request_id
            }
        elif task_id in self.active_tasks:
            return {
                'status': 'running',
                'task_type': self.active_tasks[task_id].task_type,
                'created_at': self.active_tasks[task_id].created_at
            }
        else:
            # Check if it's in the queue
            for task in self.task_queue:
                if task.task_id == task_id:
                    return {
                        'status': 'queued',
                        'priority': task.priority,
                        'position': self.task_queue.index(task)
                    }
            
            return {'status': 'not_found'}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Chainlink Functions compute engine statistics."""
        return {
            **self.stats,
            'queue_length': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'avg_compute_time': (
                self.stats['total_compute_time'] / max(self.stats['tasks_completed'], 1)
            )
        }
    
    async def shutdown(self):
        """Shutdown the Chainlink Functions compute engine gracefully."""
        logger.info("Shutting down Chainlink Functions compute engine...")
        
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(1)
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        logger.info("Chainlink Functions compute engine shutdown complete") 