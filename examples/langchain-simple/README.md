# Try Coagent - LangChain Simple Example

This example demonstrates how to use the `coa-dev-coagent` package (installed via pip) with LangChain and Ollama to generate structured recipe data.

## Prerequisites

1. **Python 3.13+** - This example uses PEP 723 inline script metadata
2. **Ollama** - Install from https://ollama.ai
3. **Coagent Server** - Running on `http://localhost:3000`
4. **uv** - Python package installer (recommended): https://docs.astral.sh/uv/

## Installation

### Install Ollama and Pull a Model

```bash
# Install Ollama (see https://ollama.ai)
# Then pull a model:
ollama pull llama2
# or
ollama pull gpt-oss:20b
```

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Configuration

Edit `config.py` to customize:
- Ollama model name (default: `gpt-oss:20b`)
- Ollama base URL (default: `http://localhost:11434`)
- Temperature, top_p, and max_tokens
- Default ingredients list
- Number of recipes to generate

## Usage

### Option 1: Using uv (Recommended)

The script uses PEP 723 inline script metadata, so uv will automatically install dependencies:

```bash
uv run run_example.py
```

### Option 2: Using pip

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install langchain langchain-ollama pydantic coa-dev-coagent

# Run the example
python run_example.py
```

## What This Example Does

1. **Structured Output**: Uses Pydantic models to generate structured recipe data
2. **LangChain Integration**: Demonstrates LangChain with Ollama LLM
3. **Coagent Logging**: Logs all LLM calls and run metadata to the Coagent server
4. **Metadata Extraction**: Captures token usage and timing information
5. **Output**: Generates 3 recipes and saves them to `generated_recipes.json`

## Key Differences from langchain-simple

This example uses the **pip-installed** `coa-dev-coagent` package instead of a local editable install:

```python
from coa_dev_coagent import CoagentClient
```

Dependencies in the PEP 723 script metadata:
```python
# dependencies = [
#     "langchain",
#     "langchain-ollama",
#     "pydantic",
#     "coa-dev-coagent",  # pip-installed package
# ]
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check available models: `ollama list`
- Verify the model name in `config.py` matches an available model

### Coagent Server Issues
- Ensure the Coagent server is running on `http://localhost:3000`
- Check the server logs for any errors
- The example will continue running even if logging fails (warnings will be printed)

### Model Not Found
```bash
ollama pull <model-name>
```

## Example Output

```
🍳 Advanced LangChain Recipe Generator (Structured Output)
============================================================
Generating structured recipes with: chicken, tomatoes, onions, garlic, rice, olive oil, salt, pepper
Using model: gpt-oss:20b
Max recipes: 3

Generating recipes... (this may take a moment)
------------------------------------------------------------

🎉 Structured Recipe Collection:
============================================================

📋 Recipe 1: Chicken and Rice Pilaf
⏱️  Prep: 15 min | Cook: 30 min | Serves: 4

🥘 Ingredients:
   • 1 lb chicken breast, diced
   • 2 cups rice
   • 1 onion, chopped
   • ...

👨‍🍳 Instructions:
   1. Heat olive oil in a large skillet
   2. Add diced chicken and cook until browned
   ...

💾 Recipes saved to: generated_recipes.json
```

## License

This example is part of the Infinyon Coagent project.
