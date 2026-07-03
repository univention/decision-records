# Move to HTMX-based server rendering for the UCS@school User Management UI

- status: draft
- supersedes: -
- superseded by: -
- date: 2026-07-03
- author: @oschwieg
- approval level: medium (see [approval_level.md](../approval_level.md))
- coordinated with: ByteBenders (feedback gathered, supportive); approved by SW architect, approval pending from PM.
- source: Proposal email "Two changes to how we build and maintain web UIs" (2026-07-03)
- scope: The new UCS@school User Management UI only. Whether this becomes the default
  approach for other UCS@school components or for Univention web UIs in general is
  explicitly **not** decided here; it is to be evaluated once User Management has been
  built and operated on this stack.
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

The UCS@school User Management UI is being rebuilt, which raises the question of how its
interactive parts should be built.

The interactive parts of our newer UIs — User Management among them — are built as Vue
single-page applications: a JavaScript SPA that runs in the browser, calls our backend
APIs, and manages its own state. These applications — with their TypeScript build
pipelines, Pinia state stores, Vite configuration, and JavaScript test suites — are
increasingly maintained by engineers whose core strength is Python, not frontend. This
slows us down and creates ongoing risk, because the SPA model requires dedicated
frontend expertise that we no longer have and have struggled to hire.

How should we build the interactive parts of the UCS@school User Management UI so that
engineers who are strong in Python can own the full request-to-response cycle, without a
separate frontend build process, dependency tree, and framework mental model?

This ADR concerns the interactivity model. The visual components it renders are
provided by the Univention Design System — see
[ADR-0016](0016-univention-design-system.md). **This decision depends on ADR-0016**:
the design system provides the visual components; HTMX provides the interactivity.

The same problem exists in other Univention products, so this decision is a plausible
candidate for wider use. That question is **out of scope here**: this ADR decides the
approach for UCS@school User Management, which serves as the reference implementation on
which a department- or company-wide evaluation can later be based.

## Decision Drivers

- **Reduce dependency on scarce frontend expertise**: UI logic should stay in Python,
  where the team is strong, so the request-to-response cycle can be owned without a
  context switch into a separate frontend ecosystem.
- **Thinner stack, lower maintenance**: One language and one ecosystem for tooling
  updates, security patches, and feature changes instead of two; no separate JavaScript
  build step or dependency tree to keep current.
- **Clear, testable frontend/backend boundary**: The boundary becomes the HTTP
  response — easy to reason about and to test.
- **Legibility to AI-assisted development**: HTMX's HTML-attribute programming model and
  server-side Python logic are unusually well-represented in current AI models' training
  data, so AI assistance is most effective precisely where the team's expertise is
  thinnest — the frontend layer.
- **Incremental, low-risk migration**: The approach must be adoptable page by page, so
  User Management can serve some routes on the new model while others remain on Vue
  during the transition. Because the new and old stacks may look slightly different, a
  mixed state within a single product is not always acceptable — so switching wholesale
  must remain an option too.
- **Bounded blast radius**: User Management is a small, self-contained UI. Trying the
  approach there keeps the cost of being wrong low, and produces evidence before anyone
  else has to decide anything.

## Considered Options

- HTMX-based server-rendered HTML (Python) with the design system
- Continue with the Vue SPA model
- Adopt another JavaScript SPA framework (e.g. React, Svelte)
- Adopt another server-side hypermedia framework (e.g. Turbo/Hotwire, Unpoly)

## Pros and Cons of the Options

### HTMX-based server-rendered HTML (Python) with the design system

HTMX is a small JavaScript library that lets a server respond to user interactions with
HTML fragments rather than JSON; the browser updates only the affected part of the page.
UI logic stays on the server in Python, and the frontend is HTML templates with
declarative attributes — no component lifecycle and no JavaScript build step. For richer
client-side behavior that HTMX does not cover, Alpine.js fills the gap without
introducing a framework. Visual components come from the design system as Custom
Elements. A proof of concept implementing the User Management UI on this stack (live
search/filtering, dependent dropdowns, cursor-based pagination, role-based rendering)
was built against a stub backend to validate that the approach handles the interaction
complexity of the real product.

- Good, because UI logic stays in Python; engineers strong in the backend own the full
  request-to-response cycle without a frontend context switch.
- Good, because there is no separate frontend build process, no JavaScript dependency
  tree to maintain, and no framework-specific mental model to acquire.
- Good, because the frontend/backend boundary is the HTTP response — clear and testable.
- Good, because it is server-render-friendly for configuration-driven UIs
  (per-customer column selection, field visibility, server-side translations) without a
  client-side configuration or localisation layer.
- Good, because extending functionality (e.g. batch actions on table rows) means adding
  a server endpoint and template attributes — no component tree or client state to
  restructure.
- Good, because the stack is unusually legible to AI-assisted development, making the
  frontend layer tractable for a Python-strong team. Both the design system and the PoC
  were built in under 20 hours with AI assistance.
- Good, because it is learnable by anyone who understands HTML forms and HTTP; it
  extends HTML rather than introducing a new programming model. The shipped User
  Management implementation will serve as onboarding material for future work.
- Good, because migration can proceed page by page — new and Vue routes can run side by
  side during the transition — though, as noted above, differing looks between the two
  stacks mean a mixed state is not always acceptable, so switching wholesale may be
  preferable.
- Neutral, because it depends on adopting the design system ([ADR-0016](0016-univention-design-system.md))
  for its visual components.
- Bad, because genuinely rich client-side interactions may need Alpine.js, adding a
  (small) second client-side concern — though to date our product portfolio contains no
  client-side-heavy interactive UIs, so this rarely bites in practice.
- Bad, because server round-trips for interactions differ from the SPA model and shift
  some load and latency considerations to the server.

### Continue with the Vue SPA model

- Good, because no migration is required and existing Vue applications keep working.
- Neutral, because the SPA model is well suited to very rich client-side interactivity,
  but our UIs are mostly forms over database entries (LDAP, SQL) that rarely need it.
- Bad, because it perpetuates the dependency on frontend expertise (TypeScript, Pinia,
  Vite, JS test suites) the teams lack.
- Bad, because it maintains two ecosystems and build pipelines instead of one.
- Bad, because the reactivity/component/type-system interaction has more surface area
  for errors that are hard to catch without deep framework knowledge — including for
  AI-assisted work.

### Adopt another JavaScript SPA framework (e.g. React, Svelte)

- Good, because these are mature, widely used frameworks with large ecosystems.
- Bad, because switching SPA frameworks does not solve the core problem: it still
  requires dedicated frontend expertise and a JavaScript build/dependency toolchain.
- Bad, because it would be a large migration with no reduction in the two-ecosystem
  maintenance burden.

### Adopt another server-side hypermedia framework (e.g. Turbo/Hotwire, Unpoly)

- Good, because these share HTMX's server-rendered, hypermedia philosophy and its
  benefits for a backend-centric team.
- Neutral, because they would achieve broadly similar architectural goals.
- Bad, because HTMX has the simplest, most declarative HTML-attribute model, the
  broadest presence in AI training data, and a validated PoC in our context; the
  alternatives carry more convention or JS-ecosystem assumptions without a clear
  advantage for us.

## Decision Outcome

Chosen option: **Build the interactive parts of the UCS@school User Management UI as
server-rendered HTML made interactive through HTMX (with Alpine.js where richer client
behavior is needed), rendering visual components from the Univention Design System.**
The ByteBenders have decided to build the new User Management UI on this stack,
targeting a releasable MVP by end of Q3 2026, integrated with the existing backend
(Kelvin) and Keycloak.

This is the option that directly addresses the frontend-expertise dependency by keeping
UI logic in Python, removes the separate JavaScript build/ecosystem burden, gives a
clear and testable HTTP boundary, and is validated by a working proof of concept
against the real interaction complexity of the product.

This decision binds **only** the UCS@school User Management UI. No other UCS@school
component and no other Univention product is required to move to HTMX on the basis of
this ADR; existing Vue applications stay as they are. Migration within User Management
is not big-bang either: the approach can be adopted page by page.

### Path to wider adoption

User Management is a small, self-contained UI, which bounds the risk and produces a
reference implementation before any other team must decide anything.

Whether HTMX-based server rendering should become the default for other UCS@school
components, for the department, or for Univention web UIs in general is to be evaluated
after User Management has shipped and been operated on the stack. That evaluation
belongs in a separate ADR at the appropriate level (i.e. under `dev/`), and would need
to weigh at least: how the team actually experienced owning the full request-to-response
cycle, whether the maintenance burden dropped as expected, how the model held up under
real customer usage and configuration-driven requirements, and the migration cost for
existing Vue and Dojo1 UIs.

Until then, the timeline below should be read as this team's plan for User Management,
not as a rollout commitment for anyone else.

### Consequences

- Good, because the new User Management frontend can be owned end to end by a
  Python-strong team, with AI assistance for the frontend layer.
- Good, because there is one language and ecosystem to patch and update for this UI.
- Good, because it establishes a reference implementation and onboarding material,
  which is what a later, broader evaluation will be based on.
- Good, because configuration-driven and customer-specific UI behavior becomes a
  server-side concern, avoiding client-side configuration/localisation layers.
- Bad, because we take on a new interactivity model that the team must learn (mitigated
  by its low learning curve and the PoC).
- Bad, because some interactions may still require Alpine.js, a small additional
  client-side dependency.
- Neutral, because Vue applications in other Univention products continue to exist;
  there is no forced migration.

### Risks

- When implementing the decision, a **medium** risk exists around backend integration
  complexity: the PoC runs against a stub backend and does not integrate with Kelvin or
  Keycloak. The MVP's real work is connecting to those (Python work in the team's core
  competence) and matching the current feature set (estimated 4–6 developer-weeks). The
  bottleneck is more likely integration and review cycles than raw development time.
- When implementing the decision, a **low-to-medium** risk exists that some future
  interaction genuinely needs richer client-side behavior than HTMX/Alpine.js
  comfortably provide; this is bounded by the option to use Alpine.js and, in the
  extreme, to serve a specific route with a different model. It is further mitigated by
  the design system: because its components also work in a Vue SPA (see
  [ADR-0016](0016-univention-design-system.md)), such a route could fall back to Vue
  while keeping a consistent look.
- When implementing the decision, a **low** risk exists that the approach is read as a
  wider commitment than it is. It is not: adoption beyond UCS@school User Management is
  a separate decision, gated on the User Management experience.

### Confirmation

Confirmed by the UCS@school User Management MVP shipping on HTMX + the design system,
integrated with the existing backend and Keycloak, by end of Q3 2026, matching the
current feature set. The clear HTTP-response boundary is confirmed by end-to-end tests
exercising the rendered routes and fragments.

Adoption outside User Management is explicitly not part of this confirmation criterion.

## More Information

- Timeline (from the proposal), for UCS@school User Management:
  - **Q3 2026 — User Management MVP**: build and ship the new User Management UI on
    HTMX and the design system, integrated with the existing backend; reference
    implementation for both decisions.
  - **Q4 2026 — Iteration**: add remaining features, address UX feedback, stabilize.
  - **2027 and beyond — Evaluation for wider adoption**: on the basis of that
    experience, evaluate whether either or both approaches should be recommended beyond
    User Management. Any such recommendation requires its own ADR at the appropriate
    level; there is no forced migration for any team.
- This ADR is the second of a pair and **depends on**
  [ADR-0016: Adopt the Univention Design System](0016-univention-design-system.md),
  which provides the visual components rendered by this approach. ADR-0016 can be
  adopted independently of this decision; this decision cannot be realized without it.
- This decision moves the UCS@school User Management UI away from the SPA architecture
  recorded in [ADR-0001: New UI architecture for UCS(@school) frontend
  modules](0001-new-ui-architecture.md) and the framework choice recorded in
  [ADR-0002: JavaScript framework for the UI of the new UCS@school frontend
  modules](0002-js-framework.md). No other UCS@school frontend module will be built on
  Vue, so User Management is the only UCS@school consumer of that stack.
- The AI-suitability assessment of this stack (HTMX attributes, Python server logic,
  Tailwind utility classes, Custom Elements) was authored by an AI assistant and
  reviewed by the author; it should be read as an informed perspective, not an
  objective claim.
