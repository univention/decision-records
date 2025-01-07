# LDAP Init-ConfigMap for Safe Database Initialization

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2024-12-19
- author: Carlos García Mauriño
- approval level: medium
- coordinated with: Nubus for k8s Team
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/975

---

## Context and Problem Statement

In a multi-primary LDAP setup with Mirror Mode, we need to ensure that only one instance initializes the LDAP database with the base LDIF. If multiple instances attempt to load the initial data, it could lead to data corruption or inconsistency as newer trees would overwrite pre-existing ones.

This is particularly critical in scenarios such as:

- First, fresh deployment
- Recreation of replicas during upgrades
- Expansion from one to two replicas
- One primary losing all data and restarting
- Both primaries getting killed with one losing its volume

## Decision Drivers

1. **Data Integrity**: Prevent corruption of LDAP data during initialization
2. **Reliability**: Ensure consistent behavior across different deployment scenarios
3. **Scalability**: Support safe scaling operations between one and two replicas
4. **Maintainability**: Track initialization state in a Kubernetes-native way

## Decision Outcome

We implemented a ConfigMap-based tracking mechanism that records whether the LDAP base LDIF has already been loaded in a deployment. This ConfigMap is checked before any initialization attempt.

### Implementation Details

#### StatefulSet Behavior

The solution relies on ordered pod startup sequence in StatefulSets:

- Uses default `OrderedReady` pod management policy
- Ensures pods are created in strictly increasing order
- Only one pod changes state at a time
- Critical for maintaining data consistency during initialization

1. A ConfigMap tracks the initialization state with a key `ldap_database_initialized`
2. Before loading initial LDIF data, the pod checks:
   - If database files exist locally
   - The initialization state in the ConfigMap
3. The ConfigMap is updated to "initialized" after successful base LDIF loading

### Specific Scenario Handling

1. **Fresh Deployment**:
   - First pod creates ConfigMap and loads base LDIF
   - Second pod sees initialized state and skips loading

2. **Replica Recreation During Upgrade**:
   - Pods check ConfigMap and existing database files
   - Skip initialization if either exists

3. **Scale Up (1 to 2 replicas)**:
   - New pod inherits data through replication
   - ConfigMap prevents double initialization

4. **Scale Down (2 to 1 replica)**:
   - Should be done through Helm upgrade
   - Non-leader pod should be removed first
   - If leader needs removal:
     1. Manually delete leader pod to force leadership handover
     2. Wait for new leader to sync data
     3. Proceed with scale down

5. **Data Loss Scenarios**:
   - Pod with lost data will not initialize if ConfigMap shows "initialized"
   - Will instead sync from existing primary

### Consequences

- Good, because it prevents data corruption from multiple initializations
- Good, because it provides a clear state tracking mechanism
- Good, because it handles various failure and scaling scenarios safely
- Neutral, because it requires additional Kubernetes resource (ConfigMap)

### Risks

- High risk when scaling manually with kubectl instead of Helm:
  - The n-way replication configuration would be incorrect as `slapd.conf` wouldn't be updated
  - Service configurations for individual primaries would be misaligned
  - Could lead to data loss or split-brain scenarios
  - NEVER manually adjust the replicaCount of the LDAP Primaries in kubernetes directly
- Low risk that ConfigMap could be accidentally deleted, requiring manual intervention
- Low risk of conflicting data and data-loss because an outdated hot standby becomes the new leader.
  - User foo is modified with a new mail address.
  - The old leader is stopped before this operation is replicated to the hot standby's.
  - On the new leader, User foo is modified with a new phone number
  - The old leader is redeployed and syncs with the cluster. If the modifications had been on different users, both operations would be synced. But since they are on the same user, the operations are in conflict. In this case the entry version with the most recent timestamp will win, meaning the mail address modification will be overwritten by the conflicting and newer phone number change.

### Alternatives

If we want to address the above mentioned risks and get to the next level of reliablility, we should look into creating an LDAP-Server operator.

The leader-elector sidecar container is already half-way towards an operator and there's a limit of how much more we can do with it.

An operator could:

- Always scale down the non-leader pod, avoiding the first risk completel.
- There is no statefulset, where people could manually adjust the replicaCount, leading to an invalid configuration.
Instead there is the CRD Manifest of the LDAP Operator and the Pod Manifests that the Operator creates and manages.
If the CRD Manifest is changed, the LDAP Operator creates a new Pod Manifest **and** changes the slapd.conf to add the new pod to the NxN replication.
- Check the replication status between leader and hot standby and only kill the old leader after the new leader has caught up.
- If the old leader dies unexpectedly, make the most up2date hot standby the new leader, instead of a random hot standby.
- Set an env value to trigger database initialization exactl once on the first deployed pod.

### Known Failure Scenarios

#### Notifier ID Mismatch Scenario

When the primary-0 pod loses its volumes (an uncommon failure scenario), the following occurs:

- The NotifierID stored in the shared volume between `nubus-ldap-server-primary-0` and `nubus-ldap-notifier-0` is lost
- Upon redeployment with fresh volumes, the NotifierID resets to its initial state
- The `nubu-provisioning-listener` still has the old NotifierID in its volumes
- This mismatch causes the listener to fail to connect to the notifier

Example log pattern indicating this issue:

```log
LISTENER    ( WARN    ) : can not connect any server, retrying in 30 seconds
LISTENER    ( ERROR   ) : failed to connect to any notifier
LISTENER    ( WARN    ) : connection to notifier failed (2), retry #n in x second(s)
```

#### Current Limitations and Mitigations

- The listener-notifier system is not highly available in Nubus for Kubernetes deployments
- The long-term solution is the LDIF Producer sidecar container (development currently paused)
- Similar scenarios exist in UCS (e.g., during backup2master), and established recovery procedures exist
- Support teams (Incident, Support, Professional Services) have experience handling manual recovery

### Scale Operations Recommendations

1. **Preferred Approach**: Scale down during periods of no write activity
2. **Alternative Method**: Follow the manual process described in "Scale Down" scenario
3. **Avoid**: Direct scaling with kubectl instead of Helm

### Confirmation

The implementation is confirmed through:

- Integration tests covering initialization scenarios
- Manual testing of scale up/down operations
- Validation of Mirror Mode synchronization after initialization

## More Information

- The ConfigMap is managed by the LDAP container's initialization script
- Scale-down operations should not be initiated during active data modifications (e.g., user imports)
- The configuration is compatible with the Leader Election mechanism used for Mirror Mode
