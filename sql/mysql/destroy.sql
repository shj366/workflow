delete from sys_menu
where name in (
    'WorkflowCenter',
    'WorkflowApply',
    'WorkflowProcessDesign',
    'AddWorkflowProcessDesign',
    'EditWorkflowProcessDesign',
    'DeleteWorkflowProcessDesign',
    'DeployWorkflowProcessDesign',
    'WorkflowProcessDefine',
    'AddWorkflowProcessDefine',
    'EditWorkflowProcessDefine',
    'DeleteWorkflowProcessDefine',
    'StartWorkflowProcess',
    'AddWorkflowApply',
    'WorkflowTaskTodo',
    'ViewWorkflowTodoTask',
    'CompleteWorkflowTask',
    'RejectWorkflowTask',
    'RollbackWorkflowTask',
    'JumpWorkflowTask',
    'AddCandidateWorkflowTask',
    'SurrogateWorkflowTask',
    'CcWorkflowTask',
    'WorkflowTaskDone',
    'ViewWorkflowDoneTask',
    'WorkflowInstanceMy',
    'ViewWorkflowInstanceMy',
    'WithdrawWorkflowInstanceMy',
    'WorkflowInstanceCc',
    'ViewWorkflowInstanceCc',
    'ReadWorkflowInstanceCc'
);

delete from sys_menu where name = 'Workflow';

-- 删除工作流相关表
drop table if exists wf_task_cc;
drop table if exists wf_task_candidate;
drop table if exists wf_task;
drop table if exists wf_process_instance;
drop table if exists wf_process_define;
drop table if exists wf_process_design;