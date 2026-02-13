from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)

class UserRole(str, enum.Enum):
    PROFESSOR = "professor"
    STUDENT = "student"

class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.STUDENT.value)
    
    managed_teams = relationship("Team", back_populates="owner")
    teams = relationship("Team", secondary=enrollments, back_populates="members")
    submissions = relationship("Submission", back_populates="student")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    invite_code = Column(String, unique=True, index=True) # código tipo "XJ92L"
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="managed_teams")
    members = relationship("User", secondary=enrollments, back_populates="teams")
    tasks = relationship("Task", back_populates="team")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    team_id = Column(Integer, ForeignKey("teams.id"))
    
    team = relationship("Team", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String, default=SubmissionStatus.PENDING.value) 
    
    file_url = Column(String, nullable=True) 
    
    grade = Column(Integer, nullable=True)
    feedback = Column(String, nullable=True)
    
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    task = relationship("Task", back_populates="submissions")
    student = relationship("User", back_populates="submissions")