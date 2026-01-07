"""
Ollama Client - Handles communication with Qwen2.5-Coder model
"""
import aiohttp
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen2.5-coder:7b"
        self.timeout = aiohttp.ClientTimeout(total=60)
    
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate response from Ollama model
        
        Args:
            prompt: The prompt to send to the model
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length
            
        Returns:
            str: The model's response
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40,
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
                    
                    data = await response.json()
                    return data.get("response", "")
                    
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out")
            raise Exception("Request to AI model timed out. Please try again.")
        except aiohttp.ClientError as e:
            logger.error(f"Ollama client error: {e}")
            raise Exception(f"Could not connect to Ollama: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is running and model is available
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        model_names = [m.get("name", "") for m in models]
                        
                        # Check if our model is available
                        return any(self.model in name for name in model_names)
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def generate_with_retry(
        self, 
        prompt: str, 
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate with automatic retry on failure
        """
        for attempt in range(max_retries):
            try:
                result = await self.generate(prompt)
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Wait before retry
        return None
