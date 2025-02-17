from fastapi import APIRouter
from .agent_routes import router as agent_router
from .class_routes import router as class_router
from .document_routes import router as document_router

router = APIRouter()
router.include_router(agent_router)
router.include_router(class_router)
router.include_router(document_router) 