
# UDM (REST API) reload upon changes to data model (modules, extended attributes/options)

---

- status: accepted
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

Once started and initialized, the UDM (REST API) does not adapt to changes in the data model.

UDM creates its data model at runtime from Python modules and configuration objects stored in LDAP.
But it does that only once.
After the Python modules are loaded and the configuration from LDAP is applied,
UDM does not detect changes to them and won't reconfigure itself.

In UCS, a listener module detects changes to the LDAP objects and restarts the UDM REST API.
Changes to Python modules are only applied by Debian packages,
which are responsible for restarting the UDM REST API and other Python-UDM clients like the UMC.

In Nubus for Kubernetes, updates to Python modules and configuration objects in LDAP are also possible.
However, the UDM REST API, the UMC and the UDM Transformer are not currently restarted after such a change.
Thus, the data model of UDM REST API, UMC and the UDM Transformer instances is not updated and
may even be inconsistent between multiple instances.

From a customer's perspective, that is a regression compared to Nubus on UCS.
This ADR discusses the possibilities of handling this situation.

## Decision Drivers

- Standardization: The UDM software should behave the same in Nubus for UCS and Nubus for Kubernetes.
- Standardization: The deployment configuration and runtime settings of UDM software are currently sourced from multiple places (UCR, LDAP environment variables, …). A single configuration source makes installations easier to clone, manage, migrate, test, and explain, reducing misconfiguration risks and improving user experience.
- Robustness: Update/configuration errors should be handled gracefully.
- Scalability: UDM software (UDM REST API, UMC and UDM Transformer) may run on multiple UCS machines or
  in numerous containers in Kubernetes.
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
- Good, because all types of Python-UDM software can register themselves and an operator can restart them all.
- Bad, because the mechanism doesn't exist on UCS and would thus incur additional maintenance effort.

### Add an endpoint to the UDM REST API to tell it to reload itself

The UDM REST API can create an endpoint that triggers a reload of its Python modules and dynamic configuration or
a restart of its child processes in multi-process mode.

- Good, because it reduces service downtime.
- Good, because it hides technical details behind an API.
- Good, because the same mechanism can be used on UCS, reducing maintenance effort.
- Bad, because it requires the update process or operator to know the addresses of all running instances.
  That may not be possible for an init container of e.g., a bundled integration.
- Bad, because it won't help to restart the UMC and the UDM Transformer.

### Do not support configuration changes at runtime

Document for developers and operators that dynamic configuration changes of UDM are not supported in Nubus for Kubernetes.
It is common and often desired that services in Kubernetes are immutable.
Changes to the data model, especially, are only done at deployment time.

The documentation should hint at the possibility of installing Python modules and configuration objects using extension containers (see [ADR 0010 - Extension bundles for Nubus](0010-extension-bundles.md)).

- Good, because is consistent with common Kubernetes practices.
- Good, because implementing this solution requires a low effort.
- Good, because this works for all types of Python-UDM software (currently UDM REST API, UMC and UDM Transformer).
- Neutral, because currently installing and changing of configuration objects in LDAP cannot be prevented.
- Bad, because building extension containers may be additional effort for customers and developers.
- Bad, because the pre-existing concept of dynamic extended attributes would effectively be abandoned.

## Decision Outcome

Chosen option: "Do not support configuration changes at runtime", because
none of the options is perfect and
the effort to implement the other options does not justify a delay of the Nubus release.

### Consequences

Nubus for Kubernetes does not support configuration changes at runtime,
which is different from how it behaves in UCS.
We should document this so customers migrating from UCS know it.

### Risks

The risk exists that regardless of what we document,
customers use the UDM REST API to dynamically change extended attributes without restarting UDM-using services.
Even if the resulting support cases can be quickly closed with a link to the documentation,
it leaves a bad taste that a REST API offers an endpoint that requires manual intervention.

### Confirmation

{Describe how the implementation of/compliance with the ADR is confirmed. E.g., by a review or an ArchUnit test.
 Although we classify this element as optional, it is included in most ADRs.}

## More Information

This decision should be revisited after the 1.0 release of Nubus for Kubernetes.
