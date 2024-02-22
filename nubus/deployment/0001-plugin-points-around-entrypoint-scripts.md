
# Add plugin points around the entrypoint scripts

---

- status: accepted
- deciders: tkintscher, rabdulatipov, jbornhold
- date: 2023-10-09
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/228

---

## Context and Problem Statement

We have seen that for some cases the provided options to customize the UMS
components are not sufficient. Currently we are providing customized image
builds where the product container image does contain the project specific
customization which can be activated based on various switches.

With the work on integrating the SWP specific customization needs it became
apparent that we need a way to keep those things separate.

The question is how can we allow customization from the outside without having
to keep all potential needs in the default container images?

## Decision Outcome

We add plugin points around the entrypoint scripts of our container images. This
way it is possible to run custom scripts before or after the regular entrypoint
script by mounting those into a defined place within the container.

### Consequences

- Good, because there is a defined way how to plug in custom scripts
- Good, because customization is easily possible without copying the original
  entrypoint script

### Risks

Overusing this approach to adjust the behavior can lead to difficult to maintain
or upgrade results. We assume that there is a trade-off decision to be made when
the customization reaches a certain level, at this an extension of the original
component or even a fork of it would be more appropriate.

We have also discussed a risk that users of our containers can use this approach
to customize things which they are not supposed to customize. While discussing
this we found that this is also the case without this approach, e.g. by mounting
in a custom entrypoint script to replace the container's original one the same
possibilities can be achieved. Due to this reason we do not see this as a
particular risk of this decision.

## More Information

- The Spike in which we investigated the options:
  <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/228>

- The implementation in the base container image:
  https://git.knut.univention.de/univention/customers/dataport/upx/container-ucs-base/-/merge_requests/13
