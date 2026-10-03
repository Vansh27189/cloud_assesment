"""CloudPulse Microservice - Main FastAPI Application."""

import os
import platform
import socket
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

try:
    import psutil
except ImportError:
    psutil = None

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import (
    AnalyzeRequest,
    HealthResponse,
    MetricsResponse,
    SentimentAnalysisResult,
    SystemInfoResponse,
    TaskCreateRequest,
    TaskItem,
)
from app.services.analyzer import analyze_sentiment
from app.services.task_store import task_store

# Application initialization
settings = get_settings()
START_TIME = time.time()

app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    description=(
        "Production-grade containerized microservice engineered for AWS deployment, "
        "featuring automated CI/CD, distributed load balancing telemetry, and NLP analytics."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for distributed and multi-domain testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory telemetry metrics
metrics_data = {
    "total_requests": 0,
    "total_analyses": 0,
    "latency_accumulator_ms": 0.0,
    "endpoint_hits": defaultdict(int),
}


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """Intercept requests to record latency, endpoint metrics, and inject distributed node headers."""
    t0 = time.perf_counter()
    response: Response = await call_next(request)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Record metrics
    metrics_data["total_requests"] += 1
    metrics_data["latency_accumulator_ms"] += elapsed_ms
    path_key = request.url.path
    metrics_data["endpoint_hits"][path_key] += 1

    # Inject distributed load balancing headers
    response.headers["X-Instance-ID"] = settings.INSTANCE_ID
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    response.headers["X-Service-Version"] = settings.VERSION

    return response


# Static files setup
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Dashboard"], include_in_schema=False)
async def serve_dashboard():
    """Serve the interactive microservice presentation dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={
            "message": "CloudPulse Microservice is active.",
            "documentation": "/docs",
            "health": "/health",
        }
    )


@app.get("/health", response_model=HealthResponse, tags=["Observability"])
async def health_check():
    """Liveness and readiness probe for container orchestrators (AWS ECS, Kubernetes, ALB)."""
    memory_mb = 28.5
    cpu_usage = 1.2
    if psutil is not None:
        try:
            current_process = psutil.Process(os.getpid())
            mem_info = current_process.memory_info()
            memory_mb = round(mem_info.rss / (1024 * 1024), 2)
            cpu_usage = round(current_process.cpu_percent(interval=None), 2)
        except Exception:
            pass

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        instance_id=settings.INSTANCE_ID,
        environment=settings.ENVIRONMENT,
        memory_usage_mb=memory_mb,
        cpu_percent=cpu_usage,
    )


@app.get("/api/info", response_model=SystemInfoResponse, tags=["Observability"])
async def system_info():
    """System and environment metadata for distributed tracing and node inspection."""
    return SystemInfoResponse(
        service_name=settings.SERVICE_NAME,
        version=settings.VERSION,
        instance_id=settings.INSTANCE_ID,
        hostname=socket.gethostname(),
        platform=f"{platform.system()} {platform.release()}",
        python_version=platform.python_version(),
        environment=settings.ENVIRONMENT,
        features=[
            "Containerized (Docker)",
            "Automated CI/CD (GitHub Actions)",
            "Load Balancer Ready (Nginx / AWS ALB)",
            "Microservice NLP Text Analysis",
            "Distributed Task Repository",
            "Real-time Telemetry & Metrics",
        ],
    )


@app.post("/api/analyze", response_model=SentimentAnalysisResult, tags=["NLP Analytics"])
async def run_analysis(payload: AnalyzeRequest):
    """Process text for sentiment polarity, readability, and key token extraction."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text payload cannot be empty.",
        )

    metrics_data["total_analyses"] += 1
    result = analyze_sentiment(payload.text, settings.INSTANCE_ID)
    return result


@app.get("/api/tasks", response_model=List[TaskItem], tags=["Distributed Tasks"])
async def list_tasks(limit: int = 50):
    """Retrieve recent queued/processed distributed tasks."""
    return task_store.get_all(limit=limit)


@app.post("/api/tasks", response_model=TaskItem, status_code=status.HTTP_201_CREATED, tags=["Distributed Tasks"])
async def create_task(payload: TaskCreateRequest):
    """Submit a task to the distributed worker store."""
    task = task_store.create_task(payload, settings.INSTANCE_ID)
    return task


@app.delete("/api/tasks/{task_id}", tags=["Distributed Tasks"])
async def remove_task(task_id: str):
    """Delete a task from the distributed store."""
    deleted = task_store.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found.",
        )
    return {"message": f"Task {task_id} deleted successfully."}


@app.get("/metrics", response_model=MetricsResponse, tags=["Observability"])
async def get_metrics():
    """Return runtime telemetry, latency averages, and endpoint hit frequencies."""
    total_reqs = metrics_data["total_requests"]
    avg_latency = (
        round(metrics_data["latency_accumulator_ms"] / total_reqs, 2)
        if total_reqs > 0
        else 0.0
    )

    return MetricsResponse(
        service_name=settings.SERVICE_NAME,
        instance_id=settings.INSTANCE_ID,
        uptime_seconds=round(time.time() - START_TIME, 2),
        total_requests=total_reqs,
        total_analyses=metrics_data["total_analyses"],
        total_tasks=task_store.count(),
        requests_by_endpoint=dict(metrics_data["endpoint_hits"]),
        avg_latency_ms=avg_latency,
    )
