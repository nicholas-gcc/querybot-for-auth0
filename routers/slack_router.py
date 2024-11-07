from fastapi import APIRouter, Request
from ..services.slack_service import app_handler 

router = APIRouter()

@router.post("/slack/events")
async def handle_request(req: Request):
    return await app_handler.handle(req)