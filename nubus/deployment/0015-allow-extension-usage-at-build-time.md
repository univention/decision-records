
# Allow extension usage at build-time

---

- status: accepted
- date: 2024-06-07
- author: jbornhold
- approval level: low
- coordinated with: Team Nubus Dev
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/732

---

## Context and Problem Statement

We did move the extension handling into run-time, see
[ADR-0010](./0010-extension-bundles.md). One drawback of the approach is that we
move code around at run-time and to some degree go against the idea of immutable
container images / read only file-systems.

A risk exists that a (potential) customer cannot use Nubus with the current
extension mechanism because their security policy forbids changes to containers
at runtime.

Should we keep a fallback option for affected users to mitigate this risk?

## Considered Options

- Keep a fallback option to bundle extensions at build-time
- Keep no fallback option

## Decision Outcome

We aim to keep a fallback option, so that it is possible to build custom images
instead of moving the code around at run-time. The fallback option is limited to
keeping the extension images in a way so that using them during a container
build is possible.

We do not add dedicated support for this scenario into the Helm chart
configuration to avoid complexity. This has the consequence that some extra
efforts will be required when bundling extensions at build-time.

The decision to keep compatibility with this approach is intended to be interim
until we gain more confidence about the chosen extension approach from the first
users.

### Consequences

- Good, because we keep the option available for special needs
- Good, because removing a constraint from an API is much easier than adding a
  constraint.
- Good, because we avoid extra complexity in our Helm charts
- Good, because it allows us to gain feedback about the chosen extension
  mechanism
- Bad, because there is an extra constraint around our extension image design

### Risks

There is no risk in this decision.

In case the decision turns our to be problematic in the future, then a conscious
decision can be taken to drop the compatibility and remove this constraint.

## More Information

- [ADR-0010](./0010-extension-bundles.md)
- [Nubus Infocenter about Extensions](https://git.knut.univention.de/univention/internal/nubus-infocenter/-/tree/main/topics/extensions?ref_type=heads)
- [Spike to develop the extension concept](https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/443)
