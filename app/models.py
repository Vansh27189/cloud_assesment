"""Pydantic data models and schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status (healthy/degraded)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    instance_id: str = Field(..., description="Unique node/container instance identifier")
    environment: str = Field(..., description="Deployment environment (e.g. production, aws-ec2)")
    memory_usage_mb: float = Field(..., description="Current process resident memory in MB")
    cpu_percent: float = Field(..., description="Current CPU utilization percentage")


class SystemInfoResponse(BaseModel):
    """System information response schema."""

    service_name: str
    version: str
    instance_id: str
    hostname: str
    platform: str
    python_version: str
    environment: str
    features: List[str]


class AnalyzeRequest(BaseModel):
    """Text analysis request payload."""

    text: str = Field(..., min_length=1, max_length=10000, description="Text string to analyze")
    category: Optional[str] = Field("general", description="Optional text classification category")


class KeywordItem(BaseModel):
    """Keyword frequency item."""

    word: str
    count: int


class SentimentAnalysisResult(BaseModel):
    """Result of NLP sentiment and text analytics."""

    text_preview: str
    polarity_score: float = Field(..., description="Polarity score from -1.0 (very negative) to +1.0 (very positive)")
    sentiment_label: str = Field(..., description="POSITIVE, NEUTRAL, or NEGATIVE")
    word_count: int
    char_count: int
    estimated_read_time_seconds: float
    keywords: List[KeywordItem]
    processed_by_instance: str
    processed_at: str


class TaskCreateRequest(BaseModel):
    """Task creation request."""

    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field("", max_length=500)
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")


class TaskItem(BaseModel):
    """Distributed task representation."""

    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    processed_by: str


class MetricsResponse(BaseModel):
    """Service runtime metrics schema."""

    service_name: str
    instance_id: str
    uptime_seconds: float
    total_requests: int
    total_analyses: int
    total_tasks: int
    requests_by_endpoint: Dict[str, int]
    avg_latency_ms: float
