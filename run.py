import asyncio
import os
import logging
import uvicorn
import yaml

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from romagic.config import SESSION_SECRET_KEY
from romagic.routers import auth, user


logger = logging.getLogger("uvicorn")


async def log_heartbeat():
    """
    Continuously logs a heartbeat message
    """
    while True:
        logger.info("HEARTBEAT: App is still running...")
        await asyncio.sleep(300)  # Log every 5 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to start background tasks on startup.

    :param app: FastAPI app instance
    """
    task = asyncio.create_task(log_heartbeat())  # Start the heartbeat logger
    yield  # Hand control to FastAPI
    task.cancel()  # Cancel task on shutdown


# Initalize FastAPI app
app = FastAPI(lifespan=lifespan)
# Add session middleware for user authentication
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, tags=["user"])
# Serve static files from static/ directory
app.mount("/static", StaticFiles(directory="static"), name="static")
# Use the PORT environment variable, default to 8000 for local development
port = int(os.environ.get("PORT", 8000))
# Run the FastAPI app with the uvicorn server
uvicorn.run(app, host="0.0.0.0", port=port)
