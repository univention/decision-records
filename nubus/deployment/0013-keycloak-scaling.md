# Keycloak scaling

---

- status: accepted
- date: 2024-06-20
- author: jconde
- coordinated with: Nubus Dev Team
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/418

---

## Context and Problem Statement

Keycloak uses Infinispan as a distributed cache to store sessions, users, and other data.
By default, Keycloak uses the Infinispan instances bundled with the Keycloak server,
but it is possible to use an external Infinispan cluster.

What is the best way to scale Keycloak in Nubus?

## Decision Drivers

- We want to scale Keycloak.
- We want to keep the Keycloak instances in sync.
- We want to avoid a single point of failure.
- We want to keep the deployment simple.

## Considered Options

- Use of the Keycloak bundled Infinispan, same as the AppCenter Keycloak App.
- Use of an external Infinispan with Keycloak.
- JGroups discovery mechanism using `DNS_PING` with the bundled Infinispan.
- JGroups discovery mechanism using `JDBC_PING` with the bundled Infinispan.
- JGroups discovery mechanism using `KUBE_PING` with the bundled Infinispan.

## Pros and Cons of the Options

### Use of the Keycloak bundled Infinispan

- Good, because it adds no additional complexity to the deployment.
- Good, because it is the default configuration.
- Good, because it is the configuration used in the AppCenter Keycloak App.
- Bad, because it may increase the traffic between the Keycloak replicas.

### Use of an external Infinispan with Keycloak

- Good, because it allows to scale the Infinispan cluster independently from Keycloak.
- Bad, because it adds complexity to the deployment.
- Bad, because it requires configuration of JGroups discovery in Infinispan, or an operator to manage the Infinispan cluster.

### Use of `DNS_PING` with the bundled Infinispan

- Good, because it is the default configuration provided by Keycloak for the Kubernetes environment.
- Good, because it adds no dependency on external services - since the DNS server is provided by Kubernetes.
- Good, because the Infinispan instances can discover each other to form a cluster.
- Bad, because it may increase the traffic between the Keycloak replicas.

### Use of `JDBC_PING` with the bundled Infinispan

- Good, because it allows to use a database to discover the Infinispan instances.
- Bad, because it adds a dependency on a database.
- Bad, because it may increase the traffic between the Keycloak replicas.
- Bad, because it requires extra configuration for JGroups discovery.

### Use of `KUBE_PING` with the bundled Infinispan

- Good, because it allows to use Kubernetes API to discover the Infinispan instances.
- Good, because it adds no dependency on external services - since the Kubernetes API is provided by Kubernetes.
- Bad, because it requires RBAC (Role-Based Access Control) for the Keycloak pods to access the Kubernetes API.
- Bad, because it may increase the traffic between the Keycloak replicas.

## Decision outcome

We chose to use the Keycloak bundled Infinispan with the `DNS_PING` discovery mechanism.

### Consequences

- Good, because the Infinispan Keycloak replicas will be able to discover each other using the DNS server provided by Kubernetes, using a Headless service.
- Good, because it adds no additional complexity to the deployment.
- Good, because it is the default configuration provided by Keycloak for the Kubernetes environment.
- Bad, because it may increase the traffic between the Keycloak replicas.

### Risks

- The traffic between the Keycloak replicas may increase, needing to keep an eye on the network performance.

## More information

- [Spike](https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/418)
- [Keycloak Caching](https://www.keycloak.org/server/caching)
