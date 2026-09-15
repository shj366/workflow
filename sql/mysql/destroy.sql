DELETE FROM sys_menu
WHERE name IN (
  'Workflow', 'WorkflowCenter', 'WorkflowApply', 'WorkflowProcessDesign',
  'WorkflowProcessDefine', 'WorkflowTaskTodo', 'WorkflowTaskDone',
  'WorkflowInstanceMy', 'WorkflowInstanceCc', 'AddWorkflowProcessDesign',
  'EditWorkflowProcessDesign', 'DeleteWorkflowProcessDesign',
  'DeployWorkflowProcessDesign', 'AddWorkflowApply', 'ViewWorkflowTodoTask',
  'ViewWorkflowDoneTask', 'CompleteWorkflowTask', 'WithdrawWorkflowInstanceMy',
  'ViewWorkflowInstanceCc'
);

DROP TABLE IF EXISTS wf_process_design_his;
DROP TABLE IF EXISTS wf_process_surrogate;
DROP TABLE IF EXISTS wf_process_cc_instance;
DROP TABLE IF EXISTS wf_process_task_actor;
DROP TABLE IF EXISTS wf_process_task;
DROP TABLE IF EXISTS wf_process_instance;
DROP TABLE IF EXISTS wf_process_define;
DROP TABLE IF EXISTS wf_process_design;
