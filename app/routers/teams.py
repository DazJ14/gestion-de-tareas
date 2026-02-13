from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import database, models, schemas, auth, utils

router = APIRouter(prefix="/teams", tags=["Materias (Teams)"])

@router.post("/", response_model=schemas.TeamResponse)
def create_team(
    team: schemas.TeamCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if str(current_user.role) != models.UserRole.PROFESSOR.value:
        raise HTTPException(status_code=403, detail="Solo los profesores pueden crear materias")

    code = utils.generate_invite_code()
    while db.query(models.Team).filter(models.Team.invite_code == code).first():
        code = utils.generate_invite_code()

    new_team = models.Team(
        name=team.name,
        invite_code=code,
        owner_id=current_user.id
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

@router.post("/join/{invite_code}", response_model=schemas.TeamResponse)
def join_team(
    invite_code: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    team = db.query(models.Team).filter(models.Team.invite_code == invite_code).first()
    if not team:
        raise HTTPException(status_code=404, detail="Código de invitación inválido")

    if team in current_user.teams:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en esta materia")

    current_user.teams.append(team)
    db.commit()
    return team

@router.get("/my-teams", response_model=List[schemas.TeamResponse])
def read_my_teams(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if str(current_user.role) == models.UserRole.PROFESSOR.value:
        return current_user.managed_teams
    return current_user.teams

@router.get("/{team_id}/members", response_model=List[schemas.UserResponse])
def get_team_members(
    team_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    if team.owner_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Solo el profesor puede ver la lista de alumnos")

    return team.members