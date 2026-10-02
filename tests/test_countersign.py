import asyncio
import json
from types import SimpleNamespace

from backend.plugin.wf.service.process_task import ProcessTaskService


class _Result:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value


class _Session:
    def __init__(self, task, actor, pending):
        self._results = iter([_Result(task), _Result(actor)])
        self._pending = pending

    async def execute(self, _statement):
        return next(self._results)

    async def scalar(self, _statement):
        return self._pending

    def add(self, _value):
        pass

    async def flush(self):
        pass

    async def refresh(self, _value):
        pass


def test_countersign_waits_for_every_actor_before_flow_continues():
    async def scenario():
        task = SimpleNamespace(
            id=1,
            process_instance_id=10,
            created_by=1,
            perform_type=1,
            task_state=10,
            variable=None,
            operator='alice',
        )

        first_actor = SimpleNamespace(completed=False)
        first_result = await ProcessTaskService.complete(
            _Session(task, first_actor, SimpleNamespace(id=2)),
            task_id=1,
            operator='alice',
            args={'approvalComment': '同意'},
            require_all=True,
        )
        assert first_result.task_state == 10
        assert first_actor.completed is True
        assert json.loads(first_result.variable)['countersignApprovals'][0]['operator'] == 'alice'

        second_actor = SimpleNamespace(completed=False)
        final_result = await ProcessTaskService.complete(
            _Session(task, second_actor, None),
            task_id=1,
            operator='bob',
            args={'approvalComment': '同意'},
            require_all=True,
        )
        assert final_result.task_state == 20
        assert final_result.operator == 'bob'

    asyncio.run(scenario())
