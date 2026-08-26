# Rewrite the Guardian component by keeping only the PDP and switching to Cerbos

- status: final
- supersedes: [nubus/guardian/0001-authorization-engine](./0000-authorization-engine.md), [nubus/guardian/0002-management-persistence](./0002-management-persistence.md), [nubus/guardian/0003-opa-external-data](./0003-opa-external-data.md), [nubus/guardian/0004-testing](./0004-testing.md), [nubus/guardian/0005-testing-frontend](./0005-testing-frontend.md)
- superseded by: -
- date: 2026-08-25
- author: @fbotner
- approval level: high (see [approval_level.md](../../approval_level.md))
- coordinated with: nubus core, PM, @dtroeder
- source: Onsite meeting protocol https://etherpad-lite.knut.univention.de/etherpad/p/guardian-onsite
- scope: Nubus, UCS@school, integrations
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

Guardian is the authorization engine for Nubus/UCS. Its Policy Decision Point (PDP)
is currently built on top of Open Policy Agent (OPA) and is entirely self-implemented.
The system spans five deployable components: a Management API (FastAPI + PostgreSQL),
an Authorization API (FastAPI), a Management UI (Vue 3), a shared library, and OPA
itself running as a sidecar. Policies are expressed in Rego, stored in PostgreSQL,
compiled into bundles, and polled by OPA every 10–15 seconds.

Over time, integrating the OPA-based Guardian into UCS (specifically into UDM) has
surfaced a large set of conceptual, API design, and operational problems
(see [README-authorization.md](https://git.knut.univention.de/univention/dev/ucs/-/blob/5.2-6/management/univention-directory-manager-modules/README-authorization.md)).
The original requirements had called for the creation of a _full ABAC system_:

- Policy Decision Point (PDP) (→OPA)
- Policy Retrieval Point (PRP) (→Policy bundle server)
- Policy Information Point (PIP) (→Endpoint that fetches actor/target data)
- Policy Administration Point (PAP) (→Management API and UI)

In 2026, it was decided to change the product's current requirements.
Although all of the above ABAC components would be required in the long term, only the PDP would be needed in the short- to medium-term.

The inherent complexity of the full ABAC system increased the implementation effort required to fill the gaps before it could be released to production.
On top of that, there existed a mismatch between its conceptual model and the needs of UDM and UCS operators.
With the reduced requirement set, the full Guardian system became unnecessarily hard to maintain and evolve.

[Cerbos](https://cerbos.dev) is an established open-source PDP that uses declarative
YAML policies with CEL expressions for conditions. A proof-of-concept branch
(`cerbos`) replaces the entire five-component stack with a single Debian package
(`univention-guardian-server`) running Cerbos in a systemd-managed Docker container.
A much simpler system (no PIP, PRP, PAP, and management interface)
that better matches the now-reduced requirements.

## Decision Drivers

- **Maintainability:** How much effort is it to *maintain* and *evolve* the finished application?
  Does the team have the required expertise?
  Does the architecture allow adapting and extending the application's features in the future?
  How much effort is it to support the application's dependencies?
- **User experience:** How easy is it for customers to manage and adapt the application?
- **Established open-source project:** Cerbos is an actively maintained, production-grade
  open-source project with a commercial backer, a public community, and extensive
- **Established open-source project:** How active is the project?
  Are there enough maintainers that the project can survive long-term?
  Is the project used by companies or organizations in production and at scale?
  How good is the documentation?
  How many open security issues are there, and how fast is the maintainers' response time?
- **Operability:**  How many components must an operator install, configure, monitor, and back up?
  How easy is it to scale a Guardian deployment?
  Can a policy change be rolled out, reviewed, and rolled back with standard Nubus tooling?
  Can an operator determine why a request was denied without reading source code or querying the database?
  How well can Guardian be installed, configured, upgraded, and uninstalled in Nubus deployments (UCS and Nubus for Kubernetes)?
- **Policy propagation latency:** How fast are policy updates distributed and loaded by all PDP instances in a Nubus domain?

## Considered Options

- Keep the OPA-based Guardian PDP and fix its known problems incrementally
- Keep the OPA-based Guardian PDP and drop the custom stack (PIP, PRP, PAP, and management interface).
- Replace the PDP with Cerbos while keeping the Management API and UI
- Replace the entire Guardian stack (PDP + Management API + UI) with Cerbos as the sole PDP

## Pros and Cons of the Options

### Keep the OPA-based Guardian PDP and fix its known problems incrementally

Continue developing and improving the existing five-component OPA-based stack.

- Good, because it has a administrative UC (Management UI) to manage rules.
- Bad, because the existing system has a long list of documented conceptual problems that
  require fundamental design changes, not incremental fixes (ambiguity of implementation
  patterns, capabilities bound to roles preventing reuse, no negative/subtractive
  permissions, no dynamic contexts, restricted character set, no policy lifecycle
  concept, JSON-only API with no human-writable rule format).
- Bad, because fixing the conceptual problems would require breaking API changes to the
  Management API, the client library, and the OPA Rego policy model simultaneously.
- Bad, because the Management API alone exposes 50 REST endpoints backed by 10 SQL
  tables and a 1,746-line business logic module — all custom code with no upstream to
  share the maintenance burden.
- Bad, because Rego expertise is scarce within the team, making onboarding of new
  contributors and review of policy correctness slow and error-prone.
- Bad, because UDM integration revealed that the Guardian permission model
  (additive-only, no wildcard expansion, capabilities namespace-bound) cannot cleanly
  express the requirements of a dynamically extensible system like UDM without
  significant workarounds and brittle convention.

### Keep the OPA-based Guardian PDP and drop the custom stack (PIP, PRP, PAP, and management interface)

Reduce the five-component OPA-based stack to only the PDP (OPA).
Create policies directly in the PDP's language.
Same as _Replace the entire Guardian stack with Cerbos as the sole PDP_, but with OPA instead of Cerbos.

Retire the Management API, Authorization API, Management UI, shared library,
and authorization client. Ship OPA as a Debian package. Policies are authored as
Rego files, versioned in Git, and distributed via the standard UCS errata mechanism.

- Good, because OPA is an established open-source project with active upstream
  maintenance, a public community, commercial backing, and extensive documentation —
  Univention does not own the authorization engine implementation.
- Good, because YAML + CEL is a standardized, human-readable policy format that can be
  reviewed in Git, tested offline with `cerbos compile`, and understood without
  specialized language expertise.
- Good, because the maintenance surface collapses to the bare minimum required for the authorization functionality.
- Good, because replacing five independently deployed components with a
  single `apt install` aligns with UCS's operational model and reduces the operational
  burden on both Univention and customers.
- Bad, because the Management UI and REST API for interactive policy management are
  removed; policy authoring becomes a file/package operation, which may not be
  acceptable long-term for administrators without Git or shell access.
- Neutral, because it's _unknown_ if the conceptual and integration problems with the current OPA-based Guardian
  can be fixed when removing the Authorization API and writing policies in Rego. It would require new concepts that haven't been evaluated.
- Bad, because removing the Authorization and Management APIs would break existing clients (UCS@school User Management).
- Bad, because Rego expertise is scarce within the team, making onboarding of new
  contributors and review of policy correctness slow and error-prone.

### Replace the PDP with Cerbos while keeping the Management API and UI

Use Cerbos as the runtime PDP while retaining the Guardian Management API and UI for
policy authoring, translating Guardian concepts to Cerbos policies on the fly.

- Good, because OPA is an established open-source project with active upstream
  maintenance, a public community, commercial backing, and extensive documentation —
  Univention does not own the authorization engine implementation.
- Good, because there's already a working client application for it: the UCS@school User Administration.
- Good, because it preserves the existing administrative UX (Management UI) and REST API
- Neutral, because it reduces operational risk at the cost of significantly increased
  implementation complexity: a translation layer between Guardian's data model
  (permissions, capabilities, conditions, roles stored in PostgreSQL) and Cerbos YAML
  resource policies must be written, tested, and maintained.
- Bad, because the translation layer inherits all the conceptual problems of the Guardian
  data model — it does not solve them, only relocates them.
- Bad, because two policy representations (PostgreSQL + Cerbos YAML) must be kept in
  sync, introducing a new class of consistency bugs.
- Bad, because the Management API, UI, and PostgreSQL dependency remain — the largest
  contributors to operational and maintenance cost are not removed.

### Replace the entire Guardian stack with Cerbos as the sole PDP

Retire the OPA-based Management API, Authorization API, Management UI, shared library,
and authorization client. Ship Cerbos as a Debian package. Policies are authored as
YAML files, versioned in Git, and distributed via the standard UCS errata mechanism.

- Good, because Cerbos is an established open-source project with active upstream
  maintenance, a public community, commercial backing, and extensive documentation —
  Univention does not own the authorization engine implementation.
- Good, because YAML + CEL is a standardized, human-readable policy format that can be
  reviewed in Git, tested offline with `cerbos compile`, and understood without
  specialized language expertise.
- Good, because the proof-of-concept `cerbos` branch already demonstrates a working
  prototype.
- Good, because the self-implemented OPA stack requires maintaining five services,
  a custom bundle-build pipeline, Rego expertise, and a PostgreSQL schema. The total
  maintenance surface is disproportionately large relative to the authorization
  functionality delivered.
- Good, because replacing five independently deployed components with a
  single `apt install` aligns with UCS's operational model and reduces the operational
  burden on both Univention and customers.
- Bad, because the Management UI and REST API for interactive policy management are
  removed; policy authoring becomes a file/package operation, which may not be
  acceptable long-term for administrators without Git or shell access.
- Bad, because Cerbos has no override/shadow semantics: two policies with the same
  `(resource kind, version)` are a compile error. Third-party policies can only add new
  resource kinds, not override or extend shipped ones.
- Bad, because the PIP (principal attribute enrichment from UDM/LDAP) is not yet
  defined; callers must supply all principal and resource attributes in the authorization
  request, shifting lookup responsibility to integrators.
- Neutral, because the Cerbos branch is still a proof-of-concept; the context-aware
  authorization model (e.g. OU-scoped roles via CEL hierarchy expressions) is designed
  but not yet fully implemented.

## Decision Outcome

Chosen option: **"Replace the entire Guardian stack with Cerbos as the sole PDP"**,
because the fundamental problems with the OPA-based Guardian PDP are conceptual and
architectural — not merely implementation gaps — and cannot be addressed without
rewriting the system anyway. Adopting Cerbos as an established external component
eliminates the maintenance burden of a custom PDP, provides a simpler and more readable
policy language, and aligns with the UCS packaging model. The missing pieces
(transport authentication, domain-wide policy distribution, PIP integration) are
well-scoped engineering tasks, not fundamental blockers.

### Consequences

- Good, because Univention no longer maintains a custom Policy Decision Point; upstream
  Cerbos handles security patches, performance improvements, and language evolution.
- Good, because policy review, testing, and auditing become standard Git workflows
  (`cerbos compile` for offline validation, diff-based review in merge requests).
- Good, because the operational surface shrinks from five independently deployed
  services to one Debian package.
- Bad, because the policy propagation latency changes from a known 10–15 sec lag
  (OPA bundle polling) to an _unknown_ duration (Listener replication).
- Bad, because the Guardian Management UI and REST API are retired; a replacement
  administrative interface (or explicit decision to manage policies as files) must be
  designed and communicated to operators.
- Bad, because existing Guardian-based integrations (apps using the Authorization
  Client, callers of the Authorization API) must be migrated to the Cerbos gRPC/HTTP
  API or a new Univention-provided client wrapper.

### Risks

- **Open items in the proof-of-concept:** Transport authentication, policy distribution
  across the UCS domain, and PIP (LDAP attribute enrichment) are not yet implemented.
  These must be completed before the Cerbos-based Guardian can be released. Tracked in
  issues [#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/288)
  and [#291](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/291).
- **Policy distribution:** Without a replacement for the Guardian Management API's
  policy storage, policy distribution to non-primary UCS servers requires a defined
  mechanism (e.g. LDAP-based distribution via `settings/data` and a listener handler,
  as addressed in ADR 0003).

### Confirmation

This decision is confirmed when:
1. The Cerbos-based `univention-guardian-server` package passes all integration tests
   in the `ucs-test-guardian` suite in a staging environment.
2. The open items (transport auth, domain policy distribution, PIP integration) are
   resolved and implemented.
3. At least one consuming service (e.g. new school modules) has been migrated from the
   OPA-based Authorization API to the Cerbos API and validated in a real deployment.

## More Information

- Current OPA-based implementation:
  https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian
- Cerbos proof-of-concept (`cerbos` branch):
  https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/tree/cerbos
- UDM authorization integration problems:
  https://git.knut.univention.de/univention/dev/ucs/-/blob/5.2-6/management/univention-directory-manager-modules/README-authorization.md
- Cerbos open-source project: https://cerbos.dev
