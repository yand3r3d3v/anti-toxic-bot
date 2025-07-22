from .history import router as history_router
from .message import router as message_router
from .muted import router as muted_router
from .start import router as start_router
from .toxic import router as toxic_router
from .unmute import router as unmute_router

routers = [
    start_router,
    message_router,
    history_router,
    toxic_router,
    muted_router,
    unmute_router,
]
