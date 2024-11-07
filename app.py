from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

from fastapi import FastAPI
from .routers import slack_router

app = FastAPI()

app.include_router(slack_router.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}