"""
Configuration for the LangChain example script.
"""

from typing import List
from dataclasses import dataclass


# TODO: generate a coagent factory model to create a langchain llm provider object
#       from the coagent model provider config

@dataclass
class OllamaConfig:
    """Configuration for Ollama LLM settings."""
    model_name: str = "qwen3:8b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = None


@dataclass
class RecipeConfig:
    """Configuration for recipe generation."""
    default_ingredients: List[str] = None
    max_recipes: int = 3

    def __post_init__(self):
        if self.default_ingredients is None:
            self.default_ingredients = [
                "chicken",
                "tomatoes",
                "onions",
                "garlic",
                "rice",
                "olive oil",
                "salt",
                "pepper"
            ]


@dataclass
class AppConfig:
    """Main application configuration."""
    ollama: OllamaConfig = None
    recipes: RecipeConfig = None

    def __post_init__(self):
        if self.ollama is None:
            self.ollama = OllamaConfig()
        if self.recipes is None:
            self.recipes = RecipeConfig()


# Create default configuration instance
default_config = AppConfig()
