# ADR: Managing UCR Values with Helm in Kubernetes

---

- status: proposed
- supersedes: [005 Global UCR in a K8s context](./0005-global-ucr-via-configmap.md)
- superseded by: -
- date: 2024-08-09
- author: @cgarcia
- approval level: medium <!-- (see explanation in template) -->
- coordinated with: Team Nubus
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/739
- scope: in product Nubus
- resubmission: -

---

## Decision Drivers

- Flexibility: The need for operators to modify individual UCR values without changing the entire configuration.
- Consistency: Aligning with Kubernetes and Helm best practices.
- Usability: Improving ease of use for operators and customers.
- Scalability: Allowing for easier management of UCR values as the system grows.
- Future-proofing: Preparing for potential deprecation of UCR interface in favor of proper Helm values.

## Considered Options

1. Keep the current approach (storing entire `base.conf` in ConfigMap)
1. Implement UCR management using Helm values and templates

## Pros and Cons of the Options

### 1. Keep the current approach

- Good, because it's already implemented and familiar to the team.
- Bad, because it lacks flexibility for modifying individual UCR values.
- Bad, because it doesn't align well with Kubernetes and Helm best practices.

### 2. Implement UCR management using Helm values and templates

- Good, because it provides flexibility for operators to manage individual UCR values.
- Good, because it aligns with Kubernetes and Helm best practices.
- Good, because it improves usability for operators and customers.
- Neutral, because it requires updates to existing charts and deployment processes.
- Bad, because it may lead to customers depending on a temporary UCR interface.

## Decision Outcome

We will implement a new approach that allows operators to manage UCR values using Helm, providing a more flexible and familiar configuration method (Option 2).

### Key Points

1. Use a Helm template to transform JSON-style input into UCR representation.
1. Allow overriding individual values through Helm values or CLI parameters.
1. Store default values in the Nubus chart, sourced from stack-data-ums.
1. Move openDesk-specific values from stack-data-swp to openDesk/openCoDE.
1. Implement a merging strategy for user-provided values and defaults.
1. Define a "magic value" to delete keys from the configuration.

## Implementation Details

### Helm Values Structure

UCR values will be configured in the Helm values file under the `configUcr` key:

```yaml
configUcr:
  directory:
    manager:
      rest:
        debug_level: 5
```

This will generate `directory/manager/rest/debug_level: 5` in the resulting `base.conf` file.

### Merging Strategy

- User-provided values will be merged with default values.
- Existing keys will be overwritten by user-provided values.
- A special "magic value" will be used to delete a key: `__DELETE_KEY__`.

  Example:

  ```yaml
  configUcr:
    directory:
      manager:
        rest:
          debug_level: __DELETE_KEY__
    ldap:
      master: someldap
  ```

  This example shows how to delete an existing UCR key
  (`directory/manager/rest/debug_level`) while also setting a new value for
  another key (`ldap/master`).

We decided to merge all configuration into a single file, base.conf. The files
`base-defaults.conf` and `base-forced.conf` are no longer used. These files
previously used the merging logic of UCR. Instead, we now use Helm's
`mustMergeOverwrite` to handle the merging process.

### Helm Template

We will create a Helm template that transforms the `configUcr` structure into the UCR `base.conf` format. This template will handle nested structures and apply the merging strategy.

### ConfigMap Generation

The generated UCR configuration will be stored in a ConfigMap, which will be mounted into the respective containers.

### Special Syntax for Repeating Roots of UCR Settings in YAML

Given that sometimes UCR settings can repeat the root of another setting both
for a value and a dictionary, and YAML doesn't naturally support this, we
introduced a special syntax for simple values. For example:

If there is a UCR setting:

```ucr
a: value
a/b: othervalue
```

In YAML, this would be represented as:

```yaml
a__: value
a:
  b: othervalue
```

## Consequences

### Positive

- Operators can manage UCR settings like any other Helm value.
- Individual values can be changed without modifying the entire configuration.
- Consistent with Kubernetes and Helm best practices.
- Improved flexibility and ease of use for operators and customers.

### Negative

- Requires updates to existing charts and deployment processes.
- May require additional documentation and training for operators.

### Risks

- We don't want to expose the UCR DB to customers because it leads to an explosion of configuration options and, thus, complexity. ATM we have to, so customer use cases can be fulfilled. But in the future, after observing a few customers, UCRVs that customers need will be converted to proper Helm values. Even though the documentation will warn that this UCR interface is temporary, customers may start depending on it. It will then be more difficult for Univention to deprecate it.
