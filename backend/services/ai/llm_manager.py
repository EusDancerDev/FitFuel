from typing import Dict, List, Optional
import logging
import openai
import anthropic
from datetime import datetime
from ...config import settings
from ...database.cache import RedisCache

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.models = {
            "gpt4": {
                "client": openai.Client(api_key=settings.OPENAI_API_KEY),
                "model": "gpt-4",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "claude_sonnet": {
                "client": anthropic.Client(api_key=settings.ANTHROPIC_API_KEY),
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "claude_opus": {
                "client": anthropic.Client(api_key=settings.ANTHROPIC_API_KEY),
                "model": "claude-3-opus-20240229",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "claude_haiku": {
                "client": anthropic.Client(api_key=settings.ANTHROPIC_API_KEY),
                "model": "claude-3-haiku-20240229",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        self.default_model = "gpt4"
        self.fallback_order = ["gpt4", "claude_opus", "claude_sonnet", "claude_haiku"]
        self.retry_attempts = 2

    async def process_request(
        self,
        prompt: str,
        model_key: str = None,
        context: Dict = None,
        max_retries: int = None
    ) -> Dict:
        """Process request with fallback and retry logic"""
        retries = max_retries or self.retry_attempts
        errors = []
        
        # Try cache first
        cache_key = f"llm_response:{hash(prompt)}"
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            return cached_response

        # Try primary model
        model_key = model_key or self.default_model
        try:
            response = await self._make_request(model_key, prompt, context)
            await self.cache.set(cache_key, response, expire=3600)  # Cache for 1 hour
            return response
        except Exception as e:
            errors.append(f"{model_key}: {str(e)}")
            logger.warning(f"Primary model {model_key} failed: {str(e)}")

        # Try fallback models
        for fallback_model in self.fallback_order:
            if fallback_model == model_key:
                continue
                
            try:
                response = await self._make_request(fallback_model, prompt, context)
                await self.cache.set(cache_key, response, expire=3600)
                return response
            except Exception as e:
                errors.append(f"{fallback_model}: {str(e)}")
                logger.warning(f"Fallback model {fallback_model} failed: {str(e)}")

        raise RuntimeError(f"All models failed: {'; '.join(errors)}")

    async def _make_request(
        self,
        model_key: str,
        prompt: str,
        context: Dict = None
    ) -> Dict:
        """Make request to specific LLM"""
        model_config = self.models[model_key]
        
        try:
            if model_key.startswith("claude"):
                response = await self._make_anthropic_request(
                    model_config,
                    prompt,
                    context
                )
            else:  # GPT-4
                response = await self._make_openai_request(
                    model_config,
                    prompt,
                    context
                )
            
            return {
                "success": True,
                "model": model_key,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error with {model_key}: {str(e)}")
            raise

    async def _make_anthropic_request(
        self,
        config: Dict,
        prompt: str,
        context: Dict = None
    ) -> str:
        """Make request to Anthropic Claude models"""
        try:
            messages = [{"role": "user", "content": prompt}]
            if context:
                messages.insert(0, {"role": "system", "content": str(context)})

            response = await config["client"].messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                messages=messages
            )
            
            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    async def _make_openai_request(
        self,
        config: Dict,
        prompt: str,
        context: Dict = None
    ) -> str:
        """Make request to OpenAI GPT-4"""
        try:
            messages = [{"role": "user", "content": prompt}]
            if context:
                messages.insert(0, {"role": "system", "content": str(context)})

            response = await config["client"].chat.completions.create(
                model=config["model"],
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def validate_response(
        self,
        response: str,
        validation_criteria: Dict
    ) -> bool:
        """Validate LLM response against criteria"""
        try:
            # Check required fields
            if validation_criteria.get("required_fields"):
                for field in validation_criteria["required_fields"]:
                    if field not in response:
                        return False

            # Check response length
            if validation_criteria.get("min_length"):
                if len(response) < validation_criteria["min_length"]:
                    return False

            # Check for prohibited content
            if validation_criteria.get("prohibited_content"):
                for term in validation_criteria["prohibited_content"]:
                    if term.lower() in response.lower():
                        return False

            return True

        except Exception as e:
            logger.error(f"Response validation error: {str(e)}")
            return False 