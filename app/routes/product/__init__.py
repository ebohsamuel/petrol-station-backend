from .register import router as register_product_router
from .fetch import router as fetch_product_router
from .update import router as update_product_router

__all__ = [
    "register_product_router",
    "fetch_product_router",
    "update_product_router",
]
