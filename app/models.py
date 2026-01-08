from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TaskDefinition(BaseModel):
    task_name: str
    steps: List[str]
    completion_criteria: str
    sequential: bool = False  # Whether steps must be done in order

class FrameObservation(BaseModel):
    timestamp: float
    observation: str
    mapped_step: Optional[str] = None
    confidence: float

class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskState(BaseModel):
    task_name: str
    status: TaskStatus
    what_happened: List[str] = Field(default_factory=list)
    observed_steps: List[str] = Field(default_factory=list)
    missing_steps: List[str] = Field(default_factory=list)
    current_activity: Optional[str] = None
    explanation: Optional[str] = None
    confidence: float = 0.0
    next_expected_step: Optional[str] = None  # For sequential tasks

class EvaluateFrameRequest(BaseModel):
    task_name: str
    image_base64: str
    timestamp: float
