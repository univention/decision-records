
# LDAP index handling

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2025-04-08
- author: Johannes Lohmar, Andreas Kosubek
- approval level: low
- coordinated with: Thomas Kintscher, Daniel Tröder
- source: https://git.knut.univention.de/univention/dev/internal/team-nubus/-/issues/1118
- scope: Nubus for Kubernetes
- resubmission: -

---

## Context and Problem Statement

Sometimes, creating a new index in OpenLDAP or recreating an existing one is necessary.
We must implement a workflow ourselves since OpenLDAP has no solution for listing existing indexes.

Recreating an index can be required when:

- An index is added to the default indexes in an upgrade scenario.
- A customer adds an individual index.
- Adding an index as part of a packaged integration.
  For example, Nextcloud searches for users with the `nextcloudEnabled` flag on the user.
  Having an index on that attribute improves performance for this use case.
  Packaged integrations are usually added after the initial Nubus installation, making manual initial indexing of the existing LDAP data necessary.
- Changes in the LDAP schema of an indexed attribute may also require manually reindexing the LDAP for that attribute.

There is no way to determine which indexes are missing, incomplete, or outdated by looking at the LMDB database or asking slapd.
Thus, we need to do this ourselves.

## Decision Drivers

- Robustness
- Usability
- Maintainability
- Performance
- Implementation effort

## Considered Options

- Just reindex everything that has ever changed since Nubus 1.8 on every pod start.
- State file tracking the database index state.

## Option description

### Just reindex new attributes/indexes added since Nubus 1.8 on every pod start

Only new indexes are configured in the Helm charts. The slapindex command is executed for each of these attributes, each time the pod will be started.

### State file tracking the database index state

All indexes are configured in the Helm charts. Additionally, a state file is created, where we store the state of the attribute equality and the created indexes. Everytime when the pod starts, a diff between the configuration, the schema files and the state file is created and the indexes for all changed attributes are (re)created with slapindex.

## Pros and Cons of the Options

### Just reindex everything that has ever changed since Nubus 1.8 on every pod start

- Good, because little effort is required for the implementation.
- Good, because it is very robust.
- Bad, because the script would run very long, leading to long pod startup times.
  Reindexing a single attribute that many or all objects have set (e.g., `entryUUID`) takes 4 minutes for 200K objects.
  This is for only one attribute. With more attributes, the time rises.
  Over time, Nubus would accumulate more and more attributes to reindex - on each LDAP container creation!
- Bad, because it does not cover schema changes or index changes on existing attributes in Nubus 1.8 by the end user / or a packaged integration.

### State file tracking the database index state

- Bad, because of a higher implementation effort.
- Good, dynamic/configurable approach for all indexes. So it is easy to maintain and has good usability.
- Good, because the script runs only when necessary. This improves the startup time of pods that already have up-to-date indices.
- Bad, because the script's robustness is sub-optimal. OpenLDAP does not support reading the current index state and equality type, and the proposed method is error-prone.

## Decision Outcome

The chosen option is _State file tracking the database index state_, because running the index recreation at every pod start requires an unacceptable amount of time.

We track the LDAP index status in a "state file" next to the LDAP database. We store the attribute name and the index type in it.

If the equality algorithm of an index changes, we must reindex that attribute.
Thus, we parse the schema files for the attributes and the equality entries and store the information in the state file.

Example state file:

```json
{
    "attributes": {
        "univentionObjectIdentifier": {
            "equality": "uuidMatch",
            "schema": "univention-objecttype.schema",
            "indexes": [
                {
                    "type": "eq",
                    "last_index_date": "2025-04-14T08:00:32+00:00"
                },
                {
                    "type": "pres",
                    "last_index_date": "2025-04-14T08:00:32+00:00"
                }
            ]
        }
    }
}
```

The information, which indexes are expected, commes from Helm:

```yaml
global:
  configUcr:
    ldap:
      index:
        eq: univentionObjectIdentifier,...
        pres: univentionObjectIdentifier,...

```

### Open questions

- Should an index, that is not in the list, be deleted?

### Consequences

- The script can also be used to detect and only warn customers about missing or possibly broken indices.
  It could, for example, run in UCS as part of the system diagnosis module.
- A reduced startup time improves the service's MTTR.
