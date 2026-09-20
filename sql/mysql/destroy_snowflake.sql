DELETE FROM sys_menu
WHERE name IN (
  'WorkflowCenter', 'WorkflowApply', 'WorkflowProcessDesign',
  'WorkflowProcessDefine', 'WorkflowTaskTodo', 'WorkflowTaskDone',
  'WorkflowInstanceMy', 'WorkflowInstanceCc', 'WorkflowSurrogate', 'AddWorkflowProcessDesign',
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

DROP TABLE IF EXISTS wf_process_design_his;
DROP TABLE IF EXISTS wf_process_surrogate;
DROP TABLE IF EXISTS wf_process_cc_instance;
DROP TABLE IF EXISTS wf_process_task_actor;
DROP TABLE IF EXISTS wf_process_task;
DROP TABLE IF EXISTS wf_process_instance;
DROP TABLE IF EXISTS wf_process_define;
DROP TABLE IF EXISTS wf_process_design;
