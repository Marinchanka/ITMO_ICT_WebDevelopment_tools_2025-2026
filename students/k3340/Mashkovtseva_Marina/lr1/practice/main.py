from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from models import Warrior, Profession, Skill, RaceType
from connection import get_session, init_db

app = FastAPI()



@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/warriors_list", response_model=List[Warrior])
def warriors_list(session: Session = Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors


@app.get("/warrior/{warrior_id}", response_model=Warrior)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.post("/warrior", response_model=Warrior)
def warriors_create(warrior: Warrior, session: Session = Depends(get_session)):
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"status": 201, "message": "deleted"}


@app.put("/warrior/{warrior_id}", response_model=Warrior)
def warrior_update(warrior_id: int, warrior_update: Warrior, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    # Обновляем поля
    warrior.name = warrior_update.name
    warrior.race = warrior_update.race
    warrior.level = warrior_update.level
    warrior.profession_id = warrior_update.profession_id

    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.get("/professions", response_model=List[Profession])
def get_professions(session: Session = Depends(get_session)):
    professions = session.exec(select(Profession)).all()
    return professions


@app.get("/profession/{profession_id}", response_model=Profession)
def get_profession(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.post("/profession", response_model=Profession)
def create_profession(profession: Profession, session: Session = Depends(get_session)):
    session.add(profession)
    session.commit()
    session.refresh(profession)
    return profession


@app.delete("/profession/{profession_id}")
def delete_profession(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"status": 200, "message": "deleted"}


@app.put("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, profession_update: Profession, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")

    profession.title = profession_update.title
    profession.description = profession_update.description

    session.add(profession)
    session.commit()
    session.refresh(profession)
    return profession


@app.get("/skills", response_model=List[Skill])
def get_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    return skills


@app.post("/warrior/{warrior_id}/skill/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)

    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")

    if skill not in warrior.skills:
        warrior.skills.append(skill)
        session.commit()

    return {"status": 200, "message": "Skill added to warrior"}