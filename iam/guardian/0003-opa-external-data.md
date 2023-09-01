
# OPA external data

---

- status: accepted
- date: 2023-08-31
- author: Ole Schwiegert
- approval level: low
- coordinated with: The UCS@school team
- source: https://git.knut.univention.de/univention/components/authorization-engine/guardian/-/issues/45
- scope: ADR is only valid in the first release of the guardian as a first implementation, until a better
  and more permanent solution was designed, to supersede this ADR.
- resubmission: Until 2023-12-31

<!--
Explanation "approval level"

- low: Low impact on platform and business. Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.
- medium: Decisions of medium scope, i.e. minor adjustments to the platform or strategic decisions regarding specifications. The approval of the product owner is requested and the decision is made jointly.
- high: Decisions with a high impact on the business and IT. Changes that have a high-cost implication or strategic impact, among other things. These types of decisions require the decision to be made together with the leadership board.
-->

---

## Context and Problem Statement

The OPA service used for the Guardian in the Authorization API relies on two separate types of data. Static data, which is
shipped with the OPA container and dynamic data, which is created from the objects created in the Guardian Management API.

The problem to solve is how to get this dynamic data to the OPA container.

## Decision Drivers

<!-- This is an optional element. Feel free to remove. -->

<!-- Include qualities and architectural principles that influence the decision,
     e.g. simplicity, standardization, modularity, security, robustness, scalability, …
     See also https://git.knut.univention.de/groups/univention/dev-issues/-/wikis/home
-->

- reliability
- robustness
- scalability
- low latency

## Considered Options

The options are well documented [here (2023-08-31)](https://www.openpolicyagent.org/docs/latest/external-data/).
The options considered to solve this problem are:

- Option 3: Bundle API
- Option 4: Push Data
- Option 5: Pull Data during Evaluation

## Pros and Cons of the Options

<!-- This is an optional element. Feel free to remove. -->

### Option 3: Bundle API

<!-- This is an optional element. Feel free to remove. -->

https://www.openpolicyagent.org/docs/latest/external-data/#option-3-bundle-api

- Good, because OPA can fetch external data from a centralized server
- Good, because the OPA container does not need to be accessible
- Good, because the OPA container does not have to be monitored for crashes to ensure correct data was pushed
- Good, because most changes come for the mapping, which can utilize [Delta Bundles](https://www.openpolicyagent.org/docs/latest/management-bundles/#delta-bundles)
- Good, because bundles are cached and will only be downloaded if there are changes
- Bad, because if policies (custom conditions) change often, the load on the bundle server could be high
- Bad, because it has a potentially higher update delay than other options
- Bad, because the bundle server has to be maintained by us

### Option 4: Push Data

https://www.openpolicyagent.org/docs/latest/external-data/#option-4-push-data

- Good, because the update delay is lower than other options
- Bad, because the OPA server has to be accessible by the pushing entity
- Bad, because if OPA crashes/restarts we have to ensure proper data is pushed into the container again.
- Bad, because the pushing entity needs to keep track of all OPA containers
- Bad, because the pushing entity needs to be maintained by us

### Option 5: Pull Data during Evaluation

https://www.openpolicyagent.org/docs/latest/external-data/#option-5-pull-data-during-evaluation

- Good, because there is no update delay
- Bad, because the latency to answer policy request might be high due to fetching remote data with every request
- Bad, because authorization with the integrated http client is crude
- Bad, because the integrated http client is very basic
- Bad, because it causes a potentially high load on the Management API

## Decision Outcome

Option 3: Bundle API was chosen, as it fits the requirements not perfectly, but best of the possible solutions.

Option 4 has the big disadvantage of requiring us to somehow monitor the existing OPA containers and pushing the data
into them.

Option 5 has several disadvantages that disqualify it as a proper choice for us.

Option 3 is also the easiest to implement in our current Guardian Architecture and environment. That is briefly explored in
*More Information*.

### Consequences

- We have to implement the Bundle server
- The maximum delay of updates is `time_for_bundle_generation+pull_interval`

### Risks

- The delay might be too high for some customers

## More Information

Here we roughly explore how to possibly implement the chosen solution in our environment:

- The OPA container has to be configurable for setting the bundle server url, interval and credentials
- Our Management API needs a background task, which generates the OPABundle whenever relevant data changes.
  - This includes: POST/PATCH/DELETE role_capability_mapping, POST/PATCH on conditions
  - This might change at some point to some external job queue, like celery, but is out of scope for now.
- Our Management API needs a new endpoint that serves the generated bundle as a static file
- Authorization between the OPA container and the Management API might have to be established, if the bundle should
  be protected.
