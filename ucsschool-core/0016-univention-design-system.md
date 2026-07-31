# Adopt the Univention Design System as the UI component library for UCS@school User Management

- status: accepted
- supersedes: -
- superseded by: -
- date: 2026-07-03
- author: @oschwieg
- approval level: medium (see [approval_level.md](../approval_level.md))
- coordinated with: ByteBenders (feedback gathered, supportive); approved by SW architect, approval pending from PM.
- source: Proposal email "Two changes to how we build and maintain web UIs" (2026-07-03)
- scope: UCS@school User Management UI only. Adoption beyond that — by other UCS@school
  components or by other Univention products — is explicitly **not** decided here; it is
  to be evaluated once User Management has been built and operated on this stack.
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

The UCS@school User Management UI is due for a rebuild, which forces the question of
which component library it should be built on.

Our web interfaces have accumulated across several technology stacks: Dojo1 for many
years, Vue 3 for more recent work. Both stacks share a growing problem: they depend
on dedicated frontend expertise that we no longer have and have struggled to replace.
New engineers joining our teams are expected to have a strong Python background — that
is a given for the work we do — but finding someone who also brings frontend
specialization has proven difficult. Given the breadth of our product portfolio, it is
unclear whether a single dedicated frontend developer would even be sufficient.

At the same time we maintain multiple products with separate visual implementations.
As those products evolve, their UIs diverge, and there is no shared foundation that
enforces visual and behavioral consistency across the stacks.

This ADR records **two related decisions**, both scoped to the UCS@school User
Management UI, and is the single place of record for both:

1. **Whether** to build the UCS@school User Management UI on a framework-independent
   component library — the Univention Design System — instead of on a
   framework-specific one.
2. **How** that design system is built internally (component model, style
   encapsulation, styling foundation, theming, delivery).

The design system is deliberately built to be product-independent, so the wider
question — whether it should become the standard component library for Univention web
interfaces in general — is a natural follow-up. That question is **out of scope here**.
User Management is the first and, for now, only consumer; it serves as the reference
implementation on which a department- or company-wide evaluation can later be based.

## Decision Drivers

- **Reduce dependency on scarce frontend expertise**: The library must be maintainable
  by a team whose core strength is Python, and its scope must be boundable so that any
  frontend investment (a future hire or freelance work) has a clear, self-contained
  target.
- **Cross-framework compatibility**: The same component must work in Dojo1 (legacy),
  Vue 3, plain HTML, and HTMX without framework-specific adapters. For User Management
  this keeps the choice of interactivity model open; beyond it, it is the property that
  would later allow other products to adopt the library at their own pace without
  disrupting their existing stack.
- **Visual consistency**: Within User Management, a shared component library removes
  per-view styling drift, and components must look identical regardless of the host
  framework or page styles. If the library is adopted more widely later, the same
  property yields cross-product consistency without per-team coordination overhead.
- **Style isolation**: Components must guarantee their own appearance even inside host
  pages with unpredictable global CSS (notably legacy Dojo1 pages).
- **Ownership and control**: Because the components are our own, we control when and how
  they change.
- **Low long-term maintenance burden**: We want professional-grade CSS, accessibility,
  and browser-compatibility underpinnings without owning a full proprietary design
  language indefinitely.
- **Consumer theming / white-labeling**: Customers who deploy our products should be
  able to adapt colors, typography, and spacing to their own branding at the deployment
  level, without touching component or application code.
- **Simple delivery**: The artifact should be a single vendorable file with no build
  step required on the consumer side.
- **Retire redundant dependencies**: The current Vue-based component library,
  `univention-veb`, is used exclusively by the User Management and the (being retired)
  Guardian Management UI. Porting User Management to the new stack lets us retire
  `univention-veb` — replacing one library rather than adding to what we maintain.

## Considered Options

This ADR layers two decisions. The first is the adoption question for User Management;
the second only applies once adoption is chosen and concerns the internal build approach.

**Decision 1 — Whether to build User Management on a framework-independent design system:**

- Adopt the Univention Design System (framework-independent Custom Elements)
- Keep the status quo (a framework-specific component library, i.e. `univention-veb`)
- Use a third-party framework-agnostic component library
- Stay on a Vue-based component library (double down on Vue)

**Decision 2 — How to build the design system (given adoption):**

This breaks into two largely independent technology choices.

*Component model — how the components are authored:*

- Vanilla Custom Elements (no library)
- Lit
- Stencil (compile-time)
- Compile the existing Vue components (`univention-veb`) to Custom Elements (Vue's `defineCustomElement`)
- A heavier web-component toolkit (e.g. FAST)

*Styling foundation — where component styles come from:*

- Hand-written CSS with a design-token system ported from `univention-veb`
- Tailwind + DaisyUI
- Another CSS / utility framework (e.g. Bootstrap, Open Props)

## Pros and Cons of the Options

### Decision 1 — adoption

#### Adopt the Univention Design System

A UI component library built on the web platform itself: components are standard
browser-native Custom Elements, not tied to any framework. It is delivered as a single
vendorable JavaScript module and already covers a core set of components (buttons,
inputs, tables, cards, comboboxes, and more).

- Good, because the same `<u-button>` or `<u-table>` works in Vue, plain HTML, HTMX,
  and Dojo1 — User Management is not locked into one interactivity model, and any later
  adopter could take it up incrementally without disrupting their stack.
- Good, because we control when and how components change, and because the library is
  a candidate for consistent styling beyond User Management should it be adopted more
  widely.
- Good, because it can be developed and maintained independently of any product or
  backend: a frontend specialist or freelancer needs web-standards and design
  expertise, not UCS/LDAP domain knowledge. This gives any frontend investment a
  clear, bounded scope.
- Good, because it lets us retire `univention-veb` rather than adding another library.
- Good, because a utility-class styling approach (Tailwind) is highly legible to
  AI-assisted development, which helps the parts of the stack where our expertise is
  thinnest (see [ADR-0017](0017-htmx-server-rendering.md)).
- Neutral, because it does not yet contain every component we will need; reaching
  production readiness for User Management requires completing missing components.
- Bad, because we take on ownership of a new internal library and its release/versioning
  process, even if its scope is bounded.

#### Keep the status quo (a framework-specific component library)

- Good, because no migration or new library is required in the short term.
- Bad, because it perpetuates the dependency on framework-specific frontend expertise
  we struggle to hire for.
- Bad, because `univention-veb` remains to be maintained for a single remaining
  consumer once the Guardian Management UI is decommissioned.
- Bad, because visual inconsistency with other Univention products continues to
  accumulate as each evolves independently.

#### Use a third-party framework-agnostic component library

- Good, because we would not own the component implementations.
- Neutral, because framework-agnostic third-party libraries do exist (also
  Custom-Elements-based).
- Bad, because we lose control over the roadmap, visual identity, and theming model.
- Bad, because matching our existing visual design and white-labeling requirements
  against an external roadmap is harder than owning a thin theme layer over
  maintained foundations.
- Bad, because it does not clearly reduce the expertise problem — integrating and
  customizing a third-party library still requires frontend depth.

#### Stay on a Vue-based component library (double down on Vue)

- Good, because it reuses the existing `univention-veb` investment.
- Bad, because it couples User Management — and any later consumer — to Vue, which is
  exactly the framework dependency we are trying to reduce.
- Bad, because it does not work in Dojo1 or HTMX pages without adapters, blocking
  incremental cross-stack adoption.
- Bad, because it keeps the UI layer dependent on frontend specialization the teams
  lack.

### Decision 2 — internal build approach

Two technology choices drive the build: which **component model** authors the
components, and which **styling foundation** provides their look. The existing Vue 3
library (`univention-veb`) — 27 components covering form inputs, data grids, modals,
buttons, and loading states, with a CSS custom property token system for light and dark
themes — is the visual and functional reference for both.

#### Component model

##### Vanilla Custom Elements (no library)

- Good, because it has zero dependencies and no library churn to track.
- Good, because it is the lowest-level, standards-only baseline.
- Bad, because reactive rendering, attribute/property reflection, and templating must
  all be hand-written and maintained.
- Bad, because the extra boilerplate per component makes AI-assisted contributions and
  reviews harder to keep consistent.

##### Lit

A thin (~5 KB) layer over the Custom Elements standard providing templating and reactive
properties — no framework runtime.

- Good, because it stays close to the platform, so components remain framework-independent
  by construction.
- Good, because it is widely used (Google, Adobe, Microsoft), well-documented, and
  heavily represented in AI training data, which matters for AI-assisted maintenance.
- Good, because it removes the Custom Elements boilerplate without imposing a build-time
  compiler or opinionated conventions.
- Neutral, because it adds a dependency, though a small, stable, low-churn one.

##### Stencil (compile-time)

- Good, because it compiles to standards-based Custom Elements and can generate
  framework wrappers.
- Bad, because it introduces a heavier compiler-centric build and toolchain than Lit.
- Bad, because it is more opinionated and less commonly seen than Lit, with a smaller
  footprint in AI training data.

##### Compile the existing Vue components (`univention-veb`) to Custom Elements

Reuse the existing Vue components by compiling them to native Custom Elements via Vue's
`defineCustomElement`.

- Good, because it reuses the existing, already-styled component implementations rather
  than re-authoring them.
- Good, because the output is consumable as Custom Elements in any stack, like the other
  options.
- Bad, because each element still bundles the Vue runtime, so the "no framework runtime"
  benefit is lost and bundle size grows.
- Bad, because it keeps the design system coupled to Vue and its upgrade cycle — the
  framework dependency this effort aims to shed.
- Bad, because `defineCustomElement` has known rough edges (styling injection, slots,
  prop/attribute typing) that need working around, and the result is less legible to
  AI-assisted work than plain Lit.

##### A heavier web-component toolkit (e.g. FAST)

- Good, because it ships a large pre-built component set.
- Bad, because it imposes more framework-specific conventions and a larger surface to
  own and learn.
- Bad, because it couples the design language more tightly to a third party's roadmap.

#### Styling foundation

##### Hand-written CSS with a ported `univention-veb` token system

- Good, because it gives direct visual parity with the existing library with minimal
  design work.
- Good, because there is no external CSS dependency.
- Bad, because the team keeps owning the full design language — accessibility, browser
  edge cases, and design evolution are all manual.
- Bad, because more component styles are hand-written and maintained.

##### Tailwind + DaisyUI

- Good, because DaisyUI provides tested, accessible component structures and Tailwind a
  maintained utility layer, offloading work a small internal team cannot match.
- Good, because Tailwind's utility classes map directly to CSS properties, making it
  unusually legible to AI-assisted development.
- Good, because a custom DaisyUI theme (`univention-light`/`univention-dark`) maps the
  existing design tokens (~25 variables) onto a community-backed foundation instead of a
  proprietary one.
- Neutral, because DaisyUI's token structure differs between major versions; the chosen
  version must be pinned.
- Bad, because it is a one-time effort to map existing token names (e.g.
  `--bgc-content-body`) to DaisyUI's (e.g. `--b1`).

##### Another CSS / utility framework (e.g. Bootstrap, Open Props)

- Good, because these are mature and maintained.
- Neutral, because they would achieve broadly similar offloading of CSS maintenance.
- Bad, because Bootstrap carries its own visual identity and JS, and Open Props is
  tokens-only without DaisyUI's component structures — neither fits our combination of a
  custom theme plus tested component patterns as cleanly.

#### Implementation approach: encapsulation and CSS delivery

Given Lit + Tailwind/DaisyUI, one implementation question remains: how component styles
are isolated from host-page CSS. This matters because components must render identically
inside legacy Dojo1 pages with unpredictable global styles.

- **Light DOM**: the simplest setup, but no style encapsulation — host CSS leaks in and
  component CSS leaks out; unsafe in unknown host contexts.
- **Shadow DOM + constructable stylesheet**: Shadow DOM isolates components; the
  Tailwind/DaisyUI CSS is compiled once at build time into a single `CSSStyleSheet`
  shared across all shadow roots, solving the Tailwind/Shadow-DOM incompatibility via the
  [`CSSStyleSheet` / constructable stylesheets (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/CSSStyleSheet/CSSStyleSheet).
  Consumer theming still works because CSS custom properties pierce the shadow boundary
  by design. The trade-off is a less common, deliberately-configured Vite build. This is
  the chosen approach.

## Decision Outcome

**Decision 1:** Build the UCS@school User Management UI on the Univention Design System.
It is the only option that simultaneously delivers framework independence, an
independently maintainable and boundable frontend scope, retirement of
`univention-veb`, and a customer-theming model — while building on maintained community
foundations to keep our long-term ownership surface small.

This decision binds **only** the UCS@school User Management UI. No other UCS@school
component and no other Univention product is required to adopt the design system on the
basis of this ADR. Whether it becomes the standard component library across the
department or the company is to be decided separately, once we have shipped and
operated User Management on it (see [Path to wider adoption](#path-to-wider-adoption)).

**Decision 2:** Author the components with **Lit** over the native Custom Elements
standard, and build their look on **Tailwind + DaisyUI** with a custom **Univention
DaisyUI theme** (`univention-light`, `univention-dark`) derived from the existing visual
design. Lit keeps us close to the platform with a minimal runtime while staying
framework-independent — unlike compiling the existing Vue components, which would carry
the Vue runtime along and perpetuate the framework coupling we are trying to shed.
Tailwind + DaisyUI offloads accessibility, browser compatibility, and component
structure to maintained community foundations and is highly legible to AI-assisted work.
Components are encapsulated with **Shadow DOM**, with the compiled Tailwind/DaisyUI CSS
shared across shadow roots via a **constructable stylesheet** — chosen over Light DOM
because genuine style isolation is a hard requirement given legacy Dojo1 host pages with
unpredictable global CSS.

### Why not reuse the existing Vue components?

It is technically possible to take our current Vue components and repackage them as
reusable web components, and at first glance that looks cheaper — we would reuse what we
already built. We chose not to, for reasons that matter beyond the code:

- **It would keep the very dependency we are trying to remove.** Each repackaged
  component still carries Vue inside it. We would stay tied to Vue's release cycle and
  still need Vue expertise to maintain the library — exactly the frontend-hiring problem
  that motivated this decision.
- **It is heavier for end users.** Every page would ship the Vue engine bundled inside
  the components, making the UI larger and slower to load than components built on the
  browser's native foundation.
- **The repackaging path is fragile.** Vue's web-component export has known rough edges,
  so we would spend effort working around them rather than moving forward.

Building the components fresh on a small, standards-based foundation is modestly more
work up front, but it produces components that are genuinely independent of any
framework, lighter for users, and maintainable by our Python-strong team with AI
assistance. In short: repackaging Vue would be a shortcut that preserves the problem;
building fresh removes the dependency for good.

### Key parameters

| Concern                  | Decision                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------- |
| Component model          | Lit                                                                                 |
| DOM encapsulation        | Shadow DOM                                                                          |
| Styles inside components | Shared constructable stylesheet (Tailwind + DaisyUI, compiled at build time)        |
| Design language          | DaisyUI custom theme (`univention-light`, `univention-dark`)                        |
| Token injection          | Injected into `document.head` at library load time                                  |
| Delivery artifact        | Single ES module: `univention-design-system.js`                                     |
| i18n                     | None — all user-visible strings are consumer-provided via attributes or named slots |
| Customization surface    | CSS custom properties + DaisyUI themes + CSS Shadow Parts                           |

### Consumer integration

```html
<script type="module" src="univention-design-system.js"></script>
<body class="theme-light">
  <u-button variant="primary">Save</u-button>
  <u-input-text label="Username"></u-input-text>
</body>
```

No separate CSS file, no build step, no framework adapters required.

### Path to wider adoption

The UCS@school User Management UI is the first and, under this ADR, the only product
built on the design system. It serves as the reference implementation.

Nothing here obliges any other team to adopt it. Because the library's elements work in
any HTML context, a later adopter could introduce it component by component within an
existing product, including current Vue applications — but that is a possibility this
ADR keeps open, not a decision it makes.

A department- or company-wide evaluation should follow once User Management has shipped
on the design system and been operated for a meaningful period. That evaluation is a
separate ADR at the appropriate level (i.e. under `dev/`), and would need to weigh at
least: component completeness against other products' needs, whether dedicated frontend
capacity is available to evolve the library beyond one consumer, the migration cost for
existing Dojo1 and Vue UIs, and the accessibility and theming experience gathered from
User Management.

### Consequences

- Good, because User Management gains a framework-independent set of UI components,
  visually isolated from host-page CSS.
- Good, because the DaisyUI foundation reduces long-term maintenance burden on design,
  accessibility, and browser compatibility.
- Good, because the single-file delivery model is trivially vendorable, which keeps the
  door open for other products without committing them to anything.
- Good, because `univention-veb` can be retired once User Management is ported and the
  Guardian Management UI is decommissioned.
- Good, because frontend investment (hire or freelance) now has a clear, bounded,
  backend-agnostic scope.
- Good, because customer white-labeling is possible and clearly defined via CSS custom
  properties and DaisyUI themes without modifying components.
- Bad, because we own a new internal library, its component completeness, release
  process, and versioning.
- Bad, because a library maintained for a single consumer carries the risk of being
  under-invested in; this is accepted deliberately while the wider-adoption question is
  still open.
- Bad, because the constructable stylesheets approach is less familiar than Light DOM and
  requires careful Vite build configuration.

### Risks

- When implementing the decision, a **medium** risk exists that the component set is
  incomplete for a real product; reaching production readiness for User Management
  requires an accessibility review, visual alignment with the existing product,
  documentation, and completing missing components (estimated 2–3 developer-weeks).
  Note that `univention-veb` never underwent a proper accessibility review either, so
  this is new work rather than a regression from today's baseline.
- When implementing the decision, a **low-to-medium** risk exists that the library stays
  a single-consumer library if no dedicated frontend capacity (hire or freelance) is
  allocated to evolve it beyond User Management's needs. This bounds the cost — the
  scope is one UI — but it also means the later company-wide evaluation may conclude
  against wider adoption.
- When implementing the decision, a **low** risk exists that DaisyUI version upgrades
  require reviewing the custom theme mapping; the chosen major version must be pinned.
- When implementing the decision, a **low** risk exists around Dojo1 support for the
  Custom Elements v1 lifecycle (`connectedCallback`, etc.); Dojo1 predates the standard
  and may have upgrade-timing quirks in dynamically-rendered content. This is low
  priority as those UIs are likely to be replaced rather than extended.

### Confirmation

The decision is confirmed by the UCS@school User Management UI shipping on the design
system and by `univention-veb` being removed from active maintenance once its two
consumers no longer depend on it. Component completeness and accessibility for User
Management are worked on and confirmed as part of building the Q3 2026 MVP, validated by
review against the existing product.

Wider adoption is explicitly not part of this confirmation criterion.

## More Information

### Existing implementation

The design system already exists as a prototype implementing the decisions above
partially:

- Repository:
  <https://git.knut.univention.de/univention/dev/libraries/univention-design-system>
- Storybook (component catalog and design reasoning):
  <https://univention-design-system-5b148e.gitpages.knut.univention.de/>

### Discussion: is a custom design language too much to maintain?

The existing `univention-veb` token system is self-contained and fairly small
(~35 CSS properties), so it is fair to ask whether the maintenance concern is real. The
conclusion was that the token system itself is not the burden — it is everything around
it:

- **Accessibility**: focus styles, forced-colors support, high-contrast mode, and ARIA
  patterns in CSS require ongoing attention as browser standards evolve. DaisyUI absorbs
  this.
- **Component structures**: DaisyUI provides tested HTML patterns for buttons, inputs,
  selects, modals, and tables. Building these from scratch means owning every edge case.
- **Community**: bug reports and fixes from a large user base improve the library in
  ways a small internal team cannot match.

The one-time cost of mapping ~25 token values to DaisyUI's naming convention is worth
paying in exchange for reducing long-term ownership surface.

### Discussion: Shadow DOM and consumer customization

A concern was raised about whether Shadow DOM would prevent customers from customizing
component styles for white-labeling. Shadow DOM does restrict arbitrary CSS overrides
from outside — this is intentional — but three mechanisms remain available to consumers:

1. **CSS custom properties**: CSS variables pierce the Shadow DOM boundary by
   specification. Redefining any DaisyUI theme variable (`--p`, `--b1`, `--bc`, etc.) on
   `:root` or any ancestor cascades into all Shadow DOMs — covering the full color
   palette, typography, and spacing a typical white-labeling requirement would touch.
2. **DaisyUI named themes**: consumers can define their own theme entirely in CSS and
   apply it to any subtree via a `data-theme` attribute, without touching the library.
3. **CSS Shadow Parts (`::part()`)**: components can expose internal elements as named
   parts (e.g. `u-input-text::part(input)`), allowing surgical overrides without opening
   the entire Shadow DOM. The library controls which parts are exposed, maintaining
   structural integrity.

This makes Shadow DOM a feature for customization rather than an obstacle: the library
defines a clear, stable surface for theming instead of exposing all internals to
accidental breakage.

### Visual reference

The component scope and visual design are derived from `univention-veb`, whose 27
components define the initial scope: buttons, a full form element suite (text, password,
date, checkbox, select, combobox, multi-input, multi-select, textarea), data grid,
table, modal, confirm dialog, and loading states. Its token files are the source for the
`univention-light` / `univention-dark` DaisyUI theme mapping.

### Related decisions

This ADR is the first of a pair. The interactivity model that consumes these components
for the new server-rendered User Management UI is covered in
[ADR-0017: Move to HTMX-based server rendering](0017-htmx-server-rendering.md).
ADR-0017 depends on this ADR; this ADR stands on its own and can be adopted
independently of the HTMX decision.

This decision moves the UCS@school User Management UI away from the component library
implied by [ADR-0002: JavaScript framework for the UI of the new UCS@school frontend
modules](0002-js-framework.md). No other UCS@school frontend module will be built on
Vue, so User Management is the only UCS@school consumer of that stack.
