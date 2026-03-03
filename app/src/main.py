from fastapi import FastAPI, Request, Response 
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = FastAPI()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_request_count",
    "Total number of requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Count requests
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()

    # Track latency
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)

    return response

@app.get("/")
def root():
    return {"message": "SRE Observability Platform is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
