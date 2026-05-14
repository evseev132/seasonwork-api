from database import Base, SessionLocal, engine
from models import Task, User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    existing_admin = db.query(User).filter(User.login == "admin").first()

    if existing_admin is None:
        admin = User(
            full_name="Иван Петров",
            login="admin",
            password="1234",
            role="ADMIN"
        )

        worker_1 = User(
            full_name="Алексей Смирнов",
            login="worker",
            password="1234",
            role="EMPLOYEE"
        )

        worker_2 = User(
            full_name="Дмитрий Орлов",
            login="worker2",
            password="1234",
            role="EMPLOYEE"
        )

        db.add(admin)
        db.add(worker_1)
        db.add(worker_2)
        db.commit()

        db.refresh(worker_1)
        db.refresh(worker_2)

        task_1 = Task(
            title="Покос травы",
            description="Покосить траву на участке №1",
            date="2026-05-11",
            location="Объект A",
            employee_id=worker_1.id,
            status="NEW",
            worked_hours=0.0,
            photo_path=None
        )

        task_2 = Task(
            title="Уборка территории",
            description="Убрать мусор после работ",
            date="2026-05-12",
            location="Объект B",
            employee_id=worker_1.id,
            status="IN_PROGRESS",
            worked_hours=0.0,
            photo_path=None
        )

        task_3 = Task(
            title="Проверка инвентаря",
            description="Проверить рабочий инструмент перед сменой",
            date="2026-05-13",
            location="Склад",
            employee_id=worker_2.id,
            status="NEW",
            worked_hours=0.0,
            photo_path=None
        )

        db.add(task_1)
        db.add(task_2)
        db.add(task_3)
        db.commit()

        print("База успешно заполнена тестовыми данными")
    else:
        print("Тестовые данные уже есть в базе")

finally:
    db.close()