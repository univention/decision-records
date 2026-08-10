# ADR: Cerbos Python Client Transport — HTTP vs gRPC

* **Status:** Proposed — pending team decision
* **Date:** 2026-08-06
* **Decision owners:** [Team / owner]
* **Related components:** user-management-bff, `PermissionsPort` / `GuardianPermissionsAdapter`, Cerbos PDP

## Context

The user management module's Guardian integration must be adapted to talk to Cerbos-based Guardian
([user_management_bff/adapters/permissions.py](../../user-management-bff/user_management_bff/adapters/permissions.py)).
The `PermissionsPort` abstraction already isolates the domain from the concrete client, so this
decision is scoped to the transport used *inside* the adapter.

The official `cerbos` Python package offers two async clients:

```python
from cerbos.sdk.client import AsyncCerbosClient        # HTTP
from cerbos.sdk.grpc.client import AsyncCerbosClient   # gRPC
```

Both need to be evaluated against how this specific service is built and deployed, not just in the
abstract. Relevant repo facts:

- The current `GuardianPermissionsAdapter` already follows a "create once, reuse" pattern
  (`Config.cached = True`, lazily-built client property, one-time `configure()` at startup) — this
  fits either client equally well.
- Dev [docker-compose.yaml](../docker-compose.yaml) already exposes Cerbos on **both** port
  3592 (HTTP) and 3593 (gRPC).
- Production [compose.jinja](../../appcenter-management/compose.jinja) already points
  `GUARDIAN_PERMISSIONS_ADAPTER__GUARDIAN_URL` at Cerbos's **HTTP** port, via the customer-facing UCR
  variable `ucsschool-user-management/guardian/url`, over a plain external Docker network with no
  TLS/mTLS/service mesh.
- No `grpcio`/`protobuf`/`cerbos` dependency exists in `pyproject.toml`/`uv.lock` today; `httpx` is
  already the codebase's established HTTP client idiom.
- This module is a **UCS App Center app**, installed on-prem at individual customer sites (schools /
  school authorities), configured through UCR variables — not a Kubernetes/service-mesh environment.
  Site admins and support may need to debug connectivity directly against Cerbos.
- `tests/adapters/test_permissions.py` mocks the underlying client object directly rather than at the
  HTTP layer, so the existing test-mocking pattern carries over regardless of transport.

## Options considered

### Option A: Async HTTP client (`cerbos.sdk.client.AsyncCerbosClient`)

**Pros**

- No changes needed to the existing production wiring: `GUARDIAN_URL` already points at Cerbos's HTTP
  port (3592) via the `ucsschool-user-management/guardian/url` UCR variable.
- Request/response objects are plain Python (`cerbos.sdk.model.Principal`/`Resource`/`ResourceList`,
  built on `dataclasses_json`) rather than hand-built Protobuf messages — less boilerplate in the
  adapter than the gRPC client's `struct_pb2.Value` attribute wrapping (see effort estimate below).
- Easiest to debug/operate at customer sites: plain JSON over HTTP can be inspected with `curl`,
  browser tools, or standard HTTP logging — relevant given this is an on-prem, UCR-configured app
  without a service mesh or centralized observability layer.
- Matches the "create once, reuse" adapter pattern with no additional lifecycle complexity (an
  `httpx.AsyncClient` is a simple object to hold on `self._client`).
- Lower operational surface: no HTTP/2, TLS/ALPN, or channel-management concerns to introduce into an
  infrastructure that has never carried gRPC.

**Cons**

- Higher per-request overhead than gRPC (JSON serialization, no persistent multiplexed streams) —
  though this hasn't been shown to matter at this module's request volume.
- Diverges from the officially recommended default in Cerbos's own docs and from the originally
  drafted ADR, which favored gRPC for internal service-to-service calls.
- If a future internal service standard mandates gRPC across the stack, this module would be an
  outlier requiring a later migration.

### Option B: Async gRPC client (`cerbos.sdk.grpc.client.AsyncCerbosClient`)

**Pros**

- Persistent HTTP/2 connections and generated Protobuf types — lower per-call overhead and connection
  reuse, useful if authorization checks become a high-frequency, latency-sensitive path.
- The official Cerbos Python SDK itself recommends this as the default for new projects:
  > "There are two clients available; gRPC and HTTP. New projects should use the gRPC client."
  — [cerbos/cerbos-sdk-python](https://github.com/cerbos/cerbos-sdk-python)
- Generated types reduce hand-written request/response mapping code inside the adapter.

**Cons**

- Requires re-plumbing production config: `GUARDIAN_URL`/UCR variable and `compose.jinja` network
  setup currently target port 3592 (HTTP), not 3593 (gRPC) — a customer-facing config change with
  documentation and upgrade-path implications for existing on-prem installs.
- Adapter code must build Protobuf messages by hand (`engine_pb2.Principal`/`Resource`, attribute
  values wrapped as `google.protobuf.struct_pb2.Value`) and manage gRPC channel lifecycle/close() —
  no existing local pattern to lean on (see effort estimate below). Note: the `grpcio`/`protobuf`
  dependency itself is *not* unique to this option — see correction below.
- Harder to debug in the field: this is a self-hosted, UCS App Center product installed at individual
  customer sites; support staff and site admins lose the ability to `curl`/inspect requests directly
  against Cerbos.
- No measured latency pressure on this service today that would justify the added operational
  complexity — the module handles per-school/per-user permission checks, not a high-QPS hot path.
- Docker build is Debian-based with `build-essential`/`python3-dev` already present, so wheel
  installation isn't blocked — but it's still new surface to validate in CI/deployment.

## Estimated effort: adopting the gRPC client (Option B)

This section was produced by inspecting the actual `cerbos` PyPI package (v0.15.1) source rather than
relying on documentation alone — the wheel was downloaded and unpacked locally to confirm the exact
API and dependency graph.

### Correction: dependency footprint is shared between both options

`cerbos` on PyPI is a **single package** that ships both clients' generated code in one distribution.
Its core (non-extra) dependencies are:

```
dataclasses-json, requests-toolbelt, httpx[http2], anyio, tenacity,
grpcio-tools, grpcio-status, protobuf, googleapis-common-protos,
protoc-gen-openapiv2, circuitbreaker
```

`grpcio-tools`/`grpcio-status` (and therefore the `grpcio` runtime itself) are pulled in **regardless
of which client class you import** — even choosing the HTTP client (Option A) installs the same
`grpcio`/`protobuf` dependency tree. The earlier "no new binary dependency" / "introduces grpcio as a
new dependency" framing above has been corrected to reflect this: the dependency-footprint argument is
not a real differentiator between the two options. What *does* differ is which client's code path is
exercised at runtime (HTTP requests vs. gRPC channel/stub calls) and how much adapter code you write
by hand.

### Confirmed API shape (`cerbos.sdk.grpc.client.AsyncCerbosClient`)

```python
class AsyncCerbosClient(AsyncClientBase):
    def __init__(self, host: str, tls_verify: bool | str = False, playground_instance: str = "",
                 timeout_secs: float | None = None, request_retries: int = 0,
                 wait_for_ready: bool = False, channel_options: dict[str, Any] | None = None): ...

    async def check_resources(self, principal: engine_pb2.Principal,
                               resources: list[request_pb2.CheckResourcesRequest.ResourceEntry],
                               request_id: str | None = None,
                               aux_data: request_pb2.AuxData | None = None
                               ) -> response_pb2.CheckResourcesResponse: ...

    async def is_allowed(self, action: str, principal, resource, ...) -> bool: ...  # single-action convenience wrapper over check_resources
    async def server_info(self) -> response_pb2.ServerInfoResponse: ...
    async def close(self): ...  # closes the underlying grpc.aio.Channel
```

`check_resources` is the batch call — it maps directly onto the current adapter's existing
`get_permissions(actor, targets)` shape (one principal, many resources per call), so the call
pattern itself carries over cleanly.

Key Protobuf types (from `cerbos.engine.v1.engine_pb2` / `cerbos.request.v1.request_pb2` /
`cerbos.response.v1.response_pb2`):

- `Principal(id: str, roles: list[str], attr: dict[str, struct_pb2.Value], policy_version: str, scope: str)`
- `Resource(kind: str, id: str, attr: dict[str, struct_pb2.Value], policy_version: str, scope: str)`
- `CheckResourcesRequest.ResourceEntry(actions: list[str], resource: Resource)` — **the caller must
  list every action to check per resource up front**; Cerbos does not return "all permissions" the
  way `guardian_authz_client.get_permissions` does today.
- `CheckResourcesResponse.ResultEntry(resource: {id, kind, policy_version}, actions: dict[str, Effect])`
  — check each entry's `actions[name] == EFFECT_ALLOW` (helper: `cerbos.sdk.grpc.utils.is_allowed`).

### Required changes, by area

**1. `permissions.py` adapter (largest piece, ~1 day)**

- Swap `guardian_authz_client.*` imports for `cerbos.sdk.grpc.client.AsyncCerbosClient` +
  `engine_pb2`/`request_pb2`/`response_pb2`/`effect_pb2` + `google.protobuf.struct_pb2`.
- New settings: `cerbos_target: str` (bare `host:port`, e.g. `"cerbos:3593"` — **not** a URL string
  like today's `guardian_url`), `tls_verify: bool|str = False`, `timeout_secs: float`. Drop
  `client_id`/`client_secret`/`oauth2_well_known_url` entirely — Cerbos's gRPC API has no OAuth2
  client-credentials step, so `configure()` no longer calls `get_oauth2_settings()`.
- `client` property: unchanged "create once, cache on `self._client`" pattern — fits directly.
- **New**: nothing today closes the cached client/channel on shutdown (confirmed — `main.py`'s
  lifespan has no adapter teardown hook). For gRPC this means adding a small shutdown path that
  calls `await self._client.close()`; low risk (the OS reclaims the socket on process exit either
  way) but a new pattern for this codebase (~10–20 LOC in `main.py`/`adapter_registry.py`).
- Attribute mapping becomes Protobuf-shaped: build a `struct_pb2.Struct()`, call `.update(python_dict)`
  (handles nested dict/list/str/bool/number conversion), then pass `.fields` as `attr=` to
  `Principal(...)`/`Resource(...)`. Mechanical but more verbose than today's plain dict assignment.
- `get_permissions()` must now pass an explicit `actions=[...]` list (every known `Permission` value)
  per resource — a required behavior change, not just a rename, since Cerbos's `check_resources` only
  evaluates actions you ask about.
- Error handling: catch `grpc.aio.AioRpcError` (inspect `.code()`/`.details()`) and the SDK's
  `CerbosTypeError`, map to the existing `PermissionsError`. New pattern — no gRPC error handling
  exists anywhere in this codebase today.
- *Not* included in this estimate (identical cost under Option A too — this is the real bulk of the
  ticket): redesigning `ucsschool_roles_to_guardian_roles` and the old/new-target diffing away from
  Guardian's App/Namespace/Role/Context object model toward Cerbos's flat `roles: list[str]` +
  attribute-based model. [cerbos_resources.md](cerbos_resources.md) already documents an `R.attr.old`
  policy-side convention for old/new diffing, so the policy side is presumably ready; the adapter
  needs to nest old/new attributes accordingly (e.g. `attr={"old": {...}, "new": {...}}`).

**2. Settings/DI wiring (~0.5 day)**

- Rename adapter/settings classes (e.g. `CerbosPermissionsAdapter`), update `Config.alias` and the
  `port_loader` env var prefix (`GUARDIAN_PERMISSIONS_ADAPTER__*` → `CERBOS_PERMISSIONS_ADAPTER__*`).

**3. Infra/deployment (~0.5 day)**

- `appcenter-management/compose.jinja`: change the env var feeding the adapter from a URL
  (`http://cerbos:3592`) to a bare target (`cerbos:3593`) — a format change, not just a port swap —
  and remove the now-unused OAuth2 env vars (`CLIENT_ID`, `CLIENT_SECRET_FILE`,
  `OAUTH2_WELL_KNOWN_URL`) and the `keycloak_url` UCR lookup feeding them.
- Update the `ucsschool-user-management/guardian/url` UCR variable's documented semantics (URL → bare
  target) — a customer-facing change needing a migration note for existing on-prem installs that
  override it.
- Dev `docker-compose.yaml`: no change needed — port 3593 is already exposed.

**4. Tests (~0.5–1 day)**

- `tests/adapters/test_permissions.py`: today's fixtures mock `GuardianAuthzClient.get_permissions`'s
  return value with simple objects; gRPC fixtures need real (or `MagicMock`-shaped)
  `response_pb2.CheckResourcesResponse` messages — mechanical but more verbose.
- Add an integration test against the dev-compose `cerbos` service (already running with the repo's
  real policies mounted) hitting port 3593, per the ADR's implementation guidelines.
- Update whatever config `tests/e2e/test_e2e_permissions.py` / `test_guardian_objects.py` point at
  today to the new settings names.

### Rough total

- **Transport-specific delta vs. choosing HTTP: ~0.5–1 day** — mostly the `struct_pb2.Value`
  attribute-wrapping code, gRPC channel close()-on-shutdown wiring, and gRPC-specific error mapping,
  none of which exist as a pattern in this codebase today. The HTTP client's request/response types
  are plain Python objects, so that layer of ceremony disappears under Option A.
- **Shared cost regardless of transport (the real bulk of the ticket): 2–4+ days**, dominated by
  redesigning the actor/role/target-attribute mapping away from Guardian's model and validating it
  against the actual Cerbos policies — not estimated precisely here since it depends on policy
  details outside this adapter.

## Recommendation

Based on the repo evidence above, **Option A (HTTP)** fits this specific service better than the
generic gRPC recommendation in the original draft: production config already targets Cerbos's HTTP
port, there is no existing gRPC dependency or precedent in this codebase, and the on-prem/UCS deployment
model favors operational simplicity over the latency gains gRPC would bring to a service that isn't
demonstrably latency-sensitive. This recommendation is offered for team discussion, not as a final
decision.

## Decision

**Pending** — to be decided by the team based on the comparison above.

## Implementation guidelines (apply regardless of chosen option)

- Encapsulate the client in the existing `GuardianPermissionsAdapter` (or a renamed successor)
  implementing `PermissionsPort`; do not leak Cerbos-specific types (Protobuf messages or HTTP
  response models) outside the adapter.
- Create and reuse one client instance per process, following the adapter's existing
  lazily-built/cached-property pattern.
- Configure explicit request timeouts/deadlines (an equivalent to the current
  `request_timeout` setting).
- Translate Cerbos/transport errors into the existing `PermissionsError` domain exception.
- Keep action/resource-kind names as application-owned constants, not inline strings.
- Add integration tests against a real Cerbos instance (the dev `docker-compose.yaml` `cerbos` service
  already supports this) in addition to the existing mocked unit tests.
- If Option B is chosen, update `appcenter-management/compose.jinja` and the
  `ucsschool-user-management/guardian/url` UCR variable/documentation to point at port 3593, and add
  `grpcio`/`protobuf`/`cerbos` to `pyproject.toml`.
- If Option A is chosen, add `cerbos` (HTTP client) to `pyproject.toml`; `httpx` is already available.

## Reconsider this decision when

- Authorization checks become a measured latency or throughput bottleneck.
- The organization adopts a stack-wide gRPC standard for internal service calls.
- Cerbos's HTTP or gRPC SDK recommendation changes.
- The deployment model moves away from UCR-configured, on-prem Docker Compose toward an environment
  with a service mesh or centralized gRPC tooling.
