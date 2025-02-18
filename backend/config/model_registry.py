import json
import os
from typing import Optional, Dict, Any, Tuple

class ModelRegistry:
    def __init__(self, config_path: str = "config/model_config.json"):
        self.config_path = config_path
        self._config = self._load_config()
        self._current_provider = "sambanova"  # Default to sambanova if not specified

    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Model configuration file not found at {self.config_path}")

    def get_model_info(self, provider: Optional[str] = None, model_key: Optional[str] = None) -> Tuple[str, str]:
        """
        Get the actual model name and API URL for the given provider and model key.
        
        Returns:
            Tuple[str, str]: A tuple containing (model_name, api_url)
        """
        provider = provider or self._current_provider
        provider_config = self._config["providers"].get(provider)
        
        if not provider_config:
            raise ValueError(f"Provider {provider} not found in configuration")

        if not model_key:
            # If no model key provided, use the first available model
            model_key = next(iter(provider_config["model_mapping"].keys()))

        model_mapping = provider_config["model_mapping"]
        model_name = model_mapping.get(model_key)

        if not model_name:
            raise ValueError(f"No model found for key {model_key} with provider {provider}")

        return model_name, provider_config["url"]

    def get_api_key_env(self, provider: Optional[str] = None) -> str:
        """Get the environment variable name for the API key of the specified provider."""
        provider = provider or self._current_provider
        provider_config = self._config["providers"].get(provider)
        
        if not provider_config:
            raise ValueError(f"Provider {provider} not found in configuration")

        return provider_config["api_key_env"]

    def get_api_url(self, provider: Optional[str] = None) -> str:
        """Get the API URL for the specified provider."""
        provider = provider or self._current_provider
        provider_config = self._config["providers"].get(provider)
        
        if not provider_config:
            raise ValueError(f"Provider {provider} not found in configuration")

        return provider_config["url"]

    def set_provider(self, provider: str):
        """Set the current LLM provider."""
        if provider not in self._config["providers"]:
            raise ValueError(f"Provider {provider} not configured")
        self._current_provider = provider

    def get_current_provider(self) -> str:
        """Get the current LLM provider."""
        return self._current_provider

    def list_available_models(self, provider: Optional[str] = None) -> Dict[str, str]:
        """List all available models for the specified provider."""
        provider = provider or self._current_provider
        provider_config = self._config["providers"].get(provider)
        
        if not provider_config:
            raise ValueError(f"Provider {provider} not found in configuration")

        return provider_config["model_mapping"]

# Global instance
model_registry = ModelRegistry() 