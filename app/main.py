from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin_router import router as admin_router
from app.api.v1.department_router import router as department_router
from app.api.v1.parent_router import router as parent_router
from app.api.v1.parent_student_router import router as parent_student_router
from app.api.v1.student_router import router as student_router
from app.api.v1.teacher_router import router as teacher_router
from app.api.v1.users.routes import router as user_router
from .api.v1.auth.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Auth Service API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(department_router, prefix="/departments", tags=["Departments"])
app.include_router(teacher_router, prefix="/teachers", tags=["Teachers"])
app.include_router(parent_router, prefix="/parents", tags=["Parents"])
app.include_router(student_router, prefix="/students", tags=["Students"])
app.include_router(parent_student_router, prefix="/parent-students", tags=["Parent Students"])
app.include_router(user_router, tags=["Users"])
app.include_router(auth_router, tags=["auth"])


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
