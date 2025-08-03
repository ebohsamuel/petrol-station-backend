from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import async_engine, Base
from app.routes.employee import *
from app.routes.branch import *
import app.models
from contextlib import asynccontextmanager
from app.utils.general import ExpiredTokenException

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(fetch_branch_router, prefix="/employee", tags=["Employee"])
app.include_router(branch_update_router, prefix="/employee", tags=["Employee"])
app.include_router(branch_register_router, prefix="/employee", tags=["Employee"])
app.include_router(employee_login_router, prefix="/employee", tags=["Employee"])
app.include_router(employee_profile_update_router, prefix="/employee", tags=["Employee"])
app.include_router(register_employee_router, prefix="/employee", tags=["Employee"])
app.include_router(employee_admin_update_router, prefix="/employee", tags=["Employee"])
app.include_router(employee_password_reset_router, prefix="/employee", tags=["Employee"])

origin = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ExpiredTokenException)
async def handle_expired_token(request: Request, exc: ExpiredTokenException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Not authenticated", "redirect": "/login"}
    )
