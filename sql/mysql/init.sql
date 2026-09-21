-- Legacy workflow initialization.
-- Workflow tables are created from backend/plugin/wf/model by FBA metadata.create_all.
-- This script only registers the menu tree for access-mode routing.

INSERT INTO sys_menu
(title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '工作流', 'Workflow', '/workflow', 90, 'ant-design:deployment-unit-outlined', 0, NULL, NULL, 1, 1, 1, '', NULL, NULL, NOW(), NULL
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE name = 'Workflow' AND deleted = 0);

SET @workflow_menu_id = (SELECT id FROM sys_menu WHERE name = 'Workflow' AND deleted = 0 LIMIT 1);

INSERT INTO sys_menu
(title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT v.title, v.name, v.path, v.sort, v.icon, 1, v.component, NULL, 1, 1, 1, '', NULL, @workflow_menu_id, NOW(), NULL
FROM (
  SELECT '工作中心' AS title, 'WorkflowCenter' AS name, '/workflow/center' AS path, 1 AS sort, 'ant-design:appstore-outlined' AS icon, '/plugins/workflow/views/workflowCenter/index' AS component
  UNION ALL SELECT '发起申请', 'WorkflowApply', '/workflow/processInstance/applyList', 2, 'ant-design:form-outlined', '/plugins/workflow/views/processInstance/applyList'
  UNION ALL SELECT '流程设计', 'WorkflowProcessDesign', '/workflow/processDesign', 3, 'ant-design:cluster-outlined', '/plugins/workflow/views/processDesign/index'
  UNION ALL SELECT '流程定义', 'WorkflowProcessDefine', '/workflow/processDefine', 4, 'ant-design:setting-outlined', '/plugins/workflow/views/processDefine/index'
) AS v
WHERE NOT EXISTS (SELECT 1 FROM sys_menu m WHERE m.name = v.name AND m.deleted = 0);
