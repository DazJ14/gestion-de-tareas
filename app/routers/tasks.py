from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import database, models, schemas, auth

router = APIRouter(prefix="/teams", tags=["Tareas"])

@router.post("/{team_id}/tasks/", response_model=schemas.TaskResponse)
def create_task(
    team_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    if team.owner_id != current_user.id: # type: ignore
        raise HTTPException(status_code=403, detail="Solo el profesor de esta materia puede asignar tareas")
    
    new_task = models.Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        team_id=team_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{team_id}/tasks/", response_model=List[schemas.TaskResponse])
def get_tasks(
    team_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    is_owner = team.owner_id == current_user.id  # type: ignore
    is_member = current_user in team.members
    
    if not is_owner and not is_member: # type: ignore
        raise HTTPException(status_code=403, detail="No tienes acceso a las tareas de esta materia")
    
    return team.tasks