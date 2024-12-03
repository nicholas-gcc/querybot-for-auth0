import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .routers import slack_router


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(slack_router.router)


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint for the application.

    Returns:
        JSONResponse: A JSON response with a welcome message.
    """
    logger.info("Root endpoint called.")
    return JSONResponse(content={"message": "Hello Bigger Applications!"})
