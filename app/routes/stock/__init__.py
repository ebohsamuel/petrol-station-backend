from .new_delivery import router as new_delivery_router
from .update_delivery import router as update_delivery_router
from .fetch_stock_delivery import router as fetch_stock_delivery_router
from .fetch_inventory import router as fetch_inventory_router

__all__ = [
    "new_delivery_router",
    "update_delivery_router",
    "fetch_stock_delivery_router",
    "fetch_inventory_router",
]
