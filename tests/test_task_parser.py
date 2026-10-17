from backend.plugin.wf.engine.parser.impl.task_parser import TaskParser


def test_task_parser_reads_candidate_fields_from_extension_field():
    parser = TaskParser()
    parser.parse(
        {
            "id": "task-1",
            "text": {"value": "审批"},
            "properties": {
                "field": {
                    "candidateUsers": "alice,bob",
                    "candidateGroups": "finance",
                }
            },
        },
        [],
    )

    model = parser.get_model()
    assert model.candidateUsers == "alice,bob"
    assert model.candidateGroups == "finance"


def test_task_parser_prefers_top_level_candidate_fields():
    parser = TaskParser()
    parser.parse(
        {
            "id": "task-1",
            "properties": {
                "candidateUsers": "top-level",
                "field": {"candidateUsers": "fallback"},
            },
        },
        [],
    )

    assert parser.get_model().candidateUsers == "top-level"
