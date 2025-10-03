#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "langchain",
#     "langchain-ollama",
#     "pydantic",
#     "infinyon-coagent-client",
# ]
# ///
"""
Advanced LangChain integration with structured output using Pydantic.

This script demonstrates how to use LangChain with Ollama to generate
structured recipe data using Pydantic models, using the pip-installed
infinyon-coagent-client package.
"""

from langchain_ollama import OllamaLLM
from langchain_core.callbacks import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json
import time
import uuid
from config import default_config
from infinyon_coagent_client import CoagentClient


class Recipe(BaseModel):
    """Pydantic model for a structured recipe."""
    name: str = Field(description="Name of the recipe")
    ingredients: List[str] = Field(
        description="List of ingredients with quantities")
    instructions: List[str] = Field(
        description="Step-by-step cooking instructions")
    prep_time_minutes: int = Field(description="Preparation time in minutes")
    cook_time_minutes: int = Field(description="Cooking time in minutes")
    servings: int = Field(description="Number of servings")


class RecipeCollection(BaseModel):
    """Collection of three recipes."""
    recipes: List[Recipe] = Field(description="List of three recipes")


class MetadataExtractor(BaseCallbackHandler):
    def __init__(self):
        self.metadata: Dict[str, Any] = {}
        self.model: str = default_config.ollama.model_name

    def on_llm_start(self, serialized, prompts, **kwargs):
        print("LLM start")
        print(serialized)
        print(prompts)
        print(kwargs)
        self.metadata['start_time'] = time.time()
        self.metadata['model_info'] = serialized
        self.metadata['input_prompts'] = prompts

    def on_llm_end(self, response, **kwargs):
        print("LLM end")

        total_input = 0
        total_output = 0

        for gen in response.generations:
            for gen_inner in gen:
                if gen_inner.generation_info:
                    generation_info = gen[0].generation_info
                    total_input += generation_info['prompt_eval_count']
                    total_output += generation_info['eval_count']
                else:
                    print("No generation info found for this generation.")

        # create obj with input_tokens, output_tokens and total_tokens
        usage = {
            'input_tokens': total_input,
            'output_tokens': total_output,
            'total_tokens': total_input + total_output
        }

        self.metadata['model'] = self.model
        self.metadata['end_time'] = time.time()
        self.metadata['duration'] = self.metadata['end_time'] - \
            self.metadata['start_time']
        self.metadata['usage'] = usage

    # def on_llm_new_token(self, token, **kwargs):
    #     print("LLM new token")
    #     print(token)
    #     print(kwargs)

    def on_llm_error(self, error, **kwargs):
        print("LLM error")
        print(error)
        print(kwargs)
        self.metadata['error'] = str(error)


class StructuredRecipeGenerator:
    """Advanced recipe generator with structured output."""

    def __init__(self, model_name: str = None, metadata_extractor: MetadataExtractor = None):
        """Initialize the structured recipe generator."""
        if model_name is None:
            model_name = default_config.ollama.model_name

        self.llm = OllamaLLM(
            model=model_name,
            base_url=default_config.ollama.base_url,
            temperature=default_config.ollama.temperature,
            top_p=default_config.ollama.top_p,
            callbacks=[metadata_extractor] if metadata_extractor else [],
        )

        # Add max_tokens if specified in config
        if default_config.ollama.max_tokens is not None:
            self.llm.max_tokens = default_config.ollama.max_tokens

        self.parser = PydanticOutputParser(pydantic_object=RecipeCollection)

        # Initialize CoagentClient for logging
        self.client = CoagentClient(
            base_url="http://localhost:3000/api/v1"
        )

    def generate_structured_recipes(self, run_id: str, ingredients: List[str],
                                    metadata_extractor: MetadataExtractor = None) -> RecipeCollection:
        """
        Generate structured recipe data.

        Args:
            ingredients: List of available ingredients

        Returns:
            RecipeCollection with structured recipe data
        """
        system_prompt = """You are a professional chef and cooking assistant.
        Create exactly three practical and delicious recipes using the provided ingredients.
        Each recipe should be complete with ingredients, instructions, and timing information.
        Be creative but ensure the recipes are realistic and achievable."""

        # Create prompt template with format instructions
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """Create three recipes using these ingredients: {ingredients}

            {format_instructions}

            Make sure each recipe:
            - Uses the provided ingredients prominently
            - Has realistic preparation and cooking times
            - Includes clear step-by-step instructions
            - Specifies exact quantities for ingredients
            """)
        ])

        # Create the chain with parser
        chain = prompt_template | self.llm | self.parser

        # Format ingredients
        ingredients_str = ", ".join(ingredients)

        # Generate the full prompt for logging
        full_prompt = f"""Create three recipes using these ingredients: {ingredients_str}

        {self.parser.get_format_instructions()}

        Make sure each recipe:
        - Uses the provided ingredients prominently
        - Has realistic preparation and cooking times
        - Includes clear step-by-step instructions
        - Specifies exact quantities for ingredients
        """

        # Generate structured response
        start_time = time.time()
        result = chain.invoke({
            "ingredients": ingredients_str,
            "format_instructions": self.parser.get_format_instructions()
        })
        end_time = time.time()

        # Log the LLM call and response
        try:
            # Log the LLM call (request)
            self.client.log_llm_call_new(
                session_id=run_id,
                prompt=full_prompt,
                prompt_number=1,
                turn_number=1,
                issuer="langchain",
                system_prompt="You are a professional chef and cooking assistant."
            )

            # Log the LLM response with token usage
            self.client.log_llm_response(
                session_id=run_id,
                response=result.model_dump_json(),
                prompt_number=1,
                turn_number=1,
                input_tokens=metadata_extractor.metadata.get('usage', {}).get('input_tokens'),
                output_tokens=metadata_extractor.metadata.get('usage', {}).get('output_tokens'),
                total_tokens=metadata_extractor.metadata.get('usage', {}).get('total_tokens')
            )
        except Exception as e:
            print(f"Warning: Failed to log LLM call: {e}")

        return result


def main():
    """Demonstrate structured recipe generation."""
    print("🍳 Advanced LangChain Recipe Generator (Structured Output)")
    print("=" * 60)

    # Initialize CoagentClient for logging
    client = CoagentClient(
        base_url="http://localhost:3000/api/v1",
        debug=True
    )

    # Generate a unique run ID for this execution
    run_id = f"recipe-gen-{uuid.uuid4().hex[:8]}"

    try:
        # Log the start of the run
        try:
            client.log_session_start(
                session_id=run_id,
                prompt="Generate structured recipes using LangChain with Ollama",
                prompt_number=1,
                turn_number=0
            )
        except Exception as e:
            print(f"Warning: Failed to log session start: {e}")

        # Initialize generator
        metadata_extractor = MetadataExtractor()
        generator = StructuredRecipeGenerator(None, metadata_extractor)

        # Define ingredients from config
        ingredients = default_config.recipes.default_ingredients

        print(f"Generating structured recipes with: {', '.join(ingredients)}")
        print(f"Using model: {default_config.ollama.model_name}")
        print(f"Max recipes: {default_config.recipes.max_recipes}")
        print("\nGenerating recipes... (this may take a moment)")
        print("-" * 60)

        # Generate structured recipes
        start_time = time.time()
        recipe_collection = generator.generate_structured_recipes(
            run_id, ingredients, metadata_extractor)
        end_time = time.time()
        # Convert to milliseconds
        elapsed_time = int((end_time - start_time) * 1000)

        print("\n🎉 Structured Recipe Collection:")
        print("=" * 60)

        for i, recipe in enumerate(recipe_collection.recipes, 1):
            print(f"\n📋 Recipe {i}: {recipe.name}")
            print(
                f"⏱️  Prep: {recipe.prep_time_minutes} min | Cook: {recipe.cook_time_minutes} min | Serves: {recipe.servings}")

            print(f"\n🥘 Ingredients:")
            for ingredient in recipe.ingredients:
                print(f"   • {ingredient}")

            print(f"\n👨‍🍳 Instructions:")
            for j, instruction in enumerate(recipe.instructions, 1):
                print(f"   {j}. {instruction}")

            print("-" * 40)

        # Save to JSON file
        output_file = "generated_recipes.json"
        with open(output_file, 'w') as f:
            json.dump(recipe_collection.model_dump(), f, indent=2)

        print(f"\n💾 Recipes saved to: {output_file}")

        # Log the end of the session
        try:
            client.log_session_end(
                session_id=run_id,
                response=f"Generated {len(recipe_collection.recipes)} recipes successfully",
                prompt_number=1,
                turn_number=0,
                elapsed_time_ms=elapsed_time,
                meta={"context": metadata_extractor.metadata}
            )
        except Exception as e:
            print(f"Warning: Failed to log session end: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure Ollama is installed and running")
        print("   2. Check that the model is available: ollama list")
        print("   3. Try pulling the model: ollama pull llama2")

        # Log the error if possible
        try:
            client.log_session_end(
                session_id=run_id,
                response=f"Error: {str(e)}",
                prompt_number=1,
                turn_number=0,
                elapsed_time_ms=0
            )
        except Exception as log_error:
            print(f"Warning: Failed to log error: {log_error}")


if __name__ == "__main__":
    main()
