from fastapi import FastAPI

from app.routers import submissions, users, tasks, teams
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Teams API")

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(submissions.router)

@app.get("/")
def home():
    return {"message": "API de Gestión Escolar funcionando"}

# Solo dios y yo sabemos lo que estos codigos hacian anoche