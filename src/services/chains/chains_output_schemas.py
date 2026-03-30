from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum



# CONTEXT


class Participant(BaseModel):
    name: Optional[str] = Field(default=None, description="Full name of the participant")
    role: Optional[str] = Field(default=None, description="Role of the participant in the meeting (e.g., engineer, manager)")


class MeetingContextModel(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the meeting")
    participants: Optional[List[Participant]] = Field(default=None, description="List of meeting participants")
    agenda: Optional[List[str]] = Field(default=None, description="List of agenda items discussed in the meeting")
    key_purpose: Optional[str] = Field(default=None, description="Main purpose or goal of the meeting")



# DECISIONS




class Decision(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier for the decision")
    title: Optional[str] = Field(default=None, description="Short title summarizing the decision")
    description: Optional[str] = Field(default=None, description="Detailed explanation of the decision")

    type: Optional[str] = Field(default=None, description="Category of the decision (business, technical, design, etc.)")
    priority: Optional[str] = Field(default=None, description="Priority level of the decision (low, medium, high)")

    constraints: Optional[List[str]] = Field(default=None, description="Constraints or limitations affecting the decision")
    pricing: Optional[str] = Field(default=None, description="Pricing or budget-related information if applicable")

    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score of the decision extraction (0 to 1)")
    segment_id: Optional[str] = Field(default=None, description="Reference to the segment where the decision was mentioned")


class DecisionsOutput(BaseModel):
    decisions: List[Decision] = Field(default_factory=list, description="List of extracted decisions from the meeting")



# TASKS


class Task(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier for the task")
    title: Optional[str] = Field(default=None, description="Short title of the task")
    description: Optional[str] = Field(default=None, description="Detailed description of the task")

    type: Optional[str] = Field(
        default=None,
        description="Task type (action, follow_up, research, implementation, other)"
    )

    owner: Optional[str] = Field(default=None, description="Person responsible for completing the task")
    deadline: Optional[str] = Field(default=None, description="Deadline or due date for the task")

    priority: Optional[str] = Field(default=None, description="Priority level of the task (low, medium, high)")

    constraints: Optional[List[str]] = Field(default=None, description="Constraints affecting task execution")
    target: Optional[str] = Field(default=None, description="Expected outcome or target of the task")

    related_decision_ids: Optional[List[str]] = Field(default=None, description="List of related decision IDs")

    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score of the task extraction (0 to 1)")
    segment_id: Optional[str] = Field(default=None, description="Reference to the segment where the task was mentioned")


class TasksOutput(BaseModel):
    tasks: List[Task] = Field(default_factory=list, description="List of extracted tasks from the meeting")



# CONFLICTS


class Conflict(BaseModel):
    type: Optional[List[str]] = Field(
        default=None,
        description="Types of conflict (e.g., product, technical, design). Can contain multiple values"
    )
    entity: Optional[List[str]] = Field(
        default=None,
        description="Entities involved in the conflict (e.g., decision, task). Can contain multiple values"
    )
    related_ids: Optional[List[str]] = Field(
        default=None,
        description="IDs of related decisions or tasks involved in the conflict"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Explanation of why the conflict exists"
    )


class ConflictsOutput(BaseModel):
    conflicts: List[Conflict] = Field(default_factory=list, description="List of detected conflicts between decisions and tasks")



# RISKS


class Risk(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier for the risk")
    title: Optional[str] = Field(default=None, description="Short title of the risk")
    description: Optional[str] = Field(default=None, description="Detailed explanation of the risk")

    severity: Optional[str] = Field(default=None, description="Severity level of the risk (low, medium, high)")
    likelihood: Optional[str] = Field(default=None, description="Likelihood of the risk occurring")

    mitigation: Optional[str] = Field(default=None, description="Suggested mitigation or resolution for the risk")

    related_task_ids: Optional[List[str]] = Field(default=None, description="List of related task IDs")
    related_decision_ids: Optional[List[str]] = Field(default=None, description="List of related decision IDs")

    segment_id: Optional[str] = Field(default=None, description="Reference to the segment where the risk was identified")


class RisksOutput(BaseModel):
    risks: List[Risk] = Field(default_factory=list, description="List of identified risks")



# SUMMARY


class Summary(BaseModel):
    overview: Optional[str] = Field(default=None, description="General overview of the meeting")
    key_points: Optional[List[str]] = Field(default=None, description="Key discussion points")
    decisions_summary: Optional[List[str]] = Field(default=None, description="Summary of decisions made")
    tasks_summary: Optional[List[str]] = Field(default=None, description="Summary of tasks identified")



# SENTIMENT


class Sentiment(BaseModel):
    overall: Optional[str] = Field(default=None, description="Overall sentiment of the meeting (positive, neutral, negative)")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score of sentiment analysis")
    highlights: Optional[List[str]] = Field(default=None, description="Key highlights affecting sentiment")
    segment_ids: Optional[List[str]] = Field(default=None, description="Segments contributing to the sentiment")



# FINAL OUTPUT


class GenerateOutput(BaseModel):
    context: Optional[MeetingContextModel] = Field(default=None, description="Extracted meeting context")
    decisions: Optional[List[Decision]] = Field(default=None, description="List of decisions")
    tasks: Optional[List[Task]] = Field(default=None, description="List of tasks")
    conflicts: Optional[List[Conflict]] = Field(default=None, description="List of conflicts")
    risks: Optional[List[Risk]] = Field(default=None, description="List of risks")
    summary: Optional[Summary] = Field(default=None, description="Meeting summary")
    sentiment: Optional[Sentiment] = Field(default=None, description="Sentiment analysis of the meeting")