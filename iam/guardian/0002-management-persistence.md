
# Default Persistence Adapter for Guardian Management API

---

- status: accepted
- date: 2023-08-29
- deciders: J Leadbetter, Johannes Koeniger, Ole Schwiegert
- consulted: UCS@school Dev Team
- informed: UCS@school Dev Team

---

## Context and Problem Statement

The Guardians architecture (ports and adapters) allows for the use of different persistence solutions.
We have to decide on a default, which we develop and ship with the Guardian Management API.
This default adapter will be used and supported in the UCS appliance' app.

The following data has to be persisted by the Guardian Management API: apps, namespaces, roles, contexts, permissions,
role capability mappings, conditions and custom endpoints for the Authorization API.

The Guardian Management API does not load or store any data related to the actors in the domain. This concerns especially
the assignment of roles to entities (users, groups, etc in UDM), which has to be done outside the scope of the Guardian.

**This ADR is more a documentation of the decision, than an in depth analysis of different options.**

## Decision Drivers

- Applicability for both UCS and SWP context
- reliable&stable
- performance
- ease of use

## Considered Options

- UDM
- relational database
- file storage (e.g. json files in a volume)

## Decision Outcome

Chosen option: "relational database", because
they are performant, reliable and widely used. The UCS appcenter can provide a database for any docker app and even
in the SWP it is most likely, that a relational database will be used.

The adapter will be implemented with SQLAlchemy and Alembic to allow for the usage of multiple different database backends,
like mariadb, postgres or sqlite. With alembic stable and reliable migrations can be created that allow for safe and defined
updates to the data structure if needed.

UDM was not chosen because of the following reasons:
- The data contains a lot of relations, which are less intuitive to model in UDM than a relational database.
- Changes to the data model have to be anticipated. Migrations of UDM data is very manual in contrast to relational databases, which provide plenty of mature tooling.
- A relational database allows for easy development and test setups, as we do not rely on a complete UCS environment for our tests.
