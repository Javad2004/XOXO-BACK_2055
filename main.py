from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/", response_model=list[schemas.User])
def create_update_user(items: list[schemas.Item], db: Session = Depends(get_db)):
    users = []
    
    for item in items:
        db_user = crud.get_user_by_name(db, item.name)
        if db_user:
            if item.status == "Win":
                users.append(crud.update_user_score(db, db_user.name, 1))
            elif item.status == "Lose":
                users.append(crud.update_user_score(db, db_user.name, -1))
        else:
            if item.status == "Win":
                user = schemas.UserCreate(name=item.name, score=1)
                users.append(crud.create_user(db, user))
            elif item.status == "Lose":
                user = schemas.UserCreate(name=item.name, score=0)
                users.append(crud.create_user(db, user))

    return users

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users

@app.get("/users/top10", response_model=list[schemas.User])
def read_users_top10(db: Session = Depends(get_db)):
    users = crud.get_users_top10(db)
    return users

@app.get("/users/get_by_id/{user_id}", response_model=schemas.User)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/get_by_name/{user_name}", response_model=schemas.User)
def read_user_by_name(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user