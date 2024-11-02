from fastapi import APIRouter
from v1.api import endpoints_router

router = APIRouter()

router.include_router(endpoints_router,prefix="")
