from .login import router as employee_login_router
from .password_reset import router as employee_password_reset_router
from .admin_update import router as employee_admin_update_router
from .profile_update import router as employee_profile_update_router
from .register import router as register_employee_router

__all__ = [
    "employee_login_router",
    "employee_password_reset_router",
    "employee_admin_update_router",
    "employee_profile_update_router",
    "register_employee_router",
]
