"""
Centralized Gemini AI Handler with Robust Fallback Logic
- Multiple model fallback through latest available models
- Multiple API key rotation
- Automatic retry with exponential backoff
- Rate limit handling

Official Models (Jan 2026):
- gemini-2.5-flash: Best price-performance, fast, stable
- gemini-2.5-flash-lite: Ultra fast, cost-efficient
- gemini-2.5-pro: Advanced thinking, complex reasoning
- gemini-2.0-flash: Previous gen workhorse
- gemini-2.0-flash-lite: Previous gen fast model
"""
import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

try:
    from production import RequestContext
    _has_context = True
except ImportError:
    _has_context = False

logger = logging.getLogger(__name__)

# Available Gemini models in order of preference (updated Jan 2026)
# Source: https://ai.google.dev/gemini-api/docs/models
GEMINI_MODELS = [
    'gemini-2.5-flash',       # Best price-performance (stable)
    'gemini-2.5-flash-lite',  # Ultra fast, cheapest
    'gemini-2.0-flash',       # Previous gen workhorse (fallback)
    'gemini-2.5-pro',         # Advanced thinking (slower but powerful)
    'gemini-2.0-flash-lite',  # Previous gen fast (last resort)
]


class GeminiHandler:
    """
    Centralized Gemini API handler with:
    - Automatic model fallback
    - API key rotation
    - Rate limit handling with retry
    - Connection pooling
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - one handler for all"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.api_keys: List[str] = []
        self.current_key_index = 0
        self.current_model_index = 0
        self.models = GEMINI_MODELS.copy()
        self.genai = None
        self.failed_keys: Dict[str, datetime] = {}  # Track failed keys with cooldown
        self.failed_models: Dict[str, datetime] = {}  # Track failed models
        self.key_cooldown = timedelta(minutes=5)  # Wait 5 min before retrying failed key
        self.model_cooldown = timedelta(minutes=2)  # Wait 2 min before retrying failed model
        
        self._load_api_keys()
        self._initialize_genai()
        self._initialized = True
        
    def _load_api_keys(self):
        """Load all available API keys"""
        # Try environment variables
        key_vars = ['GEMINI_API_KEY', 'GEMINI_API_KEY_2', 'GEMINI_API_KEY_3']
        
        for var in key_vars:
            key = os.getenv(var, '').strip()
            if key and key not in self.api_keys:
                self.api_keys.append(key)
                
        # Try config file
        try:
            import config
            if hasattr(config, 'GEMINI_API_KEYS'):
                for key in config.GEMINI_API_KEYS:
                    if key and key.strip() and key.strip() not in self.api_keys:
                        self.api_keys.append(key.strip())
        except ImportError:
            pass
            
        if self.api_keys:
            logger.info(f"Loaded {len(self.api_keys)} Gemini API keys")
        else:
            logger.warning("No Gemini API keys found!")
            
    def _initialize_genai(self):
        """Initialize Google Generative AI module"""
        try:
            import google.generativeai as genai
            self.genai = genai
            logger.info("Google Generative AI module loaded")
        except ImportError:
            logger.error("google-generativeai package not installed!")
            self.genai = None
            
    def _get_available_key(self) -> Optional[str]:
        """Get next available API key (skip failed ones in cooldown)"""
        if not self.api_keys:
            return None
            
        now = datetime.now()
        attempts = 0
        
        while attempts < len(self.api_keys):
            key = self.api_keys[self.current_key_index % len(self.api_keys)]
            self.current_key_index += 1
            
            # Check if key is in cooldown
            if key in self.failed_keys:
                if now - self.failed_keys[key] < self.key_cooldown:
                    attempts += 1
                    continue
                else:
                    # Cooldown expired, remove from failed
                    del self.failed_keys[key]
                    
            return key
            
        # All keys in cooldown, return first one anyway
        return self.api_keys[0]
        
    def _get_available_model(self) -> Optional[str]:
        """Get next available model (skip failed ones in cooldown)"""
        now = datetime.now()
        
        for model in self.models:
            if model in self.failed_models:
                if now - self.failed_models[model] < self.model_cooldown:
                    continue
                else:
                    del self.failed_models[model]
            return model
            
        # All models in cooldown, return first one
        return self.models[0]
        
    def _mark_key_failed(self, key: str):
        """Mark an API key as failed"""
        self.failed_keys[key] = datetime.now()
        logger.warning(f"API key marked as failed (cooldown: {self.key_cooldown})")
        
    def _mark_model_failed(self, model: str):
        """Mark a model as failed"""
        self.failed_models[model] = datetime.now()
        logger.warning(f"Model {model} marked as failed (cooldown: {self.model_cooldown})")
        
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate content with automatic fallback.
        
        Args:
            prompt: The prompt to send
            temperature: Creativity level (0-1)
            max_tokens: Maximum output tokens
            max_retries: Max retry attempts per key/model combo
            
        Returns:
            Generated text or None if all attempts fail
        """
        if not self.genai:
            logger.error("Gemini not initialized")
            return None
            
        if not self.api_keys:
            logger.error("No API keys available")
            return None
            
        # Try each model
        for model_name in self.models:
            if model_name in self.failed_models:
                if datetime.now() - self.failed_models[model_name] < self.model_cooldown:
                    continue
                    
            # Try each API key
            keys_tried = 0
            while keys_tried < len(self.api_keys):
                api_key = self._get_available_key()
                if not api_key:
                    break
                    
                keys_tried += 1
                
                # Try with retries
                for attempt in range(max_retries):
                    try:
                        self.genai.configure(api_key=api_key)
                        model = self.genai.GenerativeModel(model_name)
                        
                        response = model.generate_content(
                            prompt,
                            generation_config={
                                'temperature': temperature,
                                'top_p': 0.8,
                                'max_output_tokens': max_tokens
                            }
                        )
                        
                        if response.candidates and len(response.candidates) > 0:
                            candidate = response.candidates[0]
                            if candidate.content and candidate.content.parts:
                                logger.debug(f"Success with {model_name}")
                                return response.text
                                
                        # Empty response, try next
                        break
                        
                    except Exception as e:
                        error_str = str(e).lower()
                        
                        # Rate limit - wait and retry
                        if '429' in str(e) or 'quota' in error_str or 'rate' in error_str:
                            if attempt < max_retries - 1:
                                delay = 2 ** (attempt + 1)  # Exponential backoff
                                logger.warning(f"Rate limit. Waiting {delay}s...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                self._mark_key_failed(api_key)
                                break
                                
                        # Invalid API key
                        elif 'api key' in error_str or 'invalid' in error_str or '401' in str(e):
                            self._mark_key_failed(api_key)
                            logger.error(f"Invalid API key")
                            break
                            
                        # Model not available
                        elif 'not found' in error_str or 'not supported' in error_str or '404' in str(e):
                            self._mark_model_failed(model_name)
                            logger.warning(f"Model {model_name} not available, trying next...")
                            break
                            
                        # Other error
                        else:
                            logger.error(f"Gemini error: {e}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(1)
                                continue
                            break
                            
        logger.error("All Gemini attempts failed")
        return None
        
    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> Optional[Dict[str, Any]]:
        """Generate and parse JSON response"""
        import json
        import re
        
        response = await self.generate(prompt, temperature, max_tokens)
        if not response:
            return None
            
        try:
            # Try to extract JSON from response
            # Look for JSON in code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for raw JSON
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None
                    
            # Clean and parse
            json_str = re.sub(r'//.*', '', json_str)  # Remove comments
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            json_str = re.sub(r',(\s*?[\]\}])', r'\1', json_str)  # Fix trailing commas
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return None
            
    def get_status(self) -> Dict[str, Any]:
        """Get handler status for debugging"""
        return {
            "initialized": self._initialized,
            "genai_loaded": self.genai is not None,
            "api_keys_count": len(self.api_keys),
            "api_keys_failed": len(self.failed_keys),
            "models_available": self.models,
            "models_failed": list(self.failed_models.keys()),
            "current_key_index": self.current_key_index,
        }


# Global singleton instance
gemini = GeminiHandler()


# Convenience functions
async def generate(prompt: str, **kwargs) -> Optional[str]:
    """Quick generate function"""
    return await gemini.generate(prompt, **kwargs)

async def generate_json(prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Quick generate JSON function"""
    return await gemini.generate_json(prompt, **kwargs)

def get_status() -> Dict[str, Any]:
    """Get Gemini handler status"""
    return gemini.get_status()
