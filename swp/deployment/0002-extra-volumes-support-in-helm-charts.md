
# Support extra volumes in Helm charts

---

- status: accepted
- deciders: tkintscher, rabdulatipov, jbornhold
- date: 2023-10-09
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/228

---

## Context and Problem Statement

For some types of customization it is useful to mount adjusted configuration
files or custom assets like icons into a container. In Kubernetes this can be
achieved by mounting a `ConfigMap` or a `Secret` into a container or by mounting
a pre-existing `Volume` into a container.

Currently this has to be done by patching the results of using our Helm charts.

Should we add first class support for this pattern?

## Decision Outcome

We add the following configuration options to our Helm charts consistently:

```yaml
# -- Optionally specify an extra list of additional volumes.
extraVolumes: []

# -- Optionally specify an extra list of additional volumeMounts.
extraVolumeMounts: []
```

This way a user of the Helm charts can mount in files as needed into the
containers without having to apply patches.

We orient the design towards common practices and follow the recommendation of
the Sovereign Workplace project for this aspect.

## More Information

openDesk best practice Helm chart:

- https://gitlab.souvap-univention.de/souvap/tooling/charts/opendesk-best-practises

Related Kubernetes reference documentation:

- `Volume` reference: <https://kubernetes.io/docs/reference/kubernetes-api/config-and-storage-resources/volume/#Volume>
- `VolumeMount` reference: <https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/#volumes-1>

Research and implementation related pointers:

- The Spike in which we investigated the options:
  <https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/228>

- The implementation in `common-helm`:
  <https://git.knut.univention.de/univention/customers/dataport/upx/common-helm/-/merge_requests/15>
