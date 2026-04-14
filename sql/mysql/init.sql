-- 工作流模块菜单
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values ('工作流', 'Workflow', '/workflow', 0, 'ant-design:apartment-outlined', 0, null, null, 1, 1, 1, '', null, null, now(), null);

set @workflow_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values 
('工作中心', 'WorkflowCenter', '/workflow/center', 0, 'ant-design:appstore-outlined', 1, '/plugins/workflow/views/workflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('发起申请', 'WorkflowApply', '/workflow/processInstance/applyList', 0, 'ant-design:form-outlined', 1, '/plugins/workflow/views/processInstance/applyList', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('流程设计', 'WorkflowProcessDesign', '/workflow/processDesign', 0, 'ant-design:cluster-outlined', 1, '/plugins/workflow/views/processDesign/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('流程定义', 'WorkflowProcessDefine', '/workflow/processDefine', 0, 'ant-design:setting-outlined', 1, '/plugins/workflow/views/processDefine/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null);

-- 设置各个子菜单的ID变量
set @workflow_center_id = (select id from sys_menu where name = 'WorkflowCenter' and parent_id = @workflow_menu_id);
set @workflow_apply_id = (select id from sys_menu where name = 'WorkflowApply' and parent_id = @workflow_menu_id);
set @process_design_id = (select id from sys_menu where name = 'WorkflowProcessDesign' and parent_id = @workflow_menu_id);
set @process_define_id = (select id from sys_menu where name = 'WorkflowProcessDefine' and parent_id = @workflow_menu_id);
set @task_todo_id = (select id from sys_menu where name = 'WorkflowTaskTodo' and parent_id = @workflow_menu_id);
set @task_done_id = (select id from sys_menu where name = 'WorkflowTaskDone' and parent_id = @workflow_menu_id);
set @instance_my_id = (select id from sys_menu where name = 'WorkflowInstanceMy' and parent_id = @workflow_menu_id);
set @instance_cc_id = (select id from sys_menu where name = 'WorkflowInstanceCc' and parent_id = @workflow_menu_id);

-- 流程设计权限
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增流程设计', 'AddWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:add', 1, 0, 1, '', null, @process_design_id, now(), null),
('修改流程设计', 'EditWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:edit', 1, 0, 1, '', null, @process_design_id, now(), null),
('删除流程设计', 'DeleteWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:del', 1, 0, 1, '', null, @process_design_id, now(), null),
('部署流程设计', 'DeployWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:deploy', 1, 0, 1, '', null, @process_design_id, now(), null);

-- 流程定义权限
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增流程定义', 'AddWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:add', 1, 0, 1, '', null, @process_define_id, now(), null),
('修改流程定义', 'EditWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:edit', 1, 0, 1, '', null, @process_define_id, now(), null),
('删除流程定义', 'DeleteWorkflowProcessDefine', null, 0, null, 2, null, 'workflow:process-define:del', 1, 0, 1, '', null, @process_define_id, now(), null),
('启动流程', 'StartWorkflowProcess', null, 0, null, 2, null, 'workflow:process:start', 1, 0, 1, '', null, @process_define_id, now(), null);

-- 发起申请权限
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增申请', 'AddWorkflowApply', null, 0, null, 2, null, 'workflow:apply:add', 1, 0, 1, '', null, @workflow_apply_id, now(), null);

-- 任务权限
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('查看待办任务', 'ViewWorkflowTodoTask', null, 0, null, 2, null, 'workflow:task:todo:view', 1, 0, 1, '', null, @task_todo_id, now(), null),
('查看已办任务', 'ViewWorkflowDoneTask', null, 0, null, 2, null, 'workflow:task:done:view', 1, 0, 1, '', null, @task_done_id, now(), null),
('完成任务', 'CompleteWorkflowTask', null, 0, null, 2, null, 'workflow:task:complete', 1, 0, 1, '', null, @task_todo_id, now(), null),
('驳回任务', 'RejectWorkflowTask', null, 0, null, 2, null, 'workflow:task:reject', 1, 0, 1, '', null, @task_todo_id, now(), null),
('退回任务', 'RollbackWorkflowTask', null, 0, null, 2, null, 'workflow:task:rollback', 1, 0, 1, '', null, @task_todo_id, now(), null),
('跳转节点', 'JumpWorkflowTask', null, 0, null, 2, null, 'workflow:task:jump', 1, 0, 1, '', null, @task_todo_id, now(), null),
('加签任务', 'AddCandidateWorkflowTask', null, 0, null, 2, null, 'workflow:task:add-candidate', 1, 0, 1, '', null, @task_todo_id, now(), null),
('委托任务', 'SurrogateWorkflowTask', null, 0, null, 2, null, 'workflow:task:surrogate', 1, 0, 1, '', null, @task_todo_id, now(), null),
('抄送任务', 'CcWorkflowTask', null, 0, null, 2, null, 'workflow:task:cc', 1, 0, 1, '', null, @task_todo_id, now(), null);

-- 流程实例权限
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('查看我的流程', 'ViewWorkflowInstanceMy', null, 0, null, 2, null, 'workflow:instance:my:view', 1, 0, 1, '', null, @instance_my_id, now(), null),
('撤回我的流程', 'WithdrawWorkflowInstanceMy', null, 0, null, 2, null, 'workflow:instance:my:withdraw', 1, 0, 1, '', null, @instance_my_id, now(), null),
('查看抄送', 'ViewWorkflowInstanceCc', null, 0, null, 2, null, 'workflow:instance:cc:view', 1, 0, 1, '', null, @instance_cc_id, now(), null),
('标记抄送已读', 'ReadWorkflowInstanceCc', null, 0, null, 2, null, 'workflow:instance:cc:read', 1, 0, 1, '', null, @instance_cc_id, now(), null);