
# UDM REST API reload upon changes to data model (modules, extended attributes/options)

---

- status: draft
- supersedes: -
- superseded by: -
- date: 2024-08-09
- author: @dtroeder
- approval level: medium <!-- (see explanation in ../../adr-template.md) -->
- coordinated with: @sschwardt, @steuwer
- source: Nubus technical board meeting 2024-08-06
- scope: ADR is only valid in Nubus for Kubernetes and as a workaround until a better solution exists
- resubmission: -

---

## Context and Problem Statement

Once started and initialized, the UDM REST API does not adapt to changes in the data model.

UDM creates its data model at runtime from Python modules and configuration objects stored in LDAP.
But it does that only once.
After the Python modules are loaded and the configuration from LDAP is applied,
UDM does not detect changes to them and won't reconfigure itself.

In UCS, a listener module detects changes to the LDAP objects and restarts the UDM REST API.
Changes to Python modules are only applied by Debian packages, which are responsible for restarting the UDM REST API.

In Nubus for Kubernetes, updates to Python modules and configuration objects in LDAP are also possible.
However, the UDM REST API is not currently restarted after such a change.
Thus, the data model of UDM REST API servers is not updated and may even be inconsistent between multiple instances.

From a customer's perspective, that is a regression compared to Nubus on UCS.
This ADR discusses the possibilities of handling this situation.

## Decision Drivers

- Standardization: The UDM REST API should behave the same in Nubus for UCS and Nubus for Kubernetes.
- Robustness: Update/configuration errors should be handled gracefully.
- Scalability: The UDM REST API may run on multiple UCS machines or in numerous containers in Kubernetes.
  In both cases, all instances must be reconfigured.
- User experience: Technical details like a service restart after a configuration change should be automated and
  not burden an operator's life.

## Considered Options

- Model UDM configuration objects as Kubernetes custom resources.
- Add an endpoint to the UDM REST API to tell it to reload itself.
- Do not support configuration changes at runtime.

## Pros and Cons of the Options

### Model UDM configuration objects as Kubernetes custom resources

When UDM configuration objects are represented as Kubernetes custom resources,
a Kubernetes operator can be created that reacts to changes to them.
It would do everything necessary to update all UDM instances.
In contrast to regular processes, an operator can restart a service or pod or
find out the IPs of all running instances to call an endpoint on each.

- Good, because it uses standardized Kubernetes features for configuration, retries, and error handling.
- Good, because hides technical details behind an API.
- Good, because an operator can implement complex update scenarios.
- Bad, because the mechanism doesn't exist on UCS and would thus incur additional maintenance effort.

### Add an endpoint to the UDM REST API to tell it to reload itself

The UDM REST API can create an endpoint that triggers a reload of its Python modules and dynamic configuration or
a restart of its child processes in multi-process mode.

- Good, because it reduces service downtime.
- Good, because it hides technical details behind an API.
- Good, because the same mechanism can be used on UCS, reducing maintenance effort.
- Bad, because it requires the update process or operator to know the addresses of all running instances.
  That may not be possible for an init container of e.g., a bundled integration.

### Do not support configuration changes at runtime

Document for developers and operators that dynamic configuration changes of UDM are not supported in Nubus for Kubernetes.
It is common and often desired that services in Kubernetes are immutable.
Changes to the data model, especially, are only done at deployment time.

The documentation should hint at the possibility of installing Python modules and configuration objects using extension containers (see [ADR 0010 - Extension bundles for Nubus](0010-extension-bundles.md)).

- Good, because is consistent with common Kubernetes practices.
- Good, because implementing this solution requires a low effort.
- Neutral, because currently installing and changing of configuration objects in LDAP cannot be prevented.
- Bad, because building extension containers may be additional effort for customers and developers.

## Decision Outcome

Chosen option: "Do not support configuration changes at runtime", because
none of the options is perfect and
the effort to implement the other options does not justify a delay of the Nubus release.

### Consequences

<!-- This is an optional element. Feel free to remove. -->

- Good, because {positive consequence, e.g., improvement of one or more desired qualities, …}
- Bad, because {negative consequence, e.g., compromising one or more desired qualities, …}
- … <!-- numbers of consequences can vary -->

### Risks

<!-- It's OK to repeat points from the above "Cons of the Options". -->
<!-- Maybe use "Risk storming" to identify risks. -->

- When implementing the decision, a {small, medium, high} risk exists, that {…}.
- …

### Confirmation

{Describe how the implementation of/compliance with the ADR is confirmed. E.g., by a review or an ArchUnit test.
 Although we classify this element as optional, it is included in most ADRs.}

## More Information

This decision should be revisited after the 1.0 release of Nubus for Kubernetes.
