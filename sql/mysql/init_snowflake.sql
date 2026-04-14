-- 工作流模块菜单 (使用你现有的ID结构)
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values (208, '工作流', 'Workflow', '/workflow', 0, 'ant-design:apartment-outlined', 0, null, null, 1, 1, 1, '', null, null, '2026-02-27 14:40:00', null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values 
(209, '工作中心', 'WorkflowCenter', '/workflow/center', 0, 'ant-design:appstore-outlined', 1, '/plugins/workflow/views/workflowCenter/index', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(210, '发起申请', 'WorkflowApply', '/workflow/processInstance/applyList', 0, 'ant-design:form-outlined', 1, '/plugins/workflow/views/processInstance/applyList', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(211, '流程设计', 'WorkflowProcessDesign', '/workflow/processDesign', 0, 'ant-design:cluster-outlined', 1, '/plugins/workflow/views/processDesign/index', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(212, '流程定义', 'WorkflowProcessDefine', '/workflow/processDefine', 0, 'ant-design:setting-outlined', 1, '/plugins/workflow/views/processDefine/index', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(213, '待办任务', 'WorkflowTaskTodo', '/workflow/processTask/todo', 0, 'ant-design:profile-outlined', 1, '/plugins/workflow/views/processTask/todo', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(214, '已办任务', 'WorkflowTaskDone', '/workflow/processTask/done', 0, 'ant-design:check-circle-outlined', 1, '/plugins/workflow/views/processTask/done', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(215, '我的流程', 'WorkflowInstanceMy', '/workflow/processInstance/my', 0, 'ant-design:user-switch-outlined', 1, '/plugins/workflow/views/processInstance/my', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null),
(216, '抄送给我', 'WorkflowInstanceCc', '/workflow/processInstance/cc', 0, 'ant-design:mail-outlined', 1, '/plugins/workflow/views/processInstance/ccList', null, 1, 1, 1, '', null, 208, '2026-02-27 14:40:00', null);

-- 流程设计权限
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(217, '新增流程设计', 'AddWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:add', 1, 0, 1, '', null, 211, now(), null),
(218, '修改流程设计', 'EditWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:edit', 1, 0, 1, '', null, 211, now(), null),
(219, '删除流程设计', 'DeleteWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:del', 1, 0, 1, '', null, 211, now(), null),
(220, '部署流程设计', 'DeployWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:deploy', 1, 0, 1, '', null, 211, now(), null);

-- 流程定义权限
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(221, '新增流程定义', 'AddWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:add', 1, 0, 1, '', null, 212, now(), null),
(222, '修改流程定义', 'EditWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:edit', 1, 0, 1, '', null, 212, now(), null),
(223, '删除流程定义', 'DeleteWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:del', 1, 0, 1, '', null, 212, now(), null),
(224, '启动流程', 'StartWorkflowProcess', null, 0, null, 2, null, 'workflow:process:start', 1, 0, 1, '', null, 212, now(), null);

-- 发起申请权限
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(225, '新增申请', 'AddWorkflowApply', null, 0, null, 2, null, 'workflow:apply:add', 1, 0, 1, '', null, 210, now(), null);

-- 任务权限
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(226, '查看待办任务', 'ViewWorkflowTodoTask', null, 0, null, 2, null, 'workflow:task:todo:view', 1, 0, 1, '', null, 213, now(), null),
(227, '查看已办任务', 'ViewWorkflowDoneTask', null, 0, null, 2, null, 'workflow:task:done:view', 1, 0, 1, '', null, 214, now(), null),
(228, '完成任务', 'CompleteWorkflowTask', null, 0, null, 2, null, 'workflow:task:complete', 1, 0, 1, '', null, 213, now(), null),
(229, '驳回任务', 'RejectWorkflowTask', null, 0, null, 2, null, 'workflow:task:reject', 1, 0, 1, '', null, 213, now(), null),
(230, '退回任务', 'RollbackWorkflowTask', null, 0, null, 2, null, 'workflow:task:rollback', 1, 0, 1, '', null, 213, now(), null),
(231, '跳转节点', 'JumpWorkflowTask', null, 0, null, 2, null, 'workflow:task:jump', 1, 0, 1, '', null, 213, now(), null),
(232, '加签任务', 'AddCandidateWorkflowTask', null, 0, null, 2, null, 'workflow:task:add-candidate', 1, 0, 1, '', null, 213, now(), null),
(233, '委托任务', 'SurrogateWorkflowTask', null, 0, null, 2, null, 'workflow:task:surrogate', 1, 0, 1, '', null, 213, now(), null),
(234, '抄送任务', 'CcWorkflowTask', null, 0, null, 2, null, 'workflow:task:cc', 1, 0, 1, '', null, 213, now(), null);

-- 流程实例权限
insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(235, '查看我的流程', 'ViewWorkflowInstanceMy', null, 0, null, 2, null, 'workflow:instance:my:view', 1, 0, 1, '', null, 215, now(), null),
(236, '撤回我的流程', 'WithdrawWorkflowInstanceMy', null, 0, null, 2, null, 'workflow:instance:my:withdraw', 1, 0, 1, '', null, 215, now(), null),
(237, '查看抄送', 'ViewWorkflowInstanceCc', null, 0, null, 2, null, 'workflow:instance:cc:view', 1, 0, 1, '', null, 216, now(), null),
(238, '标记抄送已读', 'ReadWorkflowInstanceCc', null, 0, null, 2, null, 'workflow:instance:cc:read', 1, 0, 1, '', null, 216, now(), null);