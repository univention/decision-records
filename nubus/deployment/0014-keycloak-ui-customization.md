# Keycloak UI Customization

---

- status: accepted
- date: 2024-06-24
- author: Carlos García-Mauriño Dueñas
- approval level: low
- coordinated with: Nubus team
- source: <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/614>

---

## Context and Problem Statement

The goal is to enable customers to adapt Keycloak's look and feel to match their design requirements, specifically regarding CSS, logos, and additional links. The challenge is to determine the most efficient and maintainable way to achieve this customization, from the operator's perspective.

## Decision Drivers

- Simplicity
- Maintainability
- Consistency with existing solutions
- Flexibility for future changes

## Considered Options

1. Shared Portal and Keycloak Customization
1. Separate Keycloak Customization

## Pros and Cons of the Options

### Option 1: Shared Portal and Keycloak Customization

This option involves using a shared CSS file for both the portal and Keycloak, as is currently done. Customizations are managed via a ConfigMap as per ADR `0012-portal-branding-customizations.md`.

- **Good, because** it maintains consistency between the portal and Keycloak.
- **Good, because** it is simpler and leverages existing configurations.
- **Good, because** it behaves as it does in the appliance.
- **Neutral, because** it requires managing shared resources which may not always be ideal.
- **Bad, because** any change in the shared CSS affects both the portal and Keycloak, potentially causing unwanted side effects.

### Option 2: Separate Keycloak Customization

This option involves providing a custom CSS file specifically for Keycloak, mounted and served by the Keycloak container. This customization is separate from the portal's CSS.

- **Good, because** it isolates Keycloak customization, preventing any impact on the portal.
- **Good, because** it allows more flexibility for Keycloak-specific customizations.
- **Neutral, because** it introduces additional complexity in managing separate customization files.
- **Bad, because** it deviates from the current shared configuration approach, requiring more effort to implement and maintain.

## Decision Outcome

Chosen option: **Option 1: Shared Portal and Keycloak Customization**, because it simplifies the configuration process and maintains consistency across the platform. The additional complexity and maintenance overhead of separating the customizations do not outweigh the benefits.

### Consequences

- **Good, because** it reduces complexity and leverages existing configuration mechanisms.
- **Bad, because** changes to the shared CSS need careful consideration to avoid unintended impacts on both the portal and Keycloak.

### Risks

- There is a medium risk that changes to the shared CSS may have unintended consequences on either the portal or Keycloak.
- It might be confusing at first to understand how the shared CSS is applied to both the portal and Keycloak.

## More Information

- **Current Customization**: For Nubus Keycloak, the theme CSS, custom theme CSS, favIcon, and logos are set. A shared theme for the portal and Keycloak is served by the portal frontend.
- **Configuration Details**:
  - The keycloak-bootstrap job sets URLs for CSS files and favIcon.
  - Additional links on the login page are configured via the keycloak-bootstrap job and can be managed in the Nubus `values.yml` file.

For detailed information, refer to the source issue.
