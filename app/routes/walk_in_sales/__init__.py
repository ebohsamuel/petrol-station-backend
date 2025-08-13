from .fetch_walk_in_sales import router as fetch_wis_router
from .update_walk_in_sales import router as update_wis_router
from .register_new_walk_in_sales import router as register_new_wis_router

__all__ = [
    "fetch_wis_router",
    "update_wis_router",
    "register_new_wis_router",
]
