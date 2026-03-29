# models/chain_models.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


#  CONTEXT 

class Participant(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Participant name as mentioned in the meeting. Null if unknown."
    )
    role: Optional[str] = Field(
        default=None,
        description="Participant role (e.g., engineer, manager). Null if not specified."
    )


class MeetingContextModel(BaseModel):
    title: str = Field(
        description="Short descriptive title summarizing the meeting topic."
    )
    participants: List[Participant] = Field(
        description="List of participants mentioned in the meeting."
    )
    agenda: List[str] = Field(
        description="List of main discussion topics or agenda points."
    )
    key_purpose: str = Field(
        description="Primary objective or purpose of the meeting."
    )


#  DECISIONS 

class DecisionType(str, Enum):
    BUSINESS = "business"
    TECHNICAL = "technical"
    DESIGN = "design"
    FINANCE = "finance"
    PRODUCT = "product"
    OTHER = "other"


class Decision(BaseModel):
    id: str = Field(
        description="Unique identifier for the decision (must be generated, not reused from segment_id)."
    )
    title: str = Field(
        description="Short title summarizing the decision."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed explanation of the decision."
    )

    type: DecisionType = Field(
        description="Category of the decision."
    )
    priority: Optional[str] = Field(
        default=None,
        description="Priority level if mentioned (e.g., low, medium, high)."
    )

    constraints: Optional[List[str]] = Field(
        default=None,
        description="List of constraints affecting the decision (e.g., budget, timeline)."
    )
    pricing: Optional[str] = Field(
        default=None,
        description="Any pricing or cost-related information mentioned."
    )

    confidence: float = Field(
        description="Confidence score between 0 and 1 indicating how certain the decision extraction is.",
        ge=0,
        le=1
    )

    segment_id: str = Field(
        description="ID of the segment where this decision was identified. MUST match input segment_id."
    )


#  TASKS 

class TaskType(str, Enum):
    ACTION = "action"
    FOLLOW_UP = "follow_up"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    OTHER = "other"


class Task(BaseModel):
    id: str = Field(
        description="Unique identifier for the task."
    )
    title: str = Field(
        description="Short actionable task title."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed explanation of the task."
    )

    type: TaskType = Field(
        description="Type of task (action, follow_up, research, implementation, other)."
    )

    owner: Optional[str] = Field(
        default=None,
        description="Person responsible for the task if mentioned."
    )
    deadline: Optional[str] = Field(
        default=None,
        description="Deadline or due date if mentioned (keep original format, do NOT normalize)."
    )

    priority: Optional[str] = Field(
        default=None,
        description="Priority level if mentioned."
    )

    constraints: Optional[List[str]] = Field(
        default=None,
        description="Constraints affecting task execution."
    )
    target: Optional[str] = Field(
        default=None,
        description="Target outcome or deliverable of the task."
    )

    related_decision_ids: List[str] = Field(
        description="List of decision IDs that this task depends on or relates to. Empty list if none."
    )

    confidence: float = Field(
        description="Confidence score between 0 and 1.",
        ge=0,
        le=1
    )

    segment_id: str = Field(
        description="ID of the segment where this task was identified. MUST match input segment_id."
    )


#  CONFLICT 

class Conflict(BaseModel):
    type: str = Field(
        description="Type of conflict (e.g., contradiction, dependency_conflict)."
    )
    entity: str = Field(
        description="Entity type involved in conflict: 'decision' or 'task'."
    )
    related_ids: List[str] = Field(
        description="IDs of decisions or tasks involved in the conflict."
    )
    reason: str = Field(
        description="Clear explanation of why the conflict exists."
    )


#  RISKS 

class Risk(BaseModel):
    id: str = Field(
        description="Unique identifier for the risk."
    )
    title: str = Field(
        description="Short title describing the risk."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed description of the risk."
    )

    severity: str = Field(
        description="Severity level (e.g., low, medium, high)."
    )
    likelihood: Optional[str] = Field(
        default=None,
        description="Likelihood of the risk occurring."
    )

    mitigation: Optional[str] = Field(
        default=None,
        description="Suggested mitigation strategy if mentioned."
    )

    related_task_ids: List[str] = Field(
        description="Tasks impacted by this risk."
    )
    related_decision_ids: List[str] = Field(
        description="Decisions impacted by this risk."
    )

    segment_id: str = Field(
        description="ID of the segment where this risk was identified."
    )


#  SUMMARY 

class Summary(BaseModel):
    overview: str = Field(
        description="High-level summary of the meeting."
    )
    key_points: List[str] = Field(
        description="Key discussion points."
    )
    decisions_summary: List[str] = Field(
        description="Summary of decisions made."
    )
    tasks_summary: List[str] = Field(
        description="Summary of tasks assigned."
    )


#  SENTIMENT 

class Sentiment(BaseModel):
    overall: str = Field(
        description="Overall sentiment (positive, neutral, negative)."
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1.",
        ge=0,
        le=1
    )
    highlights: List[str] = Field(
        description="Important emotional highlights or moments."
    )
    segment_ids: List[str] = Field(
        description="Segments contributing to the sentiment."
    )


#  FINAL 

class GenerateOutput(BaseModel):
    context: MeetingContextModel = Field(
        description="Structured meeting context."
    )
    decisions: List[Decision] = Field(
        description="List of extracted decisions."
    )
    tasks: List[Task] = Field(
        description="List of actionable tasks."
    )
    conflicts: List[Conflict] = Field(
        description="Detected conflicts between decisions or tasks."
    )
    risks: List[Risk] = Field(
        description="Identified risks."
    )
    summary: Summary = Field(
        description="Structured meeting summary."
    )
    sentiment: Sentiment = Field(
        description="Meeting sentiment analysis."
    )