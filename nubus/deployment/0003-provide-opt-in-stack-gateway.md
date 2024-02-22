
# Add opt-in stack gateway to encapsulate URL rewriting

---

- status: accepted
- deciders: tkintscher, jbornhold, jconde, jlohmer
- date: 2023-11-08
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/261

---

## Context and Problem Statement

The UMS Stack in its current form depends heavily on URL rewriting. This has
been inherited from the Appliance setup, the URL namespaces have been kept
unmodified intentionally. The question if and how this should be changed has
been left for the future, so that the insights from making the containerized
stack work would be available as input when working on this question.

In the openDesk deployment we faced the problem that different ingress
controllers are in use. The URL rewriting-needs rely on controller specific
annotations and are not supported by all Ingress controllers. As an example, in
the "dev" cluster an Ingress controller based on HAProxy is currently in use.

The question is how we should deal with the need to support various Ingress
controllers.

## Considered Options

- Encapsulate the URL rewriting need in an extra component
- Deploy a supported Ingress controller into the deployment namespace
- Try to add support for HAProxy by adding further annotations

## Pros and Cons of the Options

### Encapsulate the URL rewriting

- Good, because this works with every Ingress controller
- Good, the rewriting need is encapsulated within the UMS Stack and does not "leak" into the outside
- Good, provides an easy deployment option for all Ingress controllers
- Good, the rewriting needs are as a side-effect "documented" in one place
- Bad, a new component does increase complexity
- Bad, the setup may introduce regressions, e.g. due to wrong Header forwarding
- Risk, there may be a performance impact when using the stack gateway

### Deploy a supported Ingress controller into the namespace

- Good, it would work without a change to the UMS Stack Helm charts
- Good, because annotations would be needed only for this type of Ingress controller
- Bad, because it adds complexity due to new components
- Bad, because the Ingress controller may interfere with already deployed cluster-wide Ingress controllers

### Add support for HAProxy

- Good, because it does not add any extra component
- Neutral, because it is unclear if the specific deployment does allow this type of customization of the Ingress controller
- Bad, because it leaves the problem unsolved for other Ingress controllers
- Bad, because it increases complexity of maintaining the custom annotations

## Decision Outcome

We go with the option to "Encapsulate the URL rewriting".

As a short term approach we added another component called "Stack Gateway" which
is encapsulating the URL rewriting, so that any standards compliant Ingress
controller can be easily supported. This is considered to be a "Transitional
Architecture".

As a mid term solution we envision to have an umbrella Helm chart for the UMS
Stack which should provide the "Stack Gateway" as an opt-in component. The
needed Stories have been added into the Backlog in Gitlab.

Long term we assume that the URL rewriting should be removed or reduced. The
target picture for a long term solution has not yet been worked out or decided
upon.

## More Information

Implementation of the short term approach:

- <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/261>

Proposed Stories to implement the mid term approach:

- Create umbrella chart: <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/272>
- Provide opt-in to stack gateway: <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/275>
