
# Drop the Helm chart `common-helm`

---

- status: accepted
- date: 2024-02-15
- author: johannes.bornhold.extern@univention.de
- coordinated with: openDesk Dev Team
- source: https://git.knut.univention.de/groups/univention/-/epics/698, https://git.knut.univention.de/groups/univention/-/epics/722

---

## Context and Problem Statement

We started to add the Helm chart `common-helm` during the early phase of the
Nubus development. Back then we did observe that our Helm charts for the various
components were not consistent. Using a common chart with templates for
Kubernetes resources like `Deployment` was an intended counter measure to
mitigate this problem.

Now we are working on the umbrella chart for Nubus and refactoring most charts
to improve them in terms of security and a common interface of the values
configuration. We also found that the indirection through the templates of
`common-helm` does make it more difficult to understand the Helm charts.

Should we keep using `common-helm` as a central chart?

## Decision Drivers

- It is difficult to understand what the templates of a component chart really
  do, due to increased complexity.
- Helm has only a very simple mechanism to handle dependencies, it does not
  support one dependency in different versions within the dependency tree. There
  is no way to consistently pin the dependency to one particular version for an
  umbrella chart and all its dependencies.

## Considered Options

- Keep `common-helm` and aim to further increase its usage.
- Drop `common-helm` and accept a certain level of duplication.

## Decision Outcome

We drop the Helm chart `common-helm` in its current form and accept a certain
level of duplication across the component charts. In this case, the
gain of easy-to-understand Helm charts is higher than that of avoiding repetition.
We assume we can achieve consistency across the charts by leveraging
tooling for automatic linting and unit testing around our Helm charts.

We are going to foster the knowledge sharing and transfer by amending and
improving our internal developer notes to contain

- applied design principles,
- the expected style of the charts,
- and the common requirements (which e.g. derive from BSI IT-Grundschutz).

### Risks

- There is a small risk that we will see increased inconsistencies emerge until
  linting / testing is in place. This is assumed to be easy to correct.

## More Information

- The `common-helm` repository which also contains the Helm chart `common-helm`:
  <https://git.knut.univention.de/univention/customers/dataport/upx/common-helm>

- Current team notes about Helm charts:
  <https://univention.gitpages.knut.univention.de/customers/dataport/team-souvap/tech/helm.html#design-principles>
