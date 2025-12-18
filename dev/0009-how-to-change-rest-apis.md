
# How to change HTTP-based REST APIs

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2025-12-18
- author: @dtroeder
- approval level: medium
- coordinated with: teams maintaining UCS and N4K, software architect, product management
- source: https://git.knut.univention.de/groups/univention/dev/internal/dev-issues/-/epics/15
- related: [ADR 0002 - Versioning of APIs and artifacts](0002-versioning-of-apis-and-artifacts.md), [ADR 0011 - How to version HTTP based REST APIs](0011-how-to-version-rest-apis.md)
- scope: all Univention HTTP/REST APIs
- resubmission: -

<!--
Most information was taken from the Etherpad at https://luns.knut.univention.de/etherpad/p/API_versioning .
Please verify if it's complete and well explained.
Then remove this comment.
-->

---

[[_TOC_]]

## Context and Problem Statement

When developing software, there is sometimes a need to change an API.
The way changes are implemented has consequences for the API producer and consumer.

This ADR defines how developers should change APIs in different scenarios.
Depending on the circumstances, this can lead to backwards-compatible or breaking changes.

A [guideline in the Development Handbook](https://univention.gitpages.knut.univention.de/dev/internal/dev-handbook/guidelines/change-rest-apis.html)
extends this ADR with more variants and examples.

_If_ a breaking change to the schema or behavior of an API is required,
[ADR 0011 - How to version HTTP-based REST APIs](0011-how-to-version-rest-apis.md)
defines how developers should handle versioning and deprecation.

## Decision Drivers

- _Usability_ of an API, in the sense of "less error-prone", "easy to implement", or "intuitive" for API-client authors.
- _Maintainability_ of the solution in the API server.
- _Maintainability_: Ease and reliability of communicating API changes to API-client authors.
  (E.g., a reference to API version `x.y.z` is more apparent than long worded sentences.)
- _Maintainability_ of the solution in API clients.
  (Allow customers to plan ahead, for how long something is still available.)

## Considered Scenarios

- Adding a new field to a resource.
- Completely new functionality or context change
- Changing the behavior of a resource
- Changing a field's data type
- Removing functionality
- Fixing bugs
- Changing the response representation for cosmetic reasons
- Dynamic change of behavior

### Adding a new field to a resource

Adding new fields and/or features is backwards-compatible as long as everything new is optional.

This backward compatibility should be strived for because, when achieved, no new version is required.

To make it easier to achieve backwards compatibility:

- Clients should ignore what they do not understand.
- Prefer adding new, optional fields and features over changing existing fields and functions.
- Implement completely new functionality or context changes in new resources
  and leave the existing resources untouched (see below).
- Collect breaking changes,
  including cleaning up after adding new fields/features,
  for a future release when a breaking change has to be introduced anyway.  

### Completely new functionality or context change

Completely new functionality or context changes are implemented in new resources,
leaving the existing resources untouched, making it backward-compatible.

When the context of a resource changes
(made-up example: instead of computer objects, there is only one computer object which handles all of them),
this is not a new version, but a new resource
(e.g., `/computer`  to `/computers` instead of `/v1/computer` to `/v2/computer`).

If possible, the API should still provide the old resource unchanged, but marked as deprecated.
Remove it from the API later, when a breaking change requires releasing a new version anyway.

### Changing the behavior of a resource

Changing the behavior of a resource is a good example of when versioning is required.
For example, a person has attributes `date_of_birth`, `street`, and `house_number`, with `house_number` optional.
But now whenever `street` is provided, `house_number` will be required → same resource, changed contract.

### Changing a field's data type

Changing the field's value type from `object` (`dict`) to `list`, or from `string` to `boolean`,
is a breaking change that requires creating a new version.

Hints:

- Whenever possible, add a new field instead of changing an existing field's type.
- Choose good names for new fields.
- Create a new version of the API.
  When possible, the service should still expose the old, deprecated version (at least for some time)
  so a client can know it and support both old and new behaviors.

### Removing functionality

When you have removed functionality from an application and want to remove the corresponding field from an API, don't.
Instead, keep it, even when it's no longer in use.
That way, you won't need to create a new API version.

When a client writes to such a field, log a warning.
Include the client's user-agent in the log entry to make it easier to identify clients that must be updated.

If you can't store the value for a removed field anymore, don't return the sent value in responses.

### Fixing bugs

If it doesn't fit the documentation, we can change it.
If it's a security bug, and the contract changes, it requires a new version.

Prefer strategy one unless there are valid reasons to choose variant two:

1. Group multiple API changes in a new version. Release when appropriate.
1. Follow a maintenance policy: Deprecate and release in X years or at release X.

### Changing the response representation for cosmetic reasons

Changing the response representation for cosmetic reasons
(e.g., fixing a typo or moving from camel-case to snake-case)
is not significant enough to warrant a breaking change.

Collect these changes and introduce them when you create the next version for more significant breaking changes.

If you wish to introduce the new notation of an existing field before the next version,
add the field to the API (that's not a breaking change)
and link it to the same value/function as the original field.

Prefer strategy one unless there are valid reasons to choose variant two:

1. Group multiple API changes in a new version. Release when appropriate.
1. Follow a maintenance policy: Deprecate and release in X years or at release X.

### Dynamic change of behavior

Sometimes UDM's behavior changes dynamically (e.g., by installing apps),
without apparent changes to the API,
but with changes in its behavior or data format, such as stricter field value ranges.

We do not provide new versions or resources in these cases.
It is an expected behavior that the API's behavior changes.

Dynamic changes in behavior are generally undesirable for an API.
Univention will not introduce such dynamic changes itself.
