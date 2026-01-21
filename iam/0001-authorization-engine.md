# Nubus authorization engine

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2026-01-21
- author: @dtroeder
- approval level: high <!-- (see explanation below) -->
- coordinated with: Dev, PO, PM, LT (@fbest, @fbotner, @stefan, @dgrebe, @tkiese, @tkintscher, @oschwieg, @steuwer)
- source: Various epics for the introduction of a Role and Access Model (RAM) for UCS@school, the Portal, and UDM.
- scope: Univention-wide decision for the use of a common authroization engine in all products.
- resubmission: -

<!--
Explanation "approval level"

- low: Low impact on platform and business.
  Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.
- medium: Minor adjustments to the platform or strategic decisions regarding specifications.
  The approval of the product owner is requested and the decision is made jointly.
- high: Decisions with a high impact on the business and IT.
  Changes that have a high-cost implication or strategic impact, among other things.
  These types of decisions require the decision to be made together with the leadership board.
-->

---

## Context and Problem Statement

Currently, every Univention software performs and implements authorization independently.
For customers, this means they must configure and monitor access to each application separately.
Examples:

- The UMC uses policies to find out which modules and endpoints a user or group has access to.
- The UDM REST API's authorization code matches a user's username and groups against a set of UCR variables.
  (Fine-grained authorization is deferred to OpenLDAP ACLs.)
- The UCS@school library uses the value in a user's extended attribute to determine a user's roles.
  It authorizes operations on user and group objects.
  (Fine-grained authorization is deferred to OpenLDAP ACLs.)
- Access to Wi-Fi networks is managed by a script interpreting the value in a user's, group's, or computer's extended attribute.
- Access to apps is usually authorized by setting a value of an app-specific extended attribute on users or groups.

To improve Nubus’ manageability and security,
we introduce a unified role and access model (RAM) to be used by all Univention software.
It allows the customer to interactively and non-interactively define access for all applications
and apply that setting to users and groups.
It doesn’t require the customer to write source code.

We separate the policy engine from the applications and centralize it,
because that way it’s much better extensible, maintainable, and observable.

For further details, read the paper on Univention's _Role and Access Model Strategy_: [2026-01-16_RAM_Strategy.pdf](2026-01-16_RAM_Strategy.pdf).

## Decision Drivers

See sections _3. The solution_ and _4. ABAC implementation_ in [2026-01-16_RAM_Strategy.pdf](2026-01-16_RAM_Strategy.pdf).

## Considered Options

See section _5. Comparison Guardian and alternative implementations_ in [2026-01-16_RAM_Strategy.pdf](2026-01-16_RAM_Strategy.pdf).

## Decision Outcome

Chosen option: "Guardian" (the containerized service),
because it meets all functional and non-functional criteria,
or can be updated to do so with manageable effort.

### Consequences

The individual authorization mechanisms implemented in Nubus components will iteratively be replaced by requests to Guardian.

### Risks

- When migrating software to use the Guardian,
  we take an iterative approach to identify risks early on and obtain feedback at an early stage.
  Iterations are defined as closely as possible to real use cases.
  - We try to assess known concerns based on use cases and identify risk hotspots as early as possible,
    without claiming 100% completeness.
- We use feature flags to roll out applications with experimental features.
  - This allows us to use and roll out the Guardian and applications using the Guardian without declaring them "production ready" yet.
- Developed code is merged to component's `main` branches and released with stable releases.
  The non-stable parts are disabled by feature flags.
  Customers can activate these, with appropriately limited support.
  - This gives us confidence that the code is maintainable and allows for quick customer feedback.
  - The early availability, even when not finalized, allows internal testing of features, e.g., using ProfS.
- Replaced authorization features will be discontinued, providing a migration path,
  and removed after some time to reduce the maintenance effort.
- UCS packages the Guardian using the App Center.
  The App Center's dependency management is very limited.
  It doesn't allow specifying a minimal and maximum version of a required app.
  With the broader use of the Guardian, we expect a continued incremental development.
  It's likely that soon in UCS, the App Center's current dependency management won't suffice.
  Then, we'll have to invest in the Self-Provider Portal and the App Center.
