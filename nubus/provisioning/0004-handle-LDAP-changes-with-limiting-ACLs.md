# How to handle LDAP changes executed with limiting LDAP ACLs

- status: draft
- supersedes: -
- superseded by: -
- date: 2024-06-03
- author: @dtroeder
- approval level: medium <!-- (see explanation in template) -->
- coordinated with: @arequate (dev UCS), @dtroeder (arch), @jlohmer (dev Nubus), @steuwer (PM Nubus), @tkintscher (PO Nubus)

- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/414
- scope: -
- resubmission: -

---

## Context and Problem Statement

The LDAP overlay [slapd-sock](https://www.openldap.org/software/man.cgi?query=slapd-sock)
is used in the Nubus Provisioning system to capture every LDAP change that a UDM operation causes.
The overlay has been extended to return all pre-read and post-read data for a query,
and UDM has been adapted to set the respective pre-read and post-read controls with every changing operation.

The pre-read and post-read operations are server-internal queries
executed using the original queries user account.
Thus, the LDAP ACLs associated with that account are applied.

If those ACLs restrict the visibility of the changed object attributes,
this leads to incomplete LDAP objects in the pre-read and post-read data.

If another change with more or less restrictive ACLs to the same object happens next or happened before,
seemingly (dis)appearing attributes cannot be distinguished from attributes being (un)set.

## Decision Drivers

The most important qualities of Nubus Provisioning are completeness (catching all changes) and correctness (accurate data).

The complexity, and thus stability and maintainability, of the overall system played a huge role in the decision.

## Considered Options

1. Stateful system handling ACL problem:
   1. Store the previous state of every object in a separate database.
   2. Create a diff of a query's pre-read and post-read data.
   3. Apply the new values of only the changed attributes to the previous object to create the "new" object.
      This circumnavigates the problem of (dis)appearing attributes
      because the ACLs apply equally to the pre-read and post-read queries.
      Thus, the same attributes will (dis)appear in both.
      If their values are unchanged, they will be the same in the pre-read and post-read data,
      and thus not in the diff and not applied to the "old" object.
   4. When a privileged account (unaffected by ACLs) like `cn=admin` is used, apply the whole object.
2. Stateless system ignoring ACL problem:

   The operator configures the accounts for UDM operations using the UDM REST API and the UMC.
   We assume equally privileged accounts will be used, not triggering the described problem.

## Pros and Cons of the Options

### Stateful system handling ACL problem

- Good, because it fulfills the "correctness" (accurate data) quality requirement in case of differing LDAP ACLs.
- Bad, because a separate (clustered) database must be added to the system.
- Bad, because creating the "new" object is complex.
- Bad, because continuously applying deltas raises the chance of corrupted data, defeating the correctness gain.

### Stateless system ignoring ACL problem

- Good, because stateless systems have a reduced complexity, improving stability and maintainability.
- Good, because no extra database is required.
- Good, because we are not creating a solution for a problem that will most likely disappear entirely in the near future.
  We assume that the UDM REST API will soon be the only relevant LDAP client
  using the same privileged account for all operations
  because the Guardian does authorization.
- Neutral, because if the problem happened, it'd be easily observable in the provisioning consumer's data.
- Neutral, because if in the future it turns out the other solution must be implemented, only the "UDM producer" must be adapted.
  That component is well isolated from the OpenLDAP server and the core Provisioning system.

## Decision Outcome

Chosen option: "Stateless system ignoring ACL problem",
because we assume the corner case of different LDAP ACLs does not happen today
and is less likely in the future.

In light of this, we do not want to proactively make the system more complex.

### Consequences

- Good, because less complex system.
- Bad, because of a risk for reduced correctness.

### Risks

- When implementing the decision,
  there is a small risk that the operator configures two users
  with different ACLs for the UDM REST API and the UMC, resulting in incomplete event data.
- The end-user Self-Service is currently based on LDAP ACLs.
  Sometimes, project-specific LDAP ACLs are not designed carefully.
  An end-user may have limited read access to, e.g., OX-related attributes.
  If it changes contact data, the event could miss OX information,
  leading to the OX-Connector removing the user from OX.
- Projects like Phoenix have LDAP ACLs for delegated administration.
  Those may limit a user's LDAP read access in specific scenarios.
  Changes in UMC/UDM could then lead to incomplete event data.

For now, we will take these risks,
document them in a way that is visible to customers,
and focus on implementing Guardian support instead of LDAP ACLs in all these scenarios.
