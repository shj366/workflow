-- jeeflow workflow schema for the Flzk MySQL database.
-- The existing wf_* tables are intentionally recreated by deployment; no data migration is provided.

DROP TABLE IF EXISTS wf_process_design_his;
DROP TABLE IF EXISTS wf_process_surrogate;
DROP TABLE IF EXISTS wf_process_cc_instance;
DROP TABLE IF EXISTS wf_process_task_actor;
DROP TABLE IF EXISTS wf_process_task;
DROP TABLE IF EXISTS wf_process_instance;
DROP TABLE IF EXISTS wf_process_define;
DROP TABLE IF EXISTS wf_process_design;

CREATE TABLE wf_process_define (
  id BIGINT NOT NULL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  display_name VARCHAR(128) NULL,
  type VARCHAR(64) NULL,
  state INT NOT NULL DEFAULT 1,
  content LONGTEXT NULL,
  version INT NOT NULL DEFAULT 0,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  UNIQUE KEY uk_wf_process_define_name_version (name, version),
  KEY idx_wf_process_define_name (name),
  KEY idx_wf_process_define_state (state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_instance (
  id BIGINT NOT NULL PRIMARY KEY,
  parent_id BIGINT NULL,
  process_define_id BIGINT NOT NULL,
  state INT NOT NULL DEFAULT 10,
  parent_node_name VARCHAR(128) NULL,
  business_no VARCHAR(128) NULL,
  operator VARCHAR(64) NULL,
  expire_time DATETIME(6) NULL,
  variable LONGTEXT NULL,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  KEY idx_wf_process_instance_define (process_define_id),
  KEY idx_wf_process_instance_operator (operator),
  KEY idx_wf_process_instance_state (state),
  CONSTRAINT fk_wf_process_instance_define FOREIGN KEY (process_define_id) REFERENCES wf_process_define (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_task (
  id BIGINT NOT NULL PRIMARY KEY,
  process_instance_id BIGINT NOT NULL,
  task_name VARCHAR(128) NOT NULL,
  display_name VARCHAR(128) NULL,
  task_type INT NOT NULL DEFAULT 0,
  perform_type INT NOT NULL DEFAULT 0,
  task_state INT NOT NULL DEFAULT 10,
  operator VARCHAR(64) NULL,
  finish_time DATETIME(6) NULL,
  expire_time DATETIME(6) NULL,
  form_key VARCHAR(128) NULL,
  task_parent_id BIGINT NULL,
  variable LONGTEXT NULL,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  KEY idx_wf_process_task_instance (process_instance_id),
  KEY idx_wf_process_task_state (task_state),
  KEY idx_wf_process_task_operator (operator),
  CONSTRAINT fk_wf_process_task_instance FOREIGN KEY (process_instance_id) REFERENCES wf_process_instance (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_task_actor (
  id BIGINT NOT NULL PRIMARY KEY,
  process_task_id BIGINT NOT NULL,
  actor_id VARCHAR(64) NOT NULL,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  KEY idx_wf_process_task_actor_task (process_task_id),
  KEY idx_wf_process_task_actor_actor (actor_id),
  UNIQUE KEY uk_wf_process_task_actor (process_task_id, actor_id),
  CONSTRAINT fk_wf_process_task_actor_task FOREIGN KEY (process_task_id) REFERENCES wf_process_task (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_cc_instance (
  id BIGINT NOT NULL PRIMARY KEY,
  process_instance_id BIGINT NOT NULL,
  actor_id VARCHAR(64) NOT NULL,
  state INT NOT NULL DEFAULT 0,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  KEY idx_wf_process_cc_instance_instance (process_instance_id),
  KEY idx_wf_process_cc_instance_actor (actor_id),
  CONSTRAINT fk_wf_process_cc_instance_instance FOREIGN KEY (process_instance_id) REFERENCES wf_process_instance (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_design (
  id BIGINT NOT NULL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  display_name VARCHAR(128) NULL,
  type VARCHAR(64) NULL,
  icon VARCHAR(128) NULL,
  is_deployed INT NOT NULL DEFAULT 0,
  remark VARCHAR(255) NULL,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  KEY idx_wf_process_design_name (name),
  KEY idx_wf_process_design_deployed (is_deployed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_design_his (
  id BIGINT NOT NULL PRIMARY KEY,
  process_design_id BIGINT NOT NULL,
  content LONGTEXT NOT NULL,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  KEY idx_wf_process_design_his_design (process_design_id),
  CONSTRAINT fk_wf_process_design_his_design FOREIGN KEY (process_design_id) REFERENCES wf_process_design (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wf_process_surrogate (
  id BIGINT NOT NULL PRIMARY KEY,
  process_name VARCHAR(128) NULL,
  operator VARCHAR(64) NOT NULL,
  surrogate VARCHAR(64) NOT NULL,
  start_time DATETIME(6) NULL,
  end_time DATETIME(6) NULL,
  enabled INT NOT NULL DEFAULT 1,
  create_time DATETIME(6) NOT NULL,
  create_user VARCHAR(64) NULL,
  update_time DATETIME(6) NULL,
  update_user VARCHAR(64) NULL,
  KEY idx_wf_process_surrogate_operator (operator),
  KEY idx_wf_process_surrogate_surrogate (surrogate),
  KEY idx_wf_process_surrogate_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Re-running initialization must remove old workflow menu component paths first.
DELETE FROM sys_menu
WHERE name IN (
  'WorkflowCenter', 'WorkflowApply', 'WorkflowProcessDesign',
  'WorkflowProcessDefine', 'WorkflowTaskTodo', 'WorkflowTaskDone',
  'WorkflowInstanceMy', 'WorkflowInstanceCc', 'AddWorkflowProcessDesign',
  'EditWorkflowProcessDesign', 'DeleteWorkflowProcessDesign',
  'DeployWorkflowProcessDesign', 'AddWorkflowProcessDefine',
  'EditWorkflowProcessDefine', 'DeleteWorkflowProcessDefine',
  'StartWorkflowProcess', 'AddWorkflowApply', 'ViewWorkflowTodoTask',
  'ViewWorkflowDoneTask', 'CompleteWorkflowTask', 'RejectWorkflowTask',
  'RollbackWorkflowTask', 'JumpWorkflowTask', 'AddCandidateWorkflowTask',
  'SurrogateWorkflowTask', 'CcWorkflowTask', 'ViewWorkflowInstanceMy',
  'WithdrawWorkflowInstanceMy', 'ViewWorkflowInstanceCc',
  'ReadWorkflowInstanceCc'
);
DELETE FROM sys_menu WHERE name = 'Workflow';
-- 工作流模块菜单
insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values ('工作流', 'Workflow', '/workflow', 0, 'ant-design:apartment-outlined', 0, null, null, 1, 1, 1, '', null, null, now(), null);

set @workflow_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('工作中心', 'WorkflowCenter', '/workflow/center', 0, 'ant-design:appstore-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('发起申请', 'WorkflowApply', '/workflow/processInstance/applyList', 0, 'ant-design:form-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('流程设计', 'WorkflowProcessDesign', '/workflow/processDesign', 0, 'ant-design:cluster-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('流程定义', 'WorkflowProcessDefine', '/workflow/processDefine', 0, 'ant-design:setting-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('待办任务', 'WorkflowTaskTodo', '/workflow/processTask/todo', 0, 'ant-design:profile-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('已办任务', 'WorkflowTaskDone', '/workflow/processTask/done', 0, 'ant-design:check-circle-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('我的流程', 'WorkflowInstanceMy', '/workflow/processInstance/my', 0, 'ant-design:user-switch-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null),
('抄送给我', 'WorkflowInstanceCc', '/workflow/processInstance/cc', 0, 'ant-design:mail-outlined', 1, '/plugins/workflow/views/jeeflowCenter/index', null, 1, 1, 1, '', null, @workflow_menu_id, now(), null);

set @workflow_center_id = (select id from sys_menu where name = 'WorkflowCenter' and parent_id = @workflow_menu_id);
set @workflow_apply_id = (select id from sys_menu where name = 'WorkflowApply' and parent_id = @workflow_menu_id);
set @process_design_id = (select id from sys_menu where name = 'WorkflowProcessDesign' and parent_id = @workflow_menu_id);
set @process_define_id = (select id from sys_menu where name = 'WorkflowProcessDefine' and parent_id = @workflow_menu_id);

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增流程设计', 'AddWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:add', 1, 0, 1, '', null, @process_design_id, now(), null),
('修改流程设计', 'EditWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:edit', 1, 0, 1, '', null, @process_design_id, now(), null),
('删除流程设计', 'DeleteWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:del', 1, 0, 1, '', null, @process_design_id, now(), null),
('部署流程设计', 'DeployWorkflowProcessDesign', null, 0, null, 2, null, 'workflow:process-design:deploy', 1, 0, 1, '', null, @process_design_id, now(), null),
('新增申请', 'AddWorkflowApply', null, 0, null, 2, null, 'workflow:apply:add', 1, 0, 1, '', null, @workflow_apply_id, now(), null),
('查看待办任务', 'ViewWorkflowTodoTask', null, 0, null, 2, null, 'workflow:task:todo:view', 1, 0, 1, '', null, @workflow_center_id, now(), null),
('查看已办任务', 'ViewWorkflowDoneTask', null, 0, null, 2, null, 'workflow:task:done:view', 1, 0, 1, '', null, @workflow_center_id, now(), null),
('完成任务', 'CompleteWorkflowTask', null, 0, null, 2, null, 'workflow:task:complete', 1, 0, 1, '', null, @workflow_center_id, now(), null),
('撤回我的流程', 'WithdrawWorkflowInstanceMy', null, 0, null, 2, null, 'workflow:instance:my:withdraw', 1, 0, 1, '', null, @workflow_center_id, now(), null),
('查看抄送', 'ViewWorkflowInstanceCc', null, 0, null, 2, null, 'workflow:instance:cc:view', 1, 0, 1, '', null, @workflow_center_id, now(), null);
