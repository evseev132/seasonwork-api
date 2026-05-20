from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Task, User
from schemas import (
    LoginRequest,
    LoginResponse,
    TaskCreateRequest,
    TaskHoursUpdateRequest,
    TaskPhotoUpdateRequest,
    TaskResponse,
    TaskReviewUpdateRequest,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
    UserRegisterRequest,
    UserResponse,
)

Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    connection.exec_driver_sql(
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS admin_comment TEXT"
    )
    connection.exec_driver_sql(
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS started_at TIMESTAMP"
    )
    connection.exec_driver_sql(
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP"
    )

app = FastAPI(
    title="SeasonWork API",
    description="API для Android-приложения SeasonWork",
    version="1.0.0"
)


def task_to_response(task: Task) -> TaskResponse:
    employee_name = None

    if task.employee is not None:
        employee_name = task.employee.full_name

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        date=task.date,
        location=task.location,
        employee_id=task.employee_id,
        status=task.status,
        worked_hours=task.worked_hours,
        photo_path=task.photo_path,
        employee_name=employee_name,
        admin_comment=task.admin_comment,
        started_at=task.started_at.isoformat() if task.started_at is not None else None,
        finished_at=task.finished_at.isoformat() if task.finished_at is not None else None
    )


@app.get("/")
def root():
    return {
        "message": "SeasonWork API работает"
    }


@app.post("/register", response_model=UserResponse)
def register(
        request: UserRegisterRequest,
        db: Session = Depends(get_db)
):
    allowed_roles = ["ADMIN", "EMPLOYEE"]

    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Некорректная роль пользователя"
        )

    existing_user = db.query(User).filter(User.login == request.login).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )

    user = User(
        full_name=request.full_name.strip(),
        login=request.login.strip(),
        password=request.password.strip(),
        role=request.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/login", response_model=LoginResponse)
def login(
        request: LoginRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.login == request.login).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    if user.password != request.password:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    return LoginResponse(
        user=UserResponse(
            id=user.id,
            full_name=user.full_name,
            login=user.login,
            role=user.role
        )
    )


@app.get("/users", response_model=List[UserResponse])
def get_users(
        db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users


@app.get("/users/employees", response_model=List[UserResponse])
def get_employees(
        db: Session = Depends(get_db)
):
    employees = db.query(User).filter(User.role == "EMPLOYEE").all()

    return employees


@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(
        db: Session = Depends(get_db)
):
    tasks = db.query(Task).all()

    return [
        task_to_response(task)
        for task in tasks
    ]


@app.get("/tasks/employee/{employee_id}", response_model=List[TaskResponse])
def get_tasks_by_employee(
        employee_id: int,
        db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.employee_id == employee_id).all()

    return [
        task_to_response(task)
        for task in tasks
    ]


@app.post("/tasks", response_model=TaskResponse)
def create_task(
        request: TaskCreateRequest,
        db: Session = Depends(get_db)
):
    employee = db.query(User).filter(User.id == request.employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Сотрудник не найден"
        )

    if employee.role != "EMPLOYEE":
        raise HTTPException(
            status_code=400,
            detail="Задачу можно назначить только сотруднику"
        )

    task = Task(
        title=request.title.strip(),
        description=request.description.strip(),
        date=request.date.strip(),
        location=request.location.strip(),
        employee_id=request.employee_id,
        status="NEW",
        worked_hours=0.0,
        photo_path=None,
        admin_comment=None,
        started_at=None,
        finished_at=None
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task_to_response(task)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        request: TaskUpdateRequest,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    employee = db.query(User).filter(User.id == request.employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Сотрудник не найден"
        )

    if employee.role != "EMPLOYEE":
        raise HTTPException(
            status_code=400,
            detail="Задачу можно назначить только сотруднику"
        )

    task.title = request.title.strip()
    task.description = request.description.strip()
    task.date = request.date.strip()
    task.location = request.location.strip()
    task.employee_id = request.employee_id

    db.commit()
    db.refresh(task)

    return task_to_response(task)


@app.delete("/tasks/{task_id}")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Задача успешно удалена"
    }


@app.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
        task_id: int,
        request: TaskStatusUpdateRequest,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    allowed_statuses = ["NEW", "IN_PROGRESS", "DONE"]

    if request.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Некорректный статус"
        )

    now = datetime.utcnow()

    if request.status == "IN_PROGRESS":
        task.status = "IN_PROGRESS"

        if task.started_at is None:
            task.started_at = now

        task.finished_at = None

    elif request.status == "DONE":
        task.status = "DONE"

        if task.started_at is None:
            task.started_at = now

        task.finished_at = now

        seconds = (task.finished_at - task.started_at).total_seconds()
        hours = seconds / 3600

        task.worked_hours = round(hours, 2)

    elif request.status == "NEW":
        task.status = "NEW"
        task.started_at = None
        task.finished_at = None
        task.worked_hours = 0.0

    db.commit()
    db.refresh(task)

    return task_to_response(task)


@app.patch("/tasks/{task_id}/hours", response_model=TaskResponse)
def update_task_hours(
        task_id: int,
        request: TaskHoursUpdateRequest,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    if request.worked_hours < 0:
        raise HTTPException(
            status_code=400,
            detail="Количество часов не может быть отрицательным"
        )

    if request.worked_hours > 24:
        raise HTTPException(
            status_code=400,
            detail="Количество часов не может быть больше 24"
        )

    task.worked_hours = request.worked_hours

    db.commit()
    db.refresh(task)

    return task_to_response(task)


@app.patch("/tasks/{task_id}/photo", response_model=TaskResponse)
def update_task_photo(
        task_id: int,
        request: TaskPhotoUpdateRequest,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    task.photo_path = request.photo_path

    db.commit()
    db.refresh(task)

    return task_to_response(task)


@app.patch("/tasks/{task_id}/review", response_model=TaskResponse)
def update_task_review(
        task_id: int,
        request: TaskReviewUpdateRequest,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )

    if task.status != "DONE":
        raise HTTPException(
            status_code=400,
            detail="Комментарий можно оставить только к выполненной задаче"
        )

    task.admin_comment = request.admin_comment.strip()

    db.commit()
    db.refresh(task)

    return task_to_response(task)