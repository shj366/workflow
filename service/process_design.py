"""流程设计服务"""
import json
from typing import Any

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.pagination import paging_data
from backend.plugin.wf.model.process_design import ProcessDesign
from backend.plugin.wf.model.process_define import ProcessDefine
from backend.plugin.wf.schema.process_design import (
    ProcessDesignPageModel,
    ProcessDesignCreateModel,
    ProcessDesignUpdateModel,
    ProcessDesignModel,
)


class ProcessDesignService:
    """流程设计服务"""

    @classmethod
    async def get_page(
        cls,
        db: AsyncSession,
        query_object: ProcessDesignPageModel,
    ) -> dict[str, Any]:
        """分页查询流程设计"""

        filters = []

        if query_object.name:
            filters.append(ProcessDesign.name.like(f"%{query_object.name}%"))
        if query_object.display_name:
            filters.append(ProcessDesign.display_name.like(f"%{query_object.display_name}%"))
        if query_object.type:
            filters.append(ProcessDesign.type == query_object.type)

        stmt = (
            select(ProcessDesign)
            .where(*filters)
            .order_by(desc(ProcessDesign.update_time))
        )

        page_data = await paging_data(db, stmt)
        if items := page_data.get('items'):
            page_data['items'] = [
                ProcessDesignModel.model_validate(item).model_dump(by_alias=True)
                for item in items
            ]
        return page_data

    @classmethod
    async def get_detail(cls, db: AsyncSession, design_id: int) -> dict[str, Any]:
        """获取流程设计详情"""
        stmt = select(ProcessDesign).where(ProcessDesign.id == design_id)
        result = await db.execute(stmt)
        design = result.scalar_one_or_none()

        if not design:
            raise ValueError("流程设计不存在")

        # 解析 JSON
        design_dict = ProcessDesignModel.model_validate(design).model_dump(by_alias=True)

        # 解析 json_object
        if design.json_object:
            try:
                design_dict["jsonObject"] = (
                    json.loads(design.json_object)
                    if isinstance(design.json_object, str)
                    else design.json_object
                )
            except json.JSONDecodeError:
                design_dict["jsonObject"] = None
        else:
            design_dict["jsonObject"] = None

        return design_dict

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        data: ProcessDesignCreateModel,
        user_id: int | None = None,
    ) -> ProcessDesign:
        """创建流程设计"""
        design = ProcessDesign(
            name=data.name,
            display_name=data.display_name,
            type=data.type,
            icon=data.icon,
            remark=data.remark,
            create_user=user_id,
            update_user=user_id,
        )
        db.add(design)
        await db.flush()
        await db.refresh(design)
        return design

    @classmethod
    async def update_design(
        cls,
        db: AsyncSession,
        design_id: int,
        data: ProcessDesignUpdateModel,
        user_id: int | None = None,
    ) -> bool:
        """更新流程设计基本信息"""
        update_data = {}
        if data.name:
            update_data["name"] = data.name
        if data.display_name:
            update_data["display_name"] = data.display_name
        if data.type is not None:
            update_data["type"] = data.type
        if data.icon:
            update_data["icon"] = data.icon
        if data.remark:
            update_data["remark"] = data.remark

        if not update_data:
            return True

        update_data["update_user"] = user_id

        await db.execute(
            update(ProcessDesign)
            .where(ProcessDesign.id == design_id)
            .values(**update_data)
        )
        await db.flush()
        return True

    @classmethod
    async def save_design_json(
        cls,
        db: AsyncSession,
        design_id: int,
        json_object: dict | None,
        user_id: int | None = None,
    ) -> bool:
        """保存流程设计JSON"""
        json_str = json.dumps(json_object, ensure_ascii=False) if json_object else None
        
        # 构建更新数据
        update_data = {
            "json_object": json_str,
            "is_deployed": 0,
            "update_user": user_id,
        }
        
        # 同步 jsonObject 中的 name/displayName/type 到表字段
        if json_object:
            if json_object.get("name"):
                update_data["name"] = json_object["name"]
            if json_object.get("displayName"):
                update_data["display_name"] = json_object["displayName"]
            # type 必须是有效整数，空字符串不更新
            if json_object.get("type") not in (None, "", ""):
                try:
                    update_data["type"] = int(json_object["type"])
                except (ValueError, TypeError):
                    pass  # 无效值不更新
        
        await db.execute(
            update(ProcessDesign)
            .where(ProcessDesign.id == design_id)
            .values(**update_data)
        )
        await db.flush()
        return True

    @classmethod
    async def delete_designs(cls, db: AsyncSession, ids: list[int]) -> bool:
        """删除流程设计（软删除）"""
        await db.execute(
            update(ProcessDesign).where(ProcessDesign.id.in_(ids)).values(is_deleted=1)
        )
        await db.flush()
        return True

    @classmethod
    async def deploy(
        cls, db: AsyncSession, design_id: int, user_id: int | None = None
    ) -> ProcessDefine:
        """部署流程设计到流程定义"""
        # 获取流程设计
        stmt = select(ProcessDesign).where(ProcessDesign.id == design_id)
        result = await db.execute(stmt)
        design = result.scalar_one_or_none()

        if not design:
            raise ValueError("流程设计不存在")

        if not design.json_object:
            raise ValueError("流程设计JSON为空，无法部署")

        # 解析JSON
        try:
            json_obj = (
                json.loads(design.json_object)
                if isinstance(design.json_object, str)
                else design.json_object
            )
        except json.JSONDecodeError:
            raise ValueError("流程设计JSON格式错误")

        # 查询是否已有同名流程定义
        stmt = (
            select(ProcessDefine)
            .where(ProcessDefine.name == design.name)
            .order_by(desc(ProcessDefine.version))
            .limit(1)
        )
        result = await db.execute(stmt)
        existing = result.first()

        # 确定版本号
        version = (existing[0].version + 1) if existing else 1

        # 创建流程定义
        define = ProcessDefine(
            id=None,
            name=design.name,
            display_name=design.display_name,
            type=design.type,
            state=1,
            version=version,
            content=design.json_object.encode()
            if isinstance(design.json_object, str)
            else json.dumps(design.json_object).encode(),
            created_by=user_id or 0,
        )
        define.updated_by = user_id
        db.add(define)

        # 标记设计为已部署
        await db.execute(
            update(ProcessDesign)
            .where(ProcessDesign.id == design_id)
            .values(is_deployed=1, update_user=user_id)
        )

        await db.flush()
        await db.refresh(define)
        return define

    @classmethod
    async def redeploy(
        cls, db: AsyncSession, design_id: int, user_id: int | None = None
    ) -> ProcessDefine:
        """重新部署流程设计（覆盖最新版本）"""
        # 获取流程设计
        stmt = select(ProcessDesign).where(ProcessDesign.id == design_id)
        result = await db.execute(stmt)
        design = result.scalar_one_or_none()

        if not design:
            raise ValueError("流程设计不存在")

        if not design.json_object:
            raise ValueError("流程设计JSON为空，无法部署")

        # 查找最新版本的流程定义
        stmt = (
            select(ProcessDefine)
            .where(ProcessDefine.name == design.name)
            .order_by(desc(ProcessDefine.version))
            .limit(1)
        )
        result = await db.execute(stmt)
        latest_define = result.scalars().first()

        if not latest_define:
            # 如果不存在，则执行普通部署
            return await cls.deploy(db, design_id, user_id)

        # 更新最新版本的流程定义
        await db.execute(
            update(ProcessDefine)
            .where(ProcessDefine.id == latest_define.id)
            .values(
                display_name=design.display_name,
                type=design.type,
                content=design.json_object.encode() if isinstance(design.json_object, str) else json.dumps(design.json_object).encode(),
                updated_by=user_id,
            )
        )

        # 标记设计为已部署
        await db.execute(
            update(ProcessDesign)
            .where(ProcessDesign.id == design_id)
            .values(is_deployed=1, update_user=user_id)
        )

        await db.flush()
        await db.refresh(latest_define)
        return latest_define

    @classmethod
    async def list_by_type(cls, db: AsyncSession) -> list:
        """
        按类型获取已部署的流程设计列表
        用于发起申请页面，只返回已部署且启用的流程
        """
        from backend.plugin.wf.model.process_define import ProcessDefine
        
        # 查询所有已部署的流程设计（is_deployed=1 表示已部署）
        stmt = (
            select(ProcessDesign)
            .where(ProcessDesign.is_deployed == 1, ProcessDesign.is_deleted == 0)
            .order_by(ProcessDesign.type, ProcessDesign.id)
        )
        result = await db.execute(stmt)
        designs = result.scalars().all()
        
        print(f"[DEBUG] Found {len(designs)} deployed designs")
        
        # 按类型分组
        type_map = {}
        for design in designs:
            type_key = design.type or 0
            if type_key not in type_map:
                type_map[type_key] = {
                    "type": type_key,
                    "title": f"类型{type_key}" if type_key else "默认分类",
                    "items": []
                }
            
            # 查询对应的最新启用的流程定义
            define_stmt = (
                select(ProcessDefine)
                .where(ProcessDefine.name == design.name, ProcessDefine.state == 1)
                .order_by(desc(ProcessDefine.version))
                .limit(1)
            )
            define_result = await db.execute(define_stmt)
            define = define_result.scalars().first()
            
            print(f"[DEBUG] Design {design.name}: define found = {define is not None}")
            
            if define:
                type_map[type_key]["items"].append({
                    "id": design.id,
                    "name": design.name,
                    "displayName": design.display_name,
                    "icon": design.icon or "mdi:file-document-outline",
                    "type": design.type,
                    "processDefineId": define.id,
                })
        
        return list(type_map.values())

    @classmethod
    async def get_user_tree(cls, db: AsyncSession) -> list:
        """
        获取部门用户树
        """
        from backend.app.admin.model.dept import Dept
        from backend.app.admin.model.user import User
        
        # 1. 查询所有部门
        dept_stmt = select(Dept).where(Dept.status == 1, Dept.del_flag == 0).order_by(Dept.sort)
        dept_result = await db.execute(dept_stmt)
        depts = dept_result.scalars().all()
        
        # 2. 查询所有用户
        user_stmt = select(User).where(User.status == 1)
        user_result = await db.execute(user_stmt)
        users = user_result.scalars().all()
        
        # 3. 构建部门 Map
        dept_map = {}
        root_depts = []
        
        for dept in depts:
            dept_node = {
                "value": str(dept.id),
                "label": dept.name,
                "nodeType": "1",
                "disabled": True, # 部门不可选作为用户
                "ext": {},
                "children": []
            }
            dept_map[dept.id] = dept_node
            
        # 4. 将用户添加到部门
        for user in users:
            if user.dept_id and user.dept_id in dept_map:
                user_node = {
                    "value": user.username, 
                    "label": user.nickname or user.username,
                    "nodeType": "2",
                    "disabled": False,
                    "ext": {}
                }
                dept_map[user.dept_id]["children"].append(user_node)
            else:
                # 无部门用户，或者部门被禁用的用户，暂时忽略或放到“未分配”
                pass
                
        # 5. 构建树结构
        for dept in depts:
            node = dept_map[dept.id]
            if dept.parent_id and dept.parent_id in dept_map:
                dept_map[dept.parent_id]["children"].append(node)
            else:
                root_depts.append(node)
                
        return root_depts
