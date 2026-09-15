"""Plugin lifecycle for the jeeflow-backed workflow replacement."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .runtime import get_runtime


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    runtime = get_runtime()
    await runtime.start()
    try:
        yield
    finally:
        await runtime.stop()
