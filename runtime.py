"""jeeflow engine wiring for the existing FBA workflow plugin slot."""

from __future__ import annotations

import asyncio
from typing import Any

import aiomysql
from .vendor.jeeflow_python.jeeflow import (
    EngineExtensions,
    EngineImpl,
    HandlerRegistry,
    JeeflowFacade,
    register_builtin_assignments,
)
from .vendor.jeeflow_python.jeeflow.repository import JdbcRepository, MySqlAdapter, TsIDGenerator
from .vendor.jeeflow_python.jeeflow.repository.ext import JdbcProcessExtRepository

from backend.core.conf import settings

from .providers import FlzkExpressionEvaluator, FlzkOrgUserProvider, FlzkUserProvider, search_users


class JeeflowRuntime:
    """Owns the jeeflow engine and its database pool."""

    def __init__(self) -> None:
        self._pool: Any = None
        self._lock = asyncio.Lock()
        self.facade: JeeflowFacade | None = None

    async def start(self) -> None:
        async with self._lock:
            if self.facade is not None:
                return
            if settings.DATABASE_TYPE != 'mysql':
                raise RuntimeError('jeeflow plugin currently requires DATABASE_TYPE=mysql')

            self._pool = await aiomysql.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                db=settings.DATABASE_SCHEMA,
                charset=settings.DATABASE_CHARSET,
                autocommit=True,
                minsize=1,
                maxsize=5,
            )
            adapter = MySqlAdapter(self._pool)
            repo = JdbcRepository(adapter, TsIDGenerator())
            ext_repo = JdbcProcessExtRepository(adapter, TsIDGenerator())
            user_provider = FlzkUserProvider()
            org_provider = FlzkOrgUserProvider()
            registry = HandlerRegistry()
            register_builtin_assignments(registry, user_provider, org_provider)
            engine = EngineImpl(
                repo,
                user_provider,
                TsIDGenerator(),
                FlzkExpressionEvaluator(),
            )
            engine.set_extensions(EngineExtensions(registry=registry))
            self.facade = JeeflowFacade(
                engine,
                repo,
                ext_repo,
                user_search=search_users,
                org_prov=org_provider,
            )

    async def stop(self) -> None:
        async with self._lock:
            facade = self.facade
            pool = self._pool
            self.facade = None
            self._pool = None
            if pool is not None:
                pool.close()
                await pool.wait_closed()
            del facade

    async def flow(self, action: str, body: dict[str, Any]) -> dict[str, Any]:
        if self.facade is None:
            await self.start()
        if self.facade is None:
            raise RuntimeError('jeeflow runtime is not initialized')
        return await self.facade.flow(action, body)


_runtime = JeeflowRuntime()


def get_runtime() -> JeeflowRuntime:
    return _runtime
