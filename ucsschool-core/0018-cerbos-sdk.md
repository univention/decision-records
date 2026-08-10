# Cerbos Python client transport for UCS@school User Management

- status: proposed
- supersedes: -
- superseded by: -
- date: 2026-08-10
- author: Jan Gietzel
- approval level: low (see [approval_level.md](../approval_level.md))
- coordinated with: Daniel Tröder, Sönke Schwardt-Krummrich, Johannes Lohmer
- source: -
- scope: The Cerbos client transport used by the user-management-bff's `PermissionsPort`
  adapter only. Not binding for other Cerbos integrations — UDM's and Portal's transport
  choices are separate, still-open decisions (see "More Information").
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

The UCS@school User Management module's Guardian integration is being adapted to talk to
Cerbos-based Guardian. The `PermissionsPort` abstraction isolates the domain from the
concrete client, so this decision is scoped to the transport used inside the adapter that
implements that port.

The official `cerbos` Python package ships two async clients against the same Cerbos PDP:

```python
from cerbos.sdk.client import AsyncCerbosClient        # HTTP/JSON
from cerbos.sdk.grpc.client import AsyncCerbosClient   # gRPC
```

Which transport should the adapter use?

This module is a UCS App Center app, installed on-prem at individual customer sites and
configured through UCR variables — not a Kubernetes/service-mesh environment. That shapes
several of the decision drivers below.

## Decision Drivers

- **Authorization is on the hot path of every request.** Every UI request depends on an
  authorization check, and Cerbos limits how many resources can be checked in a single
  request; the adapter already has to batch large checks into chunks of ~50 resources.
  A check across a few thousand entities therefore means many sequential round trips, so
  small per-call latency differences compound rather than being a one-off cost.
- **HTTP is not Cerbos's native transport.** Cerbos's HTTP API is served via
  `grpc-gateway`, which internally translates every HTTP/JSON request into gRPC before it
  reaches the Cerbos service: `Python SDK → HTTP/JSON → grpc-gateway → gRPC → Cerbos
  service`, versus `Python SDK → gRPC/protobuf → Cerbos service` directly. HTTP is
  effectively Cerbos's backwards-compatible fallback path, not a co-equal alternative.
- **Error-detail fidelity.** While testing the HTTP client, a Cerbos-side batch-limit
  error (`"number of resources in batch (102) exceeds configured limit (50)"`) was
  visible only in Cerbos's own server logs, not ours: the SDK's `raise_on_error=True`
  triggers an `httpx` response hook that raises a generic `400 Bad Request` before the
  SDK's own structured error body is parsed. The gRPC client surfaces the same failure as
  `grpc.aio.AioRpcError`, whose `.details()` already contains the descriptive message —
  no extra unpacking code needed to get useful errors into our own logs.
- **Field debuggability at customer sites.** This is a self-hosted, on-prem app without a
  service mesh; inspecting our adapter's own traffic to Cerbos is easier over plain
  HTTP/JSON (`curl`, browser tools) than over a gRPC channel. This is mitigated by Cerbos
  itself continuing to expose a plain HTTP interface independent of which transport our
  adapter uses — for debugging policies directly against Cerbos, admins/support can still
  `curl` that interface; only our own application's call path moves to gRPC.
- **API-stability risk (open).** gRPC's generated stubs are more brittle to upstream API
  changes than an HTTP/JSON client. How much this matters depends on how often Cerbos's
  API actually changes — not yet assessed against Cerbos's version history, so this risk
  is noted but unresolved rather than weighed one way or the other.
- Cerbos's own SDK documentation recommends the gRPC client as the default for new
  projects.

## Considered Options

- Async HTTP/JSON client (`cerbos.sdk.client.AsyncCerbosClient`)
- Async gRPC client (`cerbos.sdk.grpc.client.AsyncCerbosClient`)

## Pros and Cons of the Options

### Async HTTP/JSON client

- Good, because production config already targets Cerbos's HTTP port — no infrastructure
  or UCR variable changes needed.
- Good, because plain JSON is the easiest thing to inspect at on-prem customer sites
  without a service mesh.
- Good, because request/response types are plain Python objects, with less adapter
  boilerplate than hand-built Protobuf messages.
- Neutral, because it pulls in the same `grpcio`/`protobuf` dependency tree as the gRPC
  client regardless — the `cerbos` package ships both clients' generated code in one
  distribution, so dependency footprint is not a real differentiator between the options.
- Bad, because it is not Cerbos's native transport: every request is translated to gRPC
  internally by `grpc-gateway`, an extra hop the gRPC client avoids.
- Bad, because the SDK swallows Cerbos's descriptive error body behind a generic `400 Bad
  Request` unless the adapter adds extra unpacking code — observed directly while testing
  the batch-size-limit error above.
- Bad, because higher per-call overhead compounds given Cerbos's batch-size limit forces
  large permission checks into many sequential round trips.
- Bad, because it diverges from Cerbos's own recommended default for new projects.
- Bad, because request/response payloads are dynamically-typed JSON — the adapter is
  responsible for validating shapes and types itself before sending a request, a class of
  bugs the gRPC client's statically typed Protobuf messages avoids by construction.

### Async gRPC client

- Good, because it talks to Cerbos's native transport directly, without the
  `grpc-gateway` translation hop HTTP goes through.
- Good, because failures surface with full detail via `grpc.aio.AioRpcError.details()` —
  no extra error-unpacking code needed, unlike the HTTP client.
- Good, because persistent HTTP/2 connections lower per-call overhead, which matters given
  authorization checks are on the hot path and get chunked into many round trips for large
  requests.
- Good, because it matches Cerbos's own recommended default for new projects.
- Good, because Protobuf messages are statically typed — the generated schema catches
  shape/type errors at construction time, reducing type errors and removing the need for
  the adapter to hand-validate request data before sending it.
- Neutral, because it pulls in the same dependency tree as the HTTP client (see above).
- Bad, because it requires re-plumbing production config — the UCR variable and
  `compose.jinja` network setup currently target Cerbos's HTTP port via a URL, not a bare
  `host:port` gRPC target.
- Bad, because our adapter's own traffic to Cerbos is harder to inspect directly at
  on-prem customer sites without a service mesh than plain HTTP/JSON would be — mitigated
  by Cerbos itself continuing to expose a plain HTTP interface for debugging policies
  directly, regardless of which transport our adapter uses in production.
- Bad, because it introduces gRPC channel lifecycle management and Protobuf message
  construction as new patterns in this codebase.
- Neutral, because statically generated stubs are more brittle to API changes than
  JSON — impact depends on how often Cerbos's API actually changes, which hasn't been
  assessed yet.

## Decision Outcome

Chosen option: **async gRPC client**, because the hot-path/batch-chunking latency
exposure and the removed `grpc-gateway` translation hop already favor gRPC, and the
error-detail fidelity gap tips it further: working around the HTTP client's
error-swallowing behavior would mean writing `httpx`-specific unpacking code purely to
compensate for a transport we would only be using as an intermediate step — that code
would become dead weight the moment we move to gRPC, so going directly to gRPC avoids
that throwaway work entirely. The loss of `curl`-level debugging against our own
adapter's calls is an acceptable trade-off given Cerbos's own HTTP interface remains
available for debugging policies directly.

### Consequences

- Good, because per-call overhead drops on a request path that is both hot and chunked
  into many round trips for large checks.
- Good, because Cerbos's own error detail lands directly in our logs instead of being
  swallowed behind a generic HTTP status.
- Bad, because production config (the `ucsschool-user-management/guardian/url` UCR
  variable and `compose.jinja`) must migrate from a URL to a bare `host:port` target — a
  customer-facing change needing a migration note for existing on-prem installs.
- Neutral, because this decision does not bind UDM's or Portal's separate,
  still-open Cerbos transport choices.

### Risks

- A **medium** risk exists that gRPC's generated stubs prove more brittle against future
  Cerbos API changes than an HTTP/JSON client would have been
- A **low** risk exists that diagnosing connectivity issues in our adapter's own gRPC
  calls specifically needs a support-process update (e.g. documenting `grpcurl`) — policy-
  level debugging remains possible via Cerbos's own HTTP interface regardless.

### Confirmation

Confirmed by an integration test against a real Cerbos instance (the dev `docker-compose`
`cerbos` service, already exposed on the gRPC port), and by a regression test asserting
that a batch-size-limit error's descriptive message is visible in our own logs — the
concrete failure that motivated the error-fidelity driver above.

## More Information

- Background and further detail on the Cerbos-Guardian integration:
  [authorization-engine/guardian README](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/blob/cerbos/README.md?ref_type=heads).
- UDM's Cerbos integration is, per its own spike investigations so far, expected to use
  HTTP/JSON; Portal's is undecided but leaning gRPC. Neither is binding on this decision —
  each integration's transport is its own choice, made against its own constraints.
