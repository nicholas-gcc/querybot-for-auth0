import logging

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from ..services.slack_service import app_handler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/slack/events")
async def handle_request(req: Request) -> Response:
    """
    Endpoint to handle incoming Slack events.

    Args:
        req (Request): The incoming request from Slack.

    Returns:
        Response: The response to be sent back to Slack.
    """
    try:
        logger.debug("Received a request at /slack/events")
        return await app_handler.handle(req)
    except Exception as e:
        logger.exception("Error handling Slack event.")
        return JSONResponse(
            content={"error": "Internal Server Error"}, status_code=500
        )
