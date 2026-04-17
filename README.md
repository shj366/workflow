# Workflow Plugin

为fastapi-best-architecture框架提供审批流相关能力的插件， 支持完整的流程定义管理、任务流转控制与实例状态维护功能。

## 📋 开源声明

本插件基于fastapi-best-architecture框架开发，审批流模块参考了开源项目的设计思路：

- **开发框架**：fastapi-best-architecture插件架构
- **参考来源**：mldong-python(Flask)开源项目的审批流模块设计

## ✨ 功能特性

### 核心功能
- **🔧 流程定义管理**：管理并持久化各版本的流程定义，支持版本隔离与热部署
- **🎯 任务流转控制**：实现业务逻辑与工作流状态的深度集成，支持审批、驳回、抄送、跳转等多种操作
- **📊 实例状态维护**：记录完整的流程审批链条与变量信息，提供实时且可回溯的流程轨迹
- **🔌 业务集成 API**：对外暴露标准的 REST API，便于各类业务系统发起流程与办理任务

### 扩展能力
- **🏗️ 高可用与可扩展**：基于轻量级引擎构建，支持自定义节点处理器、监听器与参与者转换器
- **🎨 可视化流程设计**：前端集成SnakerFlow设计器，支持拖拽式流程建模
- **📈 监控与统计**：提供流程执行效率分析和任务处理统计功能

## 🏗️ 架构设计

```
plugin/wf/
├── api/           # API路由层
├── core/          # 核心引擎
├── models/        # 数据模型
├── schemas/       # Pydantic模式
├── services/      # 业务逻辑层
└── utils/         # 工具函数
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来共同改进此插件。


## 插件预览
<img width="1689" height="948" alt="f544b3c5-5ab9-4b43-abb9-bb7258d804b9" src="https://github.com/user-attachments/assets/42635a69-ceb7-494b-a668-8ced106faef3" />
<img width="1912" height="948" alt="a925f88f-81b9-4a60-83ec-7576d21f0ec6" src="https://github.com/user-attachments/assets/032c1fb4-3f17-4208-8fa6-20612b9850c0" />
<img width="1688" height="948" alt="24b75875-20db-4a9f-a24a-6aa435a554bc" src="https://github.com/user-attachments/assets/035a6bc8-3530-41ec-8a8f-b8c3622c3298" />
