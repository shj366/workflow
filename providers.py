"""Flzk identity and expression adapters for jeeflow."""

from __future__ import annotations

import operator
import re
from typing import Any

from sqlalchemy import and_, func, or_, select

from backend.app.admin.model import Dept, Role, User, user_role
from backend.database.db import async_db_session

from jeeflow.model import UserInfo
from jeeflow.spi import ExpressionEvaluator, OrgUserProvider, UserProvider


class FlzkUserProvider(UserProvider):
    async def get_user(self, user_id: str) -> UserInfo | None:
        async with async_db_session() as db:
            user = await db.scalar(
                select(User).where(
                    User.status == 1,
                    User.deleted == 0,
                    or_(User.id == _as_int(user_id), User.username == str(user_id)),
                )
            )
            if user is None:
                return None
            dept_name = await db.scalar(select(Dept.name).where(Dept.id == user.dept_id)) if user.dept_id else None
            return UserInfo(
                userId=str(user.id),
                realName=user.nickname or user.username,
                deptId=str(user.dept_id) if user.dept_id else None,
                deptName=dept_name,
            )


class FlzkOrgUserProvider(OrgUserProvider):
    async def find_dept_leaders(self, dept_id: str) -> list[str]:
        return await _find_dept_leaders(dept_id)

    async def find_dept_main_leaders(self, dept_id: str) -> list[str]:
        # Flzk has one department leader field; use it for both jeeflow leader roles.
        return await _find_dept_leaders(dept_id)

    async def find_by_role(self, role_code: str) -> list[str]:
        async with async_db_session() as db:
            role_filter = [Role.status == 1, Role.deleted == 0]
            role_id = _as_int(role_code)
            if role_id is not None:
                role_filter.append(Role.id == role_id)
            else:
                role_filter.append(Role.name == role_code)
            rows = await db.scalars(
                select(User.id)
                .join(user_role, user_role.c.user_id == User.id)
                .join(Role, Role.id == user_role.c.role_id)
                .where(User.status == 1, User.deleted == 0, *role_filter)
            )
            return [str(user_id) for user_id in rows.all()]


async def _find_dept_leaders(dept_id: str) -> list[str]:
    dept_pk = _as_int(dept_id)
    if dept_pk is None:
        return []
    async with async_db_session() as db:
        leader = await db.scalar(select(Dept.leader).where(Dept.id == dept_pk, Dept.status == 1, Dept.deleted == 0))
        if not leader:
            return []
        rows = await db.scalars(
            select(User.id).where(
                User.status == 1,
                User.deleted == 0,
                or_(User.username == str(leader), User.id == _as_int(str(leader))),
            )
        )
        return [str(user_id) for user_id in rows.all()]


async def search_users(query: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    keywords = [str(value).strip() for key, value in query.items() if key.startswith('m_') and str(value).strip()]
    page_num = max(1, _as_int(query.get('pageNum')) or 1)
    page_size = max(1, min(200, _as_int(query.get('pageSize')) or 10))
    async with async_db_session() as db:
        filters = [User.status == 1, User.deleted == 0]
        for keyword in keywords:
            filters.append(or_(User.username.like(f'%{keyword}%'), User.nickname.like(f'%{keyword}%')))
        base = select(User.id, User.username, User.nickname, User.dept_id, Dept.name.label('dept_name')).outerjoin(
            Dept, Dept.id == User.dept_id
        ).where(*filters)
        total = int(await db.scalar(select(func.count()).select_from(base.subquery())) or 0)
        rows = (await db.execute(base.order_by(User.id).offset((page_num - 1) * page_size).limit(page_size))).all()
        return [
            {
                'userId': str(row.id),
                'realName': row.nickname or row.username,
                'deptId': str(row.dept_id) if row.dept_id else None,
                'deptName': row.dept_name,
            }
            for row in rows
        ], total


class FlzkExpressionEvaluator(ExpressionEvaluator):
    """Deliberately small evaluator matching the safe comparison subset used by flows."""

    _pattern = re.compile(r'^\s*([A-Za-z_][\w.]*)\s*(>=|<=|!=|==|>|<)\s*(.+?)\s*$')
    _operators = {
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
    }

    async def eval(self, expr: str, vars: dict[str, Any]) -> bool:
        match = self._pattern.match(expr)
        if match is None:
            return False
        key, symbol, expected_raw = match.groups()
        actual = vars.get(key)
        expected = expected_raw.strip().strip('"\'')
        if actual is None:
            return False
        try:
            if isinstance(actual, (int, float)):
                expected_value: Any = float(expected)
            else:
                expected_value = expected
            return bool(self._operators[symbol](actual, expected_value))
        except (TypeError, ValueError):
            return False


def _as_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None and str(value).strip() else None
    except (TypeError, ValueError):
        return None
