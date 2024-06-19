# Integration and customization naming conventions (Nubus-Extensions / -Plugins)

---

- status: accepted
- date: 2024.06.17
- author: @jlohmer
- approval level: low
- coordinated with: @jbornhold, @ngulden, @dtroeder, @steuwer
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/443

---

## Context and Problem Statement

The Nubus development team has been working on the new provisioning components and interfaces
and is migrating multiple Connectors/Listeners/Consumers to it.

The team is also starting to shift its focus
to the design and implementation
of the extension and customisation interfaces of Nubus.

To continue this work efficiently, we need clear name definitions and conventions.
To avoid misunderstandings within the team and with stakeholders
and to limit the amount of renaming work afterwards.

There is an existing Mediawiki page:
[Univention Nubus/terms and definitions](https://hutten.knut.univention.de/mediawiki/index.php/Univention_Nubus/terms_and_definitions#Packaged_integration)
which defines some common terms for Nubus.
It's a top-down approach from the customer's point of view.

As developers we need additional terms
and further refinement of existing terms
to accurately describe our daily work.

The top-down approach in the Mediawiki pages
is complemented by a bottom-up approach defined in this ADR.
The two approaches need to meet in the middle.

Below are a number of concept descriptions and their proposed/accepted names.
The discussion of naming conventions is inherently self-referential,
The text needs to be updated with the outcome of the decision to remain consistent.
Proposed alternatives are listed below.

### High Level Concepts

**1. (Nubus) Integration**:
Integrates Nubus with a third party application or system.
Examples are: OX Connector, itsLearning Connector, MS 365 Connector, Google Connector.

**2. (Nubus) Customization**:
Customized extension of Nubus.
Often simpler than integration packages.

Integrations and Customizations use the same extension interfaces.
Their differences are functional, not technical.
Integrations and Customizations can have passive components: **3. Extensions** and
and active components: **4. Connectors**.

### Extensions

(passive component of integration/customization)

**5. (Nubus) Extension Interface:**.
An interface to extend or customize the functionality of Nubus.
It's implemented by at least one technical component of Nubus.
Examples are: LDAP schema, UDM hook, UDM syntax class, UDM extended attribute,
UMC module, Guardian rules, `Portals/*` objects, `custom.css/svg/png` (and many more).

**6. (Nubus) Extension Type**:
Unique name for an Extension Interface describing its functionality.

**7. (Nubus) Extension:**
From both a conceptual view and a packaging and deployment point of view,
a Nubus Extension is:
A file or set of files that uses _exactly one_ **Nubus Extension Interface**.

**8. (Nubus) Extension-Set:**
A set of extensions that enable a common use case.
The extensions in an Extension-Set often depend on each other,
which is why they need to be versioned and packaged as a single artifact.
Examples are Portal extensions, Self-Service extensions,
OX extensions, openDesk extensions.

**9. (Nubus) Extension Set Image:**
OCI / Docker image containing _exactly one_ extension set.

**10. (Nubus Extension) Target Application**:
Technical Nubus component that provides Extension Interface(s).
A Target Application can provide multiple Extension Interfaces
and the same Extension-Interface can be provided by several Components.
For example, the UDM Extensions must be installed in both the UDM REST API and the UMC containers.

### Connectors

(active integration/customization component)
Connectors are separate and independent technical components,
usually deployed with their own chart and container image.
The old interface was the Listener module API, used by "Listener modules".
The new interface is the Nubus Provisioning HTTP API, used by "Provisioning Consumers".
Some connectors, like the Portal Provisioning Consumer and the Self-Service Provisioning Consumer
are installed by default as part of the core Nubus deployment.
But most, like the OX Connector, are installed separately and optionally.

Connectors often depend on associated Nubus Extensions.
E.g. a UDM extended attribute and LDAP Schema.

## Considered Options

- Plugin vs **Extension** for everything.
- One extension is a set of Plugins.
- Bundle vs **Set**.
- What is one Extension and what is one Extension-Set
- What parts of the theming and configuration interfaces are extensions?
Which parts are not?
- Connector Listener Consumer what means what?

## Pros and Cons of the Options

### Plugin vs. **Extension** for everything

3 and 5-10 were originally called
`Nubus Plugin *` instead of `Nubus Extension *`.

### One Extension is a set of Plugins

As an alternative to using just Extension or Plugin
we could use both for different contexts.
4. `Extension` (singular)
5. `Plugin Interface`
6. `Plugin Type`
7. `Plugin`
8. `Extension` (singular)
9. `Extension Image`
10. `Plugin Target Application`

- Good because Plugin vs Extension is clearer than Extension and Extension**s**.
- Neutral because from the customer's point of view
he does not install an `Extentension` or `Extension-Set`
he installs an `Integration` or `Customization`.
- Bad because the plural has a different name.
- Bad because we need a common name for **every** extension type.
- Bad because Plugins are a subset of Extension Types,
but there are Extension Types, that are not Plugins.
Plugin is a good name for everything that is Code, like UDM Hook, UMC Module and Guardian rule.
But it's not a good name for for LDAP Schema, LDAP ACL, Data-Loader UDM Object YAML,
portals.css or logo.svg.

### What is one Extension and what is one Extension-Set

Instead of `Extension-Set` we could call one functional collection of extension files
one `Extension`.

- Good because it's a simpler name than Extension-Set
- Bad because it obfuscates that there is not one Nubus Extension interface
but many separate interfaces.
- Bad because one Extension-Set Image packages an arbitrary set of Extension Types

### Bundle vs **Set**

Definitions 8 and 9 were initially called:
`Nubus Extension Bundle` and `Nubus Extension Bundle Image`
instead of:
`Nubus Extension-Set` and `Nubus Extension-Set Image`

### What parts of the theming and configuration interfaces are extensions Which parts are not?

From a bottom-up approach an `Extension` should be everything
that is packaged, distributed and installed in the same way.
Meaning everything that can be packaged into an Extension Image
and installed by running that extension image
as an Extension Loader Init Container.
Described in nubus/deployment ADR 0010-extension-bundles.md

### Connector Listener Consumer what means what?

`Connector` is the existing colloquial name
describing a component that processes Univention events
and pushes to some third party systems.

The legacy technical interfaces for this use case
is the `Listener Module API`.

The new Nubus native interface is the `Provisioning Consumer APIs`.

I propose to keep `Connector` as the common name
for active integration or Customization components.
A `Connector` can either be implemented as a `Listener Module`
or as a `Provisioning Consumer`.

- Good because it uses existing names
- Good because it distinguishes between functionality and interface.
- Bad because the OX-Connector, Microsoft 365 Connector...
contain both active components (connector) and passive components (extensions).
- Neutral because in these scenarios the active component is the important part
and the passive component is just the enabler.

## Decision Outcome

The naming definitions 1 to 10 have been updated to reflect the discussion outcomes
and have been accepted.
