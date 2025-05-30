"""
LLM-based strategy planner module.
Handles interaction with language models for strategy generation using OpenRouter.
"""

import json
import os
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMPlanner:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM planner with configuration."""
        self.config = config
        self.model = config['model']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']
        
        # OpenRouter configuration
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": os.getenv('SITE_URL', 'https://github.com/your-repo/shogun-agent'),
            "X-Title": os.getenv('SITE_NAME', 'Shogun Agent')
        }

    def _format_prompt(self, market_data: Dict[str, Any], historical_context: Dict[str, Any]) -> str:
        """Format the prompt for the LLM with market data and historical context."""
        return f"""
        Based on the following market data and historical context, generate a DeFi strategy:
        
        Market Data:
        {json.dumps(market_data, indent=2)}
        
        Historical Context:
        {json.dumps(historical_context, indent=2)}
        
        Generate a strategy that:
        1. Maximizes yield while maintaining safety
        2. Considers current market conditions
        3. Avoids known risky patterns
        4. Is executable within current gas constraints
        
        Format the response as a JSON object with the following structure:
        {{
            "strategy_type": "string",
            "target_protocol": "string",
            "actions": [
                {{
                    "action_type": "string",
                    "parameters": {{}}
                }}
            ],
            "expected_outcome": {{
                "apr": "float",
                "risk_level": "string"
            }}
        }}
        """

    def generate_strategy(self, market_data: Dict[str, Any], historical_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a strategy using the LLM based on current market data and historical context.
        
        Args:
            market_data: Current market data from all providers
            historical_context: Historical patterns and outcomes
            
        Returns:
            Dict containing the generated strategy
        """
        try:
            prompt = self._format_prompt(market_data, historical_context)
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make the API request
            response = requests.post(
                url=f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.text}")
            
            # Parse the response
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse the JSON response
            strategy = json.loads(content)
            
            # Validate the strategy format
            if not self._validate_strategy(strategy):
                raise ValueError("Invalid strategy format in LLM response")
            
            return strategy
            
        except Exception as e:
            raise Exception(f"Error generating strategy: {e}")

    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate the generated strategy format and content."""
        required_fields = ["strategy_type", "target_protocol", "actions", "expected_outcome"]
        if not all(field in strategy for field in required_fields):
            return False
            
        # Validate actions
        if not isinstance(strategy['actions'], list):
            return False
            
        for action in strategy['actions']:
            if not isinstance(action, dict):
                return False
            if not all(field in action for field in ["action_type", "parameters"]):
                return False
                
        # Validate expected outcome
        if not isinstance(strategy['expected_outcome'], dict):
            return False
        if not all(field in strategy['expected_outcome'] for field in ["apr", "risk_level"]):
            return False
            
        return True 