import json
from typing import Any, List

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import paging_data
from backend.plugin.wf.engine.parser.model_parser import ModelParser
from backend.plugin.wf.model.process_define import ProcessDefine
from backend.plugin.wf.schema.process_define import ProcessDefinePageModel, ProcessDefineModel


class ProcessDefineService:
    """流程定义服务"""

    @classmethod
    async def get_process_define_list(
        cls,
        db: AsyncSession,
        query_object: ProcessDefinePageModel,
    ) -> dict[str, Any]:
        """分页查询流程定义"""

        filters = []

        if query_object.name:
            filters.append(ProcessDefine.name.like(f"%{query_object.name}%"))
        if query_object.display_name:
            filters.append(ProcessDefine.display_name.like(f"%{query_object.display_name}%"))
        if query_object.type:
            filters.append(ProcessDefine.type == query_object.type)
        if query_object.state is not None:
            filters.append(ProcessDefine.state == query_object.state)

        stmt = (
            select(ProcessDefine)
            .where(*filters)
            .order_by(desc(ProcessDefine.created_time))
        )

        page_data = await paging_data(db, stmt)
        # 转换成驼峰格式
        if items := page_data.get('items'):
            page_data['items'] = [
                ProcessDefineModel.model_validate(item).model_dump(by_alias=True)
                for item in items
            ]
        return page_data

    @classmethod
    async def deploy(
        cls,
        db: AsyncSession,
        content: bytes,
        user_id: int,
    ) -> ProcessDefine:
        """部署流程定义"""
        
        # 1. 解析流程模型
        process_model = ModelParser.parse(content)
        
        # 2. 查询最新版本
        stmt = (
            select(ProcessDefine)
            .where(ProcessDefine.name == process_model.name)
            .order_by(desc(ProcessDefine.version))
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_define = result.scalars().first()
        
        new_version = 1
        if latest_define:
            new_version = (latest_define.version or 0) + 1
            
        # 3. 创建新版本定义
        new_define = ProcessDefine(
            name=process_model.name,
            display_name=process_model.displayName,
            type=process_model.type,
            state=1,
            content=content,
            version=new_version,
            created_by=user_id,
        )
        new_define.updated_by = user_id
        
        db.add(new_define)
        await db.flush()
        await db.refresh(new_define)
        
        return new_define

    @classmethod
    async def get_detail(cls, db: AsyncSession, id: int) -> dict[str, Any]:
        """获取流程定义详情（包含JSON内容）"""
        stmt = select(ProcessDefine).where(ProcessDefine.id == id)
        result = await db.execute(stmt)
        define = result.scalars().first()
        if not define:
            raise ValueError(f"流程定义[{id}]不存在")
            
        res = {
            "id": define.id,
            "name": define.name,
            "displayName": define.display_name,
            "type": define.type,
            "version": define.version,
            "jsonObject": json.loads(define.content.decode('utf-8')) if define.content else {}
        }
        return res

    @classmethod
    async def save_design(cls, db: AsyncSession, id: int, json_data: dict, user_id: int) -> ProcessDefine:
        """保存流程设计（更新现有记录或创建新版本）"""
        # 这里简化逻辑：如果是设计模式，通常是更新当前未发布的草稿，或者每次保存都算新版本？
        # mldong 的逻辑是 updateDefine，如果 id 存在则更新。
        # 为了兼容 mldong 的习惯，我们允许更新指定 ID 的定义，或者如果 ID 不存在则创建。
        # 但通常版本控制下，已发布的版本不应修改。
        # 这里我们要么创建一个新版本，要么更新当前 ID（如果它还没被使用）。
        # 简单起见，我们复用 deploy 的逻辑，每次保存都生成新版本，或者更新指定 ID 的 content。
        
        # 我们采用更新指定 ID 的逻辑，因为设计器通常是针对某个记录操作。
        stmt = select(ProcessDefine).where(ProcessDefine.id == id)
        result = await db.execute(stmt)
        define = result.scalars().first()
        
        content_bytes = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
        process_model = ModelParser.parse(content_bytes)
        
        if define:
            define.content = content_bytes
            define.name = process_model.name
            define.display_name = process_model.displayName
            define.type = process_model.type
            define.updated_by = user_id
            # define.version 保持不变
        else:
            # 如果没有 ID，这其实是新建
            raise ValueError("保存设计需要指定ID，新建请使用部署或创建接口")
            
        await db.flush()
        await db.refresh(define)
        return define

    @classmethod
    async def up_and_down(cls, db: AsyncSession, ids: List[int], op_type: int, user_id: int) -> int:
        """
        启用/禁用流程定义
        :param ids: 流程定义ID列表
        :param op_type: 操作类型 1=启用 0=禁用
        :param user_id: 操作用户ID
        :return: 影响行数
        """
        stmt = (
            update(ProcessDefine)
            .where(ProcessDefine.id.in_(ids))
            .values(state=op_type, updated_by=user_id)
        )
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount
