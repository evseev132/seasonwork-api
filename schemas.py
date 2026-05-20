from typing import Optional

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    full_name: str
    login: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    login: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    user: UserResponse


class TaskCreateRequest(BaseModel):
    title: str
    description: str
    date: str
    location: str
    employee_id: int


class TaskUpdateRequest(BaseModel):
    title: str
    description: str
    date: str
    location: str
    employee_id: int


class TaskStatusUpdateRequest(BaseModel):
    status: str


class TaskHoursUpdateRequest(BaseModel):
    worked_hours: float


class TaskPhotoUpdateRequest(BaseModel):
    photo_path: str


class TaskReviewUpdateRequest(BaseModel):
    admin_comment: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    date: str
    location: str
    employee_id: int
    status: str
    worked_hours: float
    photo_path: Optional[str] = None
    employee_name: Optional[str] = None
    admin_comment: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    class Config:
        from_attributes = True