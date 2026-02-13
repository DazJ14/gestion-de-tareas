from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    PROFESSOR = "professor"
    STUDENT = "student"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str
    due_date: datetime

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    team_id: int
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    invite_code: str
    owner_id: int
    class Config:
        from_attributes = True

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"

class SubmissionBase(BaseModel):
    file_url: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionGrade(BaseModel):
    grade: int
    feedback: Optional[str] = None

class SubmissionResponse(SubmissionBase):
    id: int
    task_id: int
    student_id: int
    status: SubmissionStatus
    grade: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime

    class Config:
        from_attributes = True