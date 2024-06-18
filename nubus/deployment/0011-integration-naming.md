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

We need clearly defined names and terms
in order to work efficiently on the topics of Nubus integration and customisation.

## Considered Options

- Plugin vs **Extension**.

## High level concepts

**(Nubus-)Integration**:
Extends Nubus to integrate it with a third party application or system.
Examples are: OX-Connector, ItsLearning-Connector, MS 365 Connector, Google Connector.

**(Nubus-)Customization**:
Customised extension of Nubus.
Often easier than integration packages.

*Integrations and customisations use the same extension interfaces.
Their differences are functional, not technical.
Integrations and customisations can have passive components (extensions) and
and active components (connectors)

## Extensions

(passive component of the integration/customisation)

**(Nubus) Extension Interface:**.
An interface to extend or customise the functionality of Nubus.
It is implemented by at least one technical component of Nubus.
Examples are: LDAP schema, UDM hook, UDM syntax class, UDM extended attribute,
UMC module, Guardian rules, Portals/* objects, custom.css/svg/png (and many more).

**(Nubus) Extension** (formally Plugin)
A file or set of files that implements **exactly one** *Nubus-Extension-Interface**.

**(Nubus-)Extension-Set:**)
A set of extensions that enable a common use case.
The extensions in an Extension-Set often depend on each other, which is why they
which is why they need to be versioned and packaged as a single artifact.
Examples are Portal extensions, Self-Service extensions,
OX extensions, openDesk extensions.

**(Nubus) Extension Image:**.
OCI / Docker image containing **exactly one** Extension-Set.

**(Nubus-Extension-)Target-Application:
Technical Nubus component that provides Extension-Interface(s).
A Target-Application can provide several Extension-Interfaces
and the same Extension-Interface can be provided by several Components.
(UDM extensions must also be installed in the UMC Container)

## Connectors

(active integration/customisation component)
Connectors are separate and independent technical components,
usually deployed with their own control chart and container image.
The old interface was the Listener module.
The new interface is the Nubus Provisioning HTTP API.
Some connectors, such as the Portal Listener and the Self-Service Listener
are installed by default as part of the core Nubus deployment.
But most, like the OX-Connector, are installed separately and optionally.

Connectors often depend on their respective Nubus extensions.

## Decision Outcome

`Extension` is a better name than `Plugin` for most of these definitions.
