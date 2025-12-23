"""
Prometheus metrics for monitoring LifeAI platform.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import logging

logger = logging.getLogger(__name__)

# ================================================================================
# HTTP Metrics
# ================================================================================

http_requests_total = Counter(
    'lifeai_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'lifeai_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# ================================================================================
# AI/LLM Metrics
# ================================================================================

llm_requests_total = Counter(
    'lifeai_llm_requests_total',
    'Total LLM API requests',
    ['model', 'status']
)

llm_request_duration_seconds = Histogram(
    'lifeai_llm_request_duration_seconds',
    'LLM API request duration in seconds',
    ['model'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

llm_tokens_used_total = Counter(
    'lifeai_llm_tokens_used_total',
    'Total tokens consumed by LLM requests',
    ['model', 'type']  # type: prompt, completion
)

# ================================================================================
# Agent Metrics
# ================================================================================

agent_invocations_total = Counter(
    'lifeai_agent_invocations_total',
    'Total agent invocations',
    ['agent_type', 'intent_type']
)

agent_response_duration_seconds = Histogram(
    'lifeai_agent_response_duration_seconds',
    'Agent response time in seconds',
    ['agent_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

multi_agent_coordination_count = Counter(
    'lifeai_multi_agent_coordination_count',
    'Number of multi-agent coordinations',
    ['routing_type']
)

# ================================================================================
# Session Metrics
# ================================================================================

active_sessions = Gauge(
    'lifeai_active_sessions',
    'Number of active chat sessions'
)

sessions_created_total = Counter(
    'lifeai_sessions_created_total',
    'Total sessions created'
)

sessions_ended_total = Counter(
    'lifeai_sessions_ended_total',
    'Total sessions ended'
)

session_duration_seconds = Histogram(
    'lifeai_session_duration_seconds',
    'Session duration in seconds',
    buckets=(60, 300, 600, 1800, 3600, 7200, 14400)  # 1m, 5m, 10m, 30m, 1h, 2h, 4h
)

messages_per_session = Histogram(
    'lifeai_messages_per_session',
    'Number of messages per session',
    buckets=(1, 5, 10, 20, 50, 100, 200)
)

# ================================================================================
# Vector DB Metrics
# ================================================================================

vector_db_operations_total = Counter(
    'lifeai_vector_db_operations_total',
    'Total vector DB operations',
    ['operation', 'status']  # operation: upsert, search, delete
)

vector_db_search_duration_seconds = Histogram(
    'lifeai_vector_db_search_duration_seconds',
    'Vector DB search duration in seconds',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
)

vector_db_documents_total = Gauge(
    'lifeai_vector_db_documents_total',
    'Total documents in vector database'
)

# ================================================================================
# Redis Metrics
# ================================================================================

redis_operations_total = Counter(
    'lifeai_redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']  # operation: get, set, delete
)

redis_connection_status = Gauge(
    'lifeai_redis_connection_status',
    'Redis connection status (1=connected, 0=disconnected)'
)

# ================================================================================
# Multimodal Metrics
# ================================================================================

multimodal_requests_total = Counter(
    'lifeai_multimodal_requests_total',
    'Total multimodal requests',
    ['modality', 'operation']  # modality: voice, image; operation: transcribe, analyze, tts
)

multimodal_request_duration_seconds = Histogram(
    'lifeai_multimodal_request_duration_seconds',
    'Multimodal request duration in seconds',
    ['modality', 'operation'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

multimodal_file_size_bytes = Histogram(
    'lifeai_multimodal_file_size_bytes',
    'Multimodal file size in bytes',
    ['modality'],
    buckets=(1024, 10240, 102400, 1048576, 10485760, 26214400)  # 1KB, 10KB, 100KB, 1MB, 10MB, 25MB
)

# ================================================================================
# Error Metrics
# ================================================================================

errors_total = Counter(
    'lifeai_errors_total',
    'Total errors',
    ['error_type', 'component']
)

# ================================================================================
# Business Metrics
# ================================================================================

user_registrations_total = Counter(
    'lifeai_user_registrations_total',
    'Total user registrations'
)

user_logins_total = Counter(
    'lifeai_user_logins_total',
    'Total user logins',
    ['status']  # success, failed
)

premium_users_total = Gauge(
    'lifeai_premium_users_total',
    'Number of premium users'
)

# ================================================================================
# Application Info
# ================================================================================

app_info = Info(
    'lifeai_app',
    'Application information'
)

# Set application info
app_info.info({
    'version': '2.1.0',
    'environment': 'development',  # Will be overridden by env var
})

logger.info("✅ Prometheus metrics initialized")
