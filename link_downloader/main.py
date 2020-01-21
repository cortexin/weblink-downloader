import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from .models import database
from .routers import auth, links


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event('startup')
async def startup_handler():
    await database.connect()
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    loop.set_default_executor(executor)


@app.on_event('shutdown')
async def shutdown_hander():
    await database.disconnect()


app.include_router(
    auth.router,
    prefix='/auth'
)
app.include_router(
    links.router,
    prefix='/links'
)
