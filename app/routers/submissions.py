from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import database, models, schemas, auth

router = APIRouter(prefix="/tasks", tags=["Entregas (Submissions)"])

@router.post("/{task_id}/submissions/", response_model=schemas.SubmissionResponse)
def submit_task(
    task_id: int,
    submission: schemas.SubmissionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    is_member = any(member.id == current_user.id for member in task.team.members)
    if not is_member:
        raise HTTPException(status_code=403, detail="No estás inscrito en esta materia")
        
    db_submission = db.query(models.Submission).filter(
        models.Submission.task_id == task_id,
        models.Submission.student_id == current_user.id
    ).first()

    if db_submission:
        db_submission.file_url = submission.file_url # type: ignore
        db_submission.status = models.SubmissionStatus.SUBMITTED.value # type: ignore
    else:
        db_submission = models.Submission(
            task_id=task_id,
            student_id=current_user.id,
            file_url=submission.file_url,
            status=models.SubmissionStatus.SUBMITTED.value
        )
        db.add(db_submission)
        
    db.commit()
    db.refresh(db_submission)
    return db_submission


@router.put("/{task_id}/submissions/{student_id}/grade", response_model=schemas.SubmissionResponse)
def grade_submission(
    task_id: int,
    student_id: int,
    grade_data: schemas.SubmissionGrade,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
        
    if task.team.owner_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Solo el profesor de la materia puede calificar")
        
    db_submission = db.query(models.Submission).filter(
        models.Submission.task_id == task_id,
        models.Submission.student_id == student_id
    ).first()
    
    if not db_submission:
        db_submission = models.Submission(
            task_id=task_id,
            student_id=student_id,
            status=models.SubmissionStatus.GRADED.value,
            grade=grade_data.grade,
            feedback=grade_data.feedback
        )
        db.add(db_submission)
    else:
        db_submission.grade = grade_data.grade # type: ignore
        db_submission.feedback = grade_data.feedback # type: ignore
        db_submission.status = models.SubmissionStatus.GRADED.value # type: ignore
        
    db.commit()
    db.refresh(db_submission)
    return db_submission


@router.get("/{task_id}/submissions/", response_model=List[schemas.SubmissionResponse])
def get_task_submissions(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
        
    if task.team.owner_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Solo el profesor puede ver todas las entregas")
        
    return task.submissions