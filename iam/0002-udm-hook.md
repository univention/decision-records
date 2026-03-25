# OX-Connector bug fix using a UDM move hook instead of a data migration

- status: accepted
- supersedes: -
- superseded by: -
- date: 2026-03-12
- author: @tkiese
- approval level: medium (see [approval_level.md](../approval_level.md))
- coordinated with: Team WIN, Team Nubus Core, PM @steuwer, SW architect @dtroeder
- source: https://git.knut.univention.de/groups/univention/dev/projects/open-xchange/-/epics/3
- scope: -
- resubmission: -

## Context and Problem Statement

This ADR is to document a divergence from our architectural default,
specifically solving a bug using a UDM hook
where a migration to the `univentionObjectIdentifier` would have been a viable solution as well.

### Background

This work was caused by epic https://git.knut.univention.de/groups/univention/dev/projects/open-xchange/-/epics/3.

_Summary of the bug:_
`oxDeputyPermissiongivenTo` refers to DN of other users.
The DN of a user changes during a move, but is not updated in other users' `oxDeputyPermissiongivenTo`.

_What alternative solutions were investigated:_
Implementing the switch to `univentionObjectIdentifier` would require a migration,
iterating all users and updating their `oxDeputyPermissiongivenTo`.
This would need to be implemented separately for UCS and Nubus for Kubernetes.
Due to the early stage of Team WIN's existence, we do not yet have all the required knowledge.
Therefore, this implementation would be very costly right now, but likely easier down the road.

## Decision Drivers

Deciding factors in this decision were the goals to deliver solutions efficiently (impact vs effort), minimize the risk of regressions, and in a non-breaking manner.

This problem occured in the early stage of Team WIN's existence, meaning knowledge of procedures across the platforms and associated risks were limited. This introduced additional risks and effort to any solution the team is not yet well-versed in.
Additionally, we expect more breaking changes in the coming months in the Ox-Connector. We need to limit the number of breaking changes, as customers delay such updates.

## Considered Options

1. Replacing the DN in users' oxDeputyPermissiongivenTo with the univentionObjectIdentifier, as it is independent of a user's location in the ldap tree, i.e. not changing during a move.
2. Implementing a move hook in UDM which is triggered on moves and then updates oxDeputyPermissiongivenTo to a user's new DN.

## Pros and Cons of the Options

The move hook has the following benefits compared to the univentionObjectIdentifier-option:

- No breaking change.
- Faster to implement (around 1/3rd of the effort estimated).
- Less risk, since the modify hook can be used as template, limiting the amount of new code. And the team has more expertise in this.
- Enabling other move hook implementations down the road, i.e. by Professional Service - though the extent of this is currently unknown.
- The (enterprise) customer affected by the bug is still using UCS 5.0 where the univentionObjectIdentifier is not available

The following downsides of the hook option have been identified:

- The univentionObjectIdentifier is the canonical way according to our architecture - we should do the work down the road anyway.
- The hook will likely introduce a (small) performance impact on moves.
- When the hook is implemented in UDM, others can add custom move hooks.
- Custom hooks are a known source of recurring need for support.

## Decision Outcome

Chosen option: Implementing the move hook in UDM.

### Consequences

- Good, because the fix is available sooner.
- Good, because the same fix is applicable to both UCS 5.0 and 5.2
- Good, because the product is extended beyond the immediate scope of this bugfix.
- Bad, because the hook introduces new code that needs to be maintained.
- Neutral: The migration to univentionObjectIdentifier can be implemented at a later date together with other breaking changes.

### Risks

The hook likely will introduce a negative performance impact on moves. The team will conduct performance tests during implementation to access this impact.
While implementing the rejected option at a later date is desired, it adds work to a future breaking changes. The risk exists that the implementation won't be done as the bug is already fixed during the hook.
