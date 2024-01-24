# Handle Renovate updates manually in UMS

---

- status: accepted
- date: 2024-01-23
- author: jbornhold
- coordinated with: openDesk Dev Team, edamrose

---

## Context and Problem Statement

We have added Renovate as a tool to keep our dependencies up-to-date. As a
result we get automatically (based on a scheduled run) Merge Requests with
dependency updates on all repositories related to openDesk.

How shall we handle those Merge Requests?

## Considered Options

- Automatic merge if the CI pipeline did pass.
- Review and merge by the reviewer.

## Decision Outcome

We start by handling the Merge Requests via our regular review workflow with the
difference that the Reviewer shall also merge the Merge Request after approval.

This is applied for repositories which run tests as part of the pipeline on a
merge request, so that the Reviewer can see that tests are passing before
merging. For special cases where the CI pipeline does not yet run the tests on a
merge request this will have to be ensured manually by the Reviewer.

The main reasons are the following:

- This allows us to get experience with the dependency handling before
  considering to automate this process fully.

- It is unclear if all our repositories have sufficient automatic test coverage
  so that a fully automated process would be stable enough.

## Pointers

- Related Issue in Gitlab:
  <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/361>

- Common CI contains job templates:
  <https://git.knut.univention.de/univention/customers/dataport/upx/common-ci>
