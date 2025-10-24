# CoAgent Event Logging Reference for Python Integration

This guide explains how to use the CoAgent logging system with your AI agents to monitor performance, track behavior, and analyze execution patterns.

## Overview

The CoAgent logging system captures events of AI agent runs using structured event logs. The interactions with the CoAgent sandbox, as well as CoAgent python client integration capture log events through the logging system.

When integrated with your Python-based AI agent, the `coa-dev-coagent` client library enables you to log events at key points in your agent's lifecycle, creating a comprehensive audit trail for analysis, monitoring, and optimization.

## Core Concepts

### Sessions and Event Sequencing

Every overall agent interaction is organized as a **session** with a unique `session_id`. Within each session, events are sequenced using two counters:

- **prompt_number**: Sequential number for each major prompt/interaction
- **turn_number**: Turn number within a prompt for multi-turn interactions

Each log event can also carry metadata used for optional standard data as well as user defined
data elements. The event types have been designed to support a wide range of AI agent architectures
and workflows.

This tracking enables you to trace complex agent behaviors including multi-turn conversations and nested LLM calls.

## Event Types for Agent Monitoring

A range of Event types are available for logging. A given workflow does not need to log
all event types to capture useful logs for CoAgent. However, the more information that
is logged the more analysis and monitoring information can be assessed.

### 1. SessionStart - Initialize Agent Run Tracking

**When to use**: Log this at the very beginning of your agent's execution to mark the start of a new run.

**What it captures**:
- Initial prompt or task description
- Session metadata (configuration, parameters, etc.)
- Start timestamp
- Optional Agent "stack", workflow and versioning information

**Python example**:
```python
from coa_dev_coagent import CoagentClient
import uuid

client = CoagentClient(base_url="http://localhost:3000/api/v1")
session_id = f"agent-run-{uuid.uuid4().hex[:8]}"

client.log_session_start(
    session_id=session_id,
    prompt="Analyze customer feedback and generate insights",
    prompt_number=1,
    turn_number=0,
    meta={"agent_type": "analytics", "version": "1.2.0"}
)
```

**Use cases**:
- Track when agent runs begin
- Associate metadata with runs (version, config, environment)
- Establish baseline for execution time metrics

---

### 2. SessionEnd - Complete Agent Run Tracking

**When to use**: Log this when your agent completes its task (successfully or with errors).

**What it captures**:
- Final response or output
- Total execution time
- Session completion metadata

**Python example**:
```python
import time

start_time = time.time()
# ... agent execution ...
end_time = time.time()
elapsed_ms = int((end_time - start_time) * 1000)

client.log_session_end(
    session_id=session_id,
    response="Generated 5 key insights from 234 feedback items",
    prompt_number=1,
    turn_number=0,
    elapsed_time_ms=elapsed_ms,
    meta={"insights_count": 5, "feedback_processed": 234}
)
```

**Use cases**:
- Calculate total run duration
- Track success/failure rates
- Capture final outputs for evaluation
- Store outcome metrics

---

### 3. LlmCall - Track LLM Request Details

**When to use**: Log this before making a call to an LLM to capture the request context.

**What it captures**:
- The prompt sent to the LLM
- System prompt/instructions
- Conversation history
- Who initiated the call (user, agent, tool)

**Python example**:
```python
client.log_llm_call_new(
    session_id=session_id,
    prompt="Summarize the following customer feedback: ...",
    prompt_number=1,
    turn_number=1,
    issuer="feedback_analyzer",
    system_prompt="You are a customer insights analyst...",
    history={"messages": [ "who is account 1234"]}
)

# Make actual LLM call
response = llm.generate(prompt)
```

**Use cases**:
- Understand what prompts are being sent to LLMs
- Track prompt engineering variations
- Debug unexpected LLM behaviors
- Analyze prompt patterns across runs

---

### 4. LlmResponse - Capture LLM Output and Token Usage

**When to use**: Log this after receiving a response from an LLM to track outputs and resource consumption.

**What it captures**:
- LLM response content
- Token usage (input, output, total)
- Tool calls made by the LLM
- Timing information

**Python example**:
```python
# After LLM call completes
client.log_llm_response(
    session_id=session_id,
    response=llm_response.content,
    prompt_number=1,
    turn_number=1,
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    total_tokens=response.usage.total_tokens,
    tool_calls={"tools_used": ["search", "analyze"]}
)
```

**Use cases**:
- Monitor token consumption and costs
- Track LLM response quality
- Identify expensive operations
- Correlate inputs with outputs for evaluation
- Analyze tool usage patterns

---

### 5. ToolCall - Log Tool/Function Invocations

**When to use**: Log this when your agent calls an external tool, API, or function.

**What it captures**:
- Tool name and parameters
- Context for why the tool was called
- Input arguments

**Use cases**:
- Track which tools agents use most frequently
- Debug tool integration issues
- Understand agent reasoning and action patterns
- Measure tool call success rates

---

### 6. ToolResponse - Capture Tool Execution Results

Tool Responses are often then folded into history/system prompt information for
subsequent llm_calls

**When to use**: Log this after a tool execution completes to record the result.

**What it captures**:
- Tool output/return value
- Execution success/failure status
- Error information if applicable

**Use cases**:
- Track tool reliability
- Debug tool failures
- Measure tool execution times
- Correlate tool inputs with outputs

---

### 7. Error - Record Agent Failures and Exceptions

**When to use**: Log this whenever your agent encounters an error or exception.

**What it captures**:
- Error message
- Error type/category
- Stack trace
- Context when error occurred

**Python example**:
```python
try:
    result = agent.process(data)
except Exception as e:
    client.log_error(
        session_id=session_id,
        prompt_number=1,
        turn_number=2,
        error_message=str(e),
        error_type=type(e).__name__,
        stack_trace=traceback.format_exc()
    )
    raise
```

**Use cases**:
- Monitor agent reliability
- Identify common failure modes
- Debug production issues
- Track error rates over time
- Alert on critical failures

---

### 8. Info, Warning, Debug - Structured Logging Events

**When to use**: Use these for general logging at different severity levels throughout your agent's execution.

**What they capture**:
- Informational messages about agent state
- Warnings about potential issues
- Debug information for troubleshooting

**Use cases**:
- Track agent decision-making process
- Log intermediate state changes
- Capture context for debugging
- Monitor agent behavior without errors

---

## Complete Integration Example

Here's a full example showing how to integrate Coagent logging into a LangChain-based agent with proper prompt_number and turn_number tracking:

```python
from coa_dev_coagent import CoagentClient
from langchain_ollama import OllamaLLM
import uuid
import time

# Initialize client
client = CoagentClient(base_url="http://localhost:3000/api/v1")
session_id = f"recipe-agent-{uuid.uuid4().hex[:8]}"
llm = OllamaLLM(model="llama2")

# Start session with first prompt
prompt_number = 1
client.log_session_start(
    session_id=session_id,
    prompt="Generate three recipes using chicken and vegetables",
    prompt_number=prompt_number,
    turn_number=0,
    meta={"agent": "recipe_generator", "version": "2.0"}
)

try:
    # PROMPT 1: Initial recipe generation
    # Turn 1: First LLM call
    prompt = "Create three recipes using: chicken, carrots, onions"
    client.log_llm_call_new(
        session_id=session_id,
        prompt=prompt,
        prompt_number=prompt_number,
        turn_number=1,
        issuer="recipe_agent",
        system_prompt="You are a professional chef assistant"
    )

    response = llm.invoke(prompt)

    client.log_llm_response(
        session_id=session_id,
        response=response,
        prompt_number=prompt_number,
        turn_number=1,
        input_tokens=100,
        output_tokens=350,
        total_tokens=450
    )

    # Turn 2: Follow-up LLM call to add nutritional info
    followup_prompt = f"Add nutritional information to these recipes: {response[:200]}..."
    client.log_llm_call_new(
        session_id=session_id,
        prompt=followup_prompt,
        prompt_number=prompt_number,
        turn_number=2,
        issuer="recipe_agent",
        system_prompt="You are a professional chef assistant"
    )

    nutrition_response = llm.invoke(followup_prompt)

    client.log_llm_response(
        session_id=session_id,
        response=nutrition_response,
        prompt_number=prompt_number,
        turn_number=2,
        input_tokens=450,
        output_tokens=200,
        total_tokens=650
    )

    # PROMPT 2: User asks for vegetarian alternatives
    prompt_number = 2

    # Turn 1: LLM call for vegetarian version
    veg_prompt = "Convert these recipes to vegetarian versions"
    client.log_llm_call_new(
        session_id=session_id,
        prompt=veg_prompt,
        prompt_number=prompt_number,
        turn_number=1,
        issuer="recipe_agent",
        system_prompt="You are a professional chef assistant"
    )

    veg_response = llm.invoke(veg_prompt)

    client.log_llm_response(
        session_id=session_id,
        response=veg_response,
        prompt_number=prompt_number,
        turn_number=1,
        input_tokens=150,
        output_tokens=300,
        total_tokens=450
    )

    # End session successfully (use final prompt_number)
    total_elapsed = int((time.time()) * 1000)
    client.log_session_end(
        session_id=session_id,
        response=f"Generated 3 recipes with nutrition info and vegetarian alternatives",
        prompt_number=prompt_number,
        turn_number=0,
        elapsed_time_ms=total_elapsed,
        meta={"recipes_generated": 3, "total_prompts": prompt_number}
    )

except Exception as e:
    # Log error with current prompt_number
    client.log_error(
        session_id=session_id,
        prompt_number=prompt_number,
        turn_number=1,
        error_message=str(e),
        error_type=type(e).__name__
    )

    # End session with error
    client.log_session_end(
        session_id=session_id,
        response=f"Error: {str(e)}",
        prompt_number=prompt_number,
        turn_number=0,
        elapsed_time_ms=0
    )
```

### Understanding prompt_number and turn_number

- **prompt_number**: Increments for each major user interaction or high-level task
  - Prompt 1: "Generate recipes" (includes all related LLM calls)
  - Prompt 2: "Make them vegetarian" (new user request)
  - Think of it as the conversation's top-level structure

- **turn_number**: Increments for each LLM interaction within a prompt
  - Turn 0: Reserved for session start/end events
  - Turn 1: First LLM call/response pair for this prompt
  - Turn 2: Second LLM call/response pair (follow-up, tool use, etc.)
  - Turn 3+: Additional LLM interactions within the same logical prompt

This structure allows you to:
- Track multi-turn reasoning within a single task (prompt_number=1, turn 1-5)
- Distinguish between separate user requests (prompt_number 1, 2, 3...)
- Analyze how many LLM calls each prompt requires
- Correlate LLM calls with their responses (same prompt_number and turn_number)

## Metadata Best Practices

The `meta` parameter in most log events accepts arbitrary JSON data. Use it to store:

- **Agent configuration**: Model versions, parameters, settings
- **Business context**: Customer IDs, request types, feature flags
- **Performance metrics**: Custom timings, resource usage, cache hits
- **Experiment tracking**: A/B test variants, prompt versions
- **Environment info**: Deployment environment, region, instance ID

Example metadata structure:
```python
meta = {
    "agent_config": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "context": {
        "user_id": "user_12345",
        "request_type": "analysis",
        "priority": "high"
    },
    "performance": {
        "cache_hit": True,
        "preprocessing_ms": 45
    }
}
```

## Analyzing Your Logs

Once logged, you can:

1. **View all runs**: `GET /api/v1/runs` - List all session IDs
2. **Retrieve session logs**: `GET /api/v1/logs/{session_id}` - Get all events for a session
3. **Use the UI**: Access `http://localhost:3000` to visually explore logs

## Integration Patterns

### Decorator Pattern
Wrap agent functions with automatic logging:

```python
def log_agent_run(func):
    def wrapper(*args, **kwargs):
        session_id = f"agent-{uuid.uuid4().hex[:8]}"
        client.log_session_start(session_id, f"Running {func.__name__}", 1, 0)
        try:
            result = func(*args, session_id=session_id, **kwargs)
            client.log_session_end(session_id, "Success", 1, 0)
            return result
        except Exception as e:
            client.log_error(session_id, 1, 0, str(e))
            raise
    return wrapper

@log_agent_run
def analyze_data(data, session_id):
    # Your agent logic here
    pass
```

### Context Manager Pattern
Use Python context managers for automatic session lifecycle:

```python
from contextlib import contextmanager

@contextmanager
def logged_session(client, prompt):
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    client.log_session_start(session_id, prompt, 1, 0)

    try:
        yield session_id
        elapsed = int((time.time() - start_time) * 1000)
        client.log_session_end(session_id, "Success", 1, 0, elapsed)
    except Exception as e:
        client.log_error(session_id, 1, 0, str(e))
        client.log_session_end(session_id, f"Error: {e}", 1, 0, 0)
        raise

# Usage
with logged_session(client, "Process documents") as session_id:
    process_documents(session_id)
```

## Next Steps
- Explore the [Python client examples](../../python-client/examples/) for more integration patterns
- Check out the web UI at `http://localhost:3000` to visualize your logged sessions
