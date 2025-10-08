-- Initialize ClickHouse database and tables
CREATE DATABASE IF NOT EXISTS coagent;

USE coagent;

CREATE TABLE IF NOT EXISTS usage_events (
    timestamp DateTime DEFAULT now(),
    usage_event_type String,
    message String
) ENGINE = MergeTree()
ORDER BY timestamp;

-- Table for storing CoAgent log entries
-- Using native ClickHouse JSON type for complex data structures
-- Using proper enums for type safety and query performance
CREATE TABLE IF NOT EXISTS log_entries (
    log_id String,
    timestamp DateTime64(3),
    version String,
    session_id String,
    prompt_number UInt32,
    turn_number UInt32,
    event_id String,
    event_type Enum8(
        'session_start' = 1,
        'session_end' = 2,
        'user_input' = 3,
        'component_enter' = 4,
        'component_exit' = 5,
        'routing' = 6,
        'consensus_success' = 7,
        'consensus_failure' = 8,
        'tool_call' = 9,
        'tool_response' = 10,
        'error' = 11,
        'recovery' = 12,
        'performance_degradation' = 13,
        'human_oversight' = 14,
        'test_result' = 15,
        'llm_call' = 16,
        'llm_response' = 17
    ),
    event_data JSON,
    agent_stack Array(String),
    prompt Nullable(String),
    conversation_context Nullable(JSON),
    meta Nullable(JSON),
    custom_metadata Nullable(JSON),
    additional_properties Nullable(JSON)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (session_id, timestamp, event_id);