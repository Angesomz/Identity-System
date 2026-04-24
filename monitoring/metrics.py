from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Define Metrics
REQUEST_COUNT = Counter("insa_request_count", "Total request count", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("insa_request_latency_seconds", "Request latency", ["endpoint"])
LIVENESS_FAILURE = Counter("insa_liveness_failure_count", "Spoofing attempts detected")
MATCH_CONFIDENCE = Histogram("insa_match_confidence_score", "Distribution of match confidence scores")

def metrics_endpoint():
    """Expose metrics for Prometheus scraping."""
    return Response(generate_latest(), media_type="text/plain")

def record_request(method, endpoint, status):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()

def record_spoof_attempt():
    LIVENESS_FAILURE.inc()
