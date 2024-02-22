
# Use `common-helm` to document best practices around Helm usage

---

- status: accepted
- deciders: Team SouvAP Dev
- author: <johannes.bornhold.extern@univention.de>
- date: 2023-10-10

---

## Context and Problem Statement

[`common-helm`](https://git.knut.univention.de/univention/customers/dataport/upx/common-helm)
started as an experiment to group useful Helm utilities in one place, so that it
can be used across the various Helm charts for the Univention Management Stack
(UMS). `common-helm` does currently provide a Helm chart called `common` which
does extend Bitnami's `common` chart with template utilities to create
Kubernetes resources like `ConfigMap`, `Deployment` and others. By now it does
see widespread adoption across most charts of the UMS.

At the same time we do have accumulated notes about our Helm related best
practices, design principles and similar topics in our team notes in
[`team-souvap`](https://git.knut.univention.de/univention/customers/dataport/team-souvap).

Should we "promote" `common-helm` to become the one go-to place for how we
implement our Helm charts?

## Decision Outcome

[`common-helm`](https://git.knut.univention.de/univention/customers/dataport/upx/common-helm)
will become the canonical place to hold both code and documentation regarding
best practices, conventions, design principles.

The main reason is that this results in one point to find out everything
relevant regarding common ways how Helm is used in the UMS. Compared to this the
team repository has been more like an interim solution.

## More Information

- `common-helm` -
  <https://git.knut.univention.de/univention/customers/dataport/upx/common-helm>

- `team-souvap` -
  <https://git.knut.univention.de/univention/customers/dataport/team-souvap>

- Bitnami's `common` chart -
  <https://github.com/bitnami/charts/tree/main/bitnami/common>
