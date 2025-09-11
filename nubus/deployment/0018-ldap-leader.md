# LDAP Leader Election

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2024-11-18
- author: @jconde
- coordinated with: Nubus for k8s Team
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/925
- approval level: medium

---

## Context and Problem Statement

The current LDAP server chart allows for launching read-only secondaries to
handle large numbers of read requests, however it only allows to safely run one
primary which handles write requests and is the single source of truth.
In order to provide a high-availability setup, we would like to make the
primary instance redundant, such that a replica could take over immediately
should the active node fail.

A robust and easy to manage setup is openLDAP's Mirror Mode as described in [Sec. 18.2.3 in the manual](https://www.openldap.org/doc/admin25/replication.html).
It allows running **two** LDAP primaries with both of them active at the same time,
but ensuring that **only one** slapd process receives write requests at any given time.
This has to be enforced by a load-balancer.
The changes will then be synced to the other instance.
Should one primary fail, the load balancer will start directing requests to the other primary, allowing the first one to be recreated/rebuilt in the mean time.

We currently have a PoC-quality implementation of the Mirror Mode which is
supposed to become production ready, and with this ADR we evaluate different
options for configuring the Service Manifest to reliably allow the operation
in Mirror Mode.

The current experimental solution, relying on readiness probes, has shown to be
unreliable and have problematic side-effects.
The chosen option should replace the current experimental solution.

## Decision Drivers

1. **Reliability**: Ensure only one primary is active at a time.
1. **Robustness**: Improve the high-availability setup for the LDAP system.
1. **Scalability**: Support up to two LDAP primaries in a high-availability setup.
1. **Maintainability**: Replace the custom lock mechanism with a more robust and stablished solution.
1. **Data Consistency**: Ensure data consistency during failover scenarios.

## Considered Options

- Maintain status quo with ReadinessProbe adjustments and dynamic service routing labels
- Using Coordinated Leader Selection
- Leader Election using Kubernetes Leases API

## Pros and Cons of the Options

### Maintain status quo with ReadinessProbe adjustments and dynamic service routing labels

The current setup uses a custom lock mechanism to ensure only one primary is `Active-Active` at a time. This approach has some limitations and we see two LDAP `Active-Active` primaries at times.

- Bad, because it doesn't consistently solve the issue of having two `Active-Active` LDAP primaries.
- Bad, because we rely on maintaining a custom lock mechanism for leader election.
- Bad, because it shows an LDAP pod as `Not Ready` even though it is ready to take over if needed and is mirroring the `Active-Active` primary.

### Using Coordinated Leader Selection

Coordinated Leader Selection is a Kubernetes feature that provides leader election for a group of replicas. This feature is currently in alpha state and not recommended for production use.

- Good, because it provides leader election for a group of replicas.
- Bad, because it is currently in alpha state and not recommended for production use.

### Leader Election using Kubernetes Leases API

Kubernetes Leases API provides a mechanism for leader election and coordination. This approach is more robust and reliable than the current custom lock mechanism.

- Good, because it provides a robust and reliable mechanism for leader election.
- Good, because it is a more established solution than the current custom lock mechanism.
- Good, because it ensures only one primary is `Active-Active` at a time.
- Good, because it ensures automatic failover to the `Hot-Standby` in case of leader failure.
- Neutral, because it requires additional complexity with the addition of a sidecar container.

## Decision

We will implement a leader election mechanism using Kubernetes Leases API for
the LDAP primaries. This approach will replace the current custom lock
mechanism and provide a more robust solution for managing `Active-Active` and
`Hot-Standby` deployments in Kubernetes, using the existing OpenLDAP Mirror-Mode.

## Details

### Implementation

1. A sidecar container will be added to each LDAP pod.
1. The sidecar will use the Kubernetes Leases API to compete for and maintain leadership.
1. The ldap-server-primary service will be set with a `selectorLabel` matching the leader pod.
1. The Kubernetes Service will use a selector to route traffic only to the leader pod.

### Key Components

- Sidecar Container: Runs alongside the OpenLDAP server in each pod.
- Leader Election Script: Python script using the Kubernetes API to manage leases.
- Selector Labeling: The sidecar will set a `selectorLabel` on the service, matching the leader label when it holds the lease.
- Service Selector: Will be updated to route traffic only to the labeled leader pod.

## Decision Outcome

Chosen option: **Leader Election using Kubernetes Leases API**, because it
provides a more robust and reliable mechanism for leader election and coordination.

### Consequences

#### Positive

1. Improved reliability in leader election and failover processes.
1. Utilization of Kubernetes native mechanisms (Leases API) for coordination.
1. Clearer distinction between `Active-Active` and `Hot-Standby` primaries.
1. Automatic failover to the standby primary in case of leader failure.

#### Negative

1. Increased complexity with the addition of a sidecar container.
1. Potential need for additional permissions for the service account.

### Risks and Mitigations

1. Race Conditions: While not expected with StatefulSet applications, the implementation should be tested for race conditions when multiple pods start simultaneously.
1. Security: The current PoC doesn't consider BSI compliance. This needs to be addressed in the final implementation.
1. Coupling with ldap-notifier: The ldap-notifier system is currently tightly coupled to ldap-primary-0. This coupling needs to be addressed to fully benefit from the new leader election mechanism.

## Alternatives Considered

1. Maintain status quo with ReadinessProbe adjustments and dynamic service routing labels:
   - Rejected due to occasional occurrence of two active replicas and suboptimal custom lock mechanism.
1. Using Coordinated Leader Selection:
   - Rejected due to its alpha state.

## Action Items

1. Develop a proper leader-election Docker image.
1. Refine and structure the leader election script.
1. Address permission for the service account.
1. Implement BSI compliance measures.
1. Review and adjust the coupling between ldap-notifier and LDAP primaries.
1. Conduct thorough testing, including failover scenarios and potential race conditions.

## References

- https://wdmartins.medium.com/active-passive-kubernetes-deployment-for-high-availability-stateful-applications-b7e6fa068944
- https://kubernetes.io/docs/concepts/architecture/leases/#leader-election
- https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/
- https://www.openldap.org/doc/admin26/replication.html
