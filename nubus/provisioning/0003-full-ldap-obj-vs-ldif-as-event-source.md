# Full LDAP object vs. LDIF as the source for UDM events in Nubus Provisioning

- status: accepted
- supersedes: -
- superseded by: -
- date: 2024-06-10
- author: @dtroeder
- approval level: low <!-- (see explanation in template) -->
- coordinated with: @arequate (dev UCS), @dtroeder (arch), @jlohmer (dev Nubus), @steuwer (PM Nubus), @tkintscher (PO Nubus)
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/414
- scope: -
- resubmission: -

---

## Context and Problem Statement

In [ADR 0002 How to propagate changes in the LDAP database to the Provisioning system](./0002-ldap-change-propagation.md) the OpenLDAP overlay (plugin) [slapd-sock](https://www.openldap.org/software/man.cgi?query=slapd-sock) was chosen as the interface to forward LDAP database changes to the Provisioning system.

The OpenLDAP server sends LDIFs to its backends, including _slapd-sock_.

The component running in and near the OpenLDAP server is called the "LDIF producer".
It catches changes to the LDAP database and forwards them to the "UDM Producer".
The "UDM Producer" component runs in the Provisioning system,
receives data from the "LDIF producer",
and converts it to UDM objects,
which it puts into the Provisioning's queueing system.

## Decision Drivers

The most important qualities of Nubus Provisioning are completeness (catching all changes) and correctness (accurate data).

For this decision the qualities simplicity, robustness and scalability were deciding factors.

## Considered Options

1. Forward only the changes to the database (the LDIF) to the _UDM Producer_.
   Let the _UDM Producer_ have a database with the previous state of every LDAP object and its UDM representation.
   It can then calculate the full new LDAP object from the LDIF and the old value and convert that to a new UDM object.
2. Let the UDM library issue pre-read and post-read controls with every database changing request,
   and patch the _slapd-sock_ overlay to receive that data in the RESULT set.
   Then full LDAP objects from before and after the change can be forwarded to the _UDM Producer_.

## Pros and Cons of the Options

### Forward the LDIF to the _UDM Producer_

- Good, because it makes the _LDIF Producer_ component simpler.
- Good, because it does not require to adapt any component of the LDAP server.
- Good, because recording only the LDIF is not affected by differences in the ACL settings of queries to the same object
  (see [ACL 0004 How to handle LDAP changes execute with limiting LDAP ACLs](./0004-handle-LDAP-changes-with-limiting-ACLs.md)).
- Bad, because it requires an additional database for the _UDM Producer_.
- Bad, because mirroring the LDAP objects lifecycle in the _UDM Producer's_ database raises its complexity.
- Bad, because the correctness of the calculation of an object from consecutive diffs is fragile.
  To prevent data corruption there must be no whole in the chain and the order must be correct.

### UDM library issues pre-read and post-read controls

- Good, because it makes the _UDM Producer_ component simpler.
- Good, because at every step of the way,
  all data for the processing is available without depending on previous events.
- Neutral, because the _slapd-sock_ overlay must be adapted anyway,
  so it adds the `entryUUID` and the `entryCSN` to the RESULT data.
- Bad, because a component of the LDAP server must be adapted.
  The _slapd-sock_ overlay must pass on pre-read and post-read data.
- Bad, because for the _slapd-sock_ overlay to receive pre-read and post-read data,
  the respective controls must be added to the requests.
  The UDM library can be adapted to do that, but other LDAP clients won't.
  So changes to LDAP objects by non-UDM software will _not_ be recorded.

## Decision Outcome

Chosen option: "UDM library issues pre-read and post-read controls",
because correctness (accurate data) is a top priority,
and the continued application of diffs can introduce difficult to debug data corruption.

The additional database and a strong dependency on order
raises the complexity of the software and reduces its scalability.

### Consequences

- Good, because all components are as stateless as possible (limited only by their interface/protocol).
- Good, because that makes them easier to debug, maintain and scale.
- Good, because fewer databases reduces operator effort.
- Bad, because depending on pre-read and post-read control means depending on cooperative behavior of the LDAP-using application.
  That means we'll miss changes to the LDAP database by non-UDM software.

### Risks

When implementing the decision,
a risk exists,
that is proportional to the likelihood of LDAP-changing non-UDM software,
that changes to the LDAP database will be missed.
