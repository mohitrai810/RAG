from prometheus_client import Counter, Histogram


HTTP_REQUESTS = Counter(
    "rag_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "rag_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path"],
)

CACHE_REQUESTS = Counter(
    "rag_cache_requests_total",
    "Query cache lookups",
    ["result"],
)

RAG_COMPONENT_DURATION = Histogram(
    "rag_component_duration_seconds",
    "RAG component latency",
    ["component"],
)