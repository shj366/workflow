# Workflow Plugin

Flzk workflow UI and API are now backed by the upstream `jeeflow-python` engine and `jeeflow-ui` facade contract.

## Runtime contract

- HTTP entrypoint: `POST /api/v1/wf/{action}`
- Engine source: `vendor/jeeflow_python/jeeflow` (synced from the upstream repository)
- Current operator: injected from the authenticated Flzk JWT user
- Persistence: `wf_*` tables initialized by `sql/mysql/init.sql` or `init_snowflake.sql`

The engine source is vendored under `vendor/jeeflow_python`; update it with the `jeeflow-python` git remote and subtree sync instead of installing a second top-level package.

## Frontend

The frontend plugin consumes the upstream `@mldong/jeeflow-ui` source synced under `vendor/jeeflow-ui`. Its process designer is patched to use `mldong-flow-designer-plus` 3.1.x so the same LogicFlow/Snaker JSON is used for design, preview, and runtime.

The frontend host adapters map user, role, token, operator, and permission data to Flzk APIs. Dictionary and upload adapters remain intentionally absent until a concrete Flzk dictionary/file contract is selected.
