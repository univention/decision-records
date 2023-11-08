
# Global UCR in a K8s context

---

- status: accepted
- date: 2023-08-11
- author: Thomas Kintscher <thomas.kintscher.extern@univention.de>
- coordinated with: jbornhold, jconde, jlohmer
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/250

---

## Context and Problem Statement

The UCS appliance uses the Univention Config Registry (UCR) to store configuration
in a global layer.

It is described [here](https://docs.software-univention.de/architecture/latest/en/services/ucr.html#services-ucr)
in detail.

This document focuses on the aspects of storing configuration data
and making it available to services.

The following features are not in scope and are not available in the UMS at the time of writing:

- UCR CLI,
- UCR hooks which are triggered by configuration changes.

In a containerized context each container is ideally a self-contained unit,
which is deployed by running a container image.
In order to make UCS services (which rely on the UCR library) work in containers,
the `base.conf` file(s) have to be provided.
At the very least, the file available to the container must contain the keys used
by the service in the container.

## Decision Drivers

- An operator should have the ability to change configuration values using
  K8s configuration methods (e.g. ConfigMaps),
  without rebuilding container images.

- Restarting affected containers manually after a configuration change is deemed
  acceptable for now.

- All UCR variables
  (which an operator might already be familiar with from using the UCS appliance)
  should be configurable.

## Considered Options

- *Exposing container configuration via environment variables.*

  The containers ships with default values for all necessary keys.
  The container entrypoint will then read a set of defined environment variables
  and set the keys in `/etc/univention/base.conf` accordingly.
  Afterwards the actual service starts.

  The variables and their values would be stored as key-value pairs in
  a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/).

  The operator could supply a set of values, e.g. using Helm,
  to fill the ConfigMap.
  Configuration changes would come into effect by re-installing the
  service with a new set of values.

  For testing, the variables can also be supplied using the `environment:`
  section of Docker Compose
  or the `--env` flag of `docker`.

- *Exposing the whole UCR database in a ConfigMap.*

  A ConfigMap has to be installed in the K8s cluster,
  which contains the contents of the `base*.conf` file(s).

  The size of the ConfigMap object must not exceed 1 MiB.

  A container with a need for UCR would mount the
  file from the ConfigMap into its filesystem.

  The operator would adjust settings by installing
  a new version of the ConfigMap
  and then restart the affected services (by hand).

  For testing, the files could be mounted into the container
  using the `volumes` or `mount` options of Docker (Compose).

- *Replacing the UCR library with an alternative.*

  Alternatives could be
  [Univention DCD](https://git.knut.univention.de/univention/components/distributed-configuration-database),
  [etcd](https://etcd.io),
  etc..

  A sidecar container could be used
  which supplies the `base.conf` file on a volume which is shared with the
  container.

  The sidecar would listen to a main configuration service for changes
  and determine when to regenerate its `base.conf`
  and restart the service.

  The operator would use the interface provided by the configuration service
  (DCD, etcd, ...) to adjust settings.

  Alternatively, a UCR drop-in could be developed which reads directly from the configuration service.

## Pros and Cons of the Options

### Environment Variables

- Good, because we only expose those settings as env-vars which have been verified to make sense in a container context.
- Good, because it is clear which set of settings controls a container's behavior.
- Good, because configuration changes automatically trigger a pod restart.
- Good, because it is easy to implement.
- Bad, because the set of settings can be huge.
- Bad, because e.g. new settings provided by the upstream software need to be manually added to the container.
- Bad, because some settings such as lists (`umc/saml/trusted/sp/*`) are difficult to represent as env-vars.
- Bad, because the set of available characters for env-var names is more restricted than for UCR keys.
- Bad, because the container entrypoint writes to the filesystem (unless an init-container is used).
- Bad, because keeping settings consistent across services is not possible.

### Put `base.conf` into a ConfigMap

- Good, because the format of `base.conf` is the same as in the appliance.
- Good, because no translations (e.g. for available character sets) have to be made.
- Good, because all options are immediately available to the operator and the container, with no additional effort.
- Good, because the container's filesystem can be read-only, and the ConfigMap can be a read-only mount, too.
- Good, because settings are consistent across containers.
- Neutral, because it supports three layers of UCR: `base-defaults.conf`, `base.conf`, `base-forced.conf`,
  corresponding to e.g. product-defaults, project-defaults, user-customizations.
- Bad, because upon updates of the ConfigMap the affected services have to be restarted by hand.
- Bad, because it introduces dependencies: the ConfigMap must be available before the container can start.
- Bad, because of additional config effort: The service must know the name of the ConfigMap(s) to mount.
- Bad, because not all options (or combinations thereof) have been vetted in the containerized context.

### Alternative Configuration Database

- Good, because it fits the micro-service pattern of one tool for one task.
- Good, because no translations (e.g. for available character sets) have to be made.
- Good, because the container's filesystem can be read-only.
- Good, because settings are consistent across containers.
- Good, because upon updates of the configuration the affected services could be restarted automatically.
- Neutral, because of some config effort: The container must know the name of the configuration service.
- Bad, because it introduces dependencies: the configuration service must be available before the container can start.
- Bad, because of additional effort to research alternatives and form an architecturally fundamental decision.
- Bad, because of additional implementation effort to replace the existing library.

## Decision Outcome

Going forward we put the `base.conf` in a ConfigMap object.

We ship one ConfigMap with the contents for `base-defaults.conf`,
which we consider the "product" (UMS) defaults.

For the openDesk project, a separate ConfigMap with the contents for `base.conf`,
is considered the "project" default.

The Helm charts offer to supply a third ConfigMap with the contents for `base-forced.conf`
in case customizations are required for CI testing, local development environments, or other purposes.

We started developing the containers with environment variables,
but the number of variables to be supported has grown a lot recently.
We have attempted to automatically map environment variables to keys in `base.conf` but
that was very error-prone and/or ugly due to the differences in available character sets.

The time spent is relatively low because we do not have to modify the upstream UCR library.

### Risks

- There is a neglible risk that the configuration file grows to more than 1 MiB.
- Not all UCR settings known from the UCS appliance are useful for the containerized stack:
  some may have no effect at all,
  others may cause breakage.
  The number of settings and combinations is too large to test,
  hence we only provide sets of tested product- and project-defaults for now.
