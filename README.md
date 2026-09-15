# Workflow Plugin

Flzk workflow UI and API are now backed by the upstream `jeeflow-python` engine and `jeeflow-ui` facade contract.

## Runtime contract

- HTTP entrypoint: `POST /api/v1/wf/{action}`
- Facade response: `{ code: 0, msg, data }`
- Current operator: injected from the authenticated Flzk JWT user
- Persistence: `wf_*` tables initialized by `sql/mysql/init.sql` or `init_snowflake.sql`
- Engine dependency: locked to the upstream `jeeflow-python` Git revision in `flzk_backend/uv.lock`

The previous FBA workflow engine implementation was removed from the active plugin surface. The pre-switch implementation is preserved in the repository backup directory created for this replacement and in the `backup/workflow-before-jeeflow` refs.

## Frontend

The frontend plugin consumes the upstream `@mldong/jeeflow-ui` source synced under `vendor/jeeflow-ui`. Its process designer is patched to use `mldong-flow-designer-plus` 3.1.x so the same LogicFlow/Snaker JSON is used for design, preview, and runtime.

The frontend host adapters map user, role, token, operator, and permission data to Flzk APIs. Dictionary and upload adapters remain intentionally absent until a concrete Flzk dictionary/file contract is selected.
