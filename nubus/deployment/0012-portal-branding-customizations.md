# Portal branding and theming customizations

---

- status: accepted
- deciders: jconde, aniemann, tkintscher
- date: 2024-06-18
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/665

---

## Context and Problem Statement

The Portal branding and theming customizations are currently shipped with the `stack-data` repository and Helm chart.
This Helm chart creates ConfigMaps that are mounted onto the `portal-frontend` with the necessary files for the branding and theming customizations.

How should we handle the customizations of the portal branding and theming?

## Decision Drivers

- We want to allow customizations of the portal branding and theming.
- Currently we ship customizations for the favicon, css, background image and loading animation.
- We want to allow the operator to customize these items.
- We want to allow the operator to add more customizations.

## Considered Options

### Use of MinIO and custom ingress paths

Place all these items in a MinIO custom folder and add necessary routes to be claimed by MinIO and not by the portal.
The custom folder inside the bucket would be publicly accessible.

Good, because it allows for hot-reload of the customizations.  
Bad, because it requires additional configuration on MinIO.  
Good, because it allows for retro-compatibility with the debian package for the UCS appliance.  
Good, because it allows for the operator to add more customizations.  
Good, because it allows for the operator to point items in the `custom.css` to MinIO or any other location.  
Bad, because it requires an additional job to provision the custom folder.  
Bad, because it might pose a security risk if operators misuse it.  
Bad, because it needs adding paths on MinIO.  
Good, because it uses existing infrastructure.  
Bad, because we still need to provide the assets in some way.  

This option could allow `custom/*` to be filled with nubus theme by default if the items are not overwritten in the provisioning job.

### Use of ConfigMaps

The operator could mount ConfigMaps containing these assets. They are mounted into the `portal-frontend`. This is similar to the current approach, only that the ConfigMaps are created by `stack-data`.

Good, because it allows shipping of default Nubus and custom configurations.  
Bad, because it does not allow hot-reload of the customizations unless they are mounted as a directory instead of files.  
Bad, because ConfigMaps can only contain up to 1 MiB of data stored.  
Bad, because updates in ConfigMaps ship an annotation with the previous state in JSON. Thus, updates of the ConfigMaps would fail. It can be avoided by using server-side apply.
Good, because it allows the operator to add more `extraVolumes` and `extraVolumeMounts` to the `portal-frontend` to add more files.  

### Use of publicly available customizations

The operator could provide links to resources that are publicly available, and some form of initContainer loads them in the correct place.

Bad, because it requires the operator to provide the links.  
Bad, because it places the burden of hosting the files on the operator.  
Bad, because we need a `initContainer` to download external files, which can be a security risk.  

## Decision Outcome

We will provide and support the use ConfigMaps in the `portal-frontend`, since for most of the other options there is still the need for some way of provisioning of the customization files.

As such, these customizations are set to be removed from the `stack-data` repository.

In the documentation we will point the operator to the 1 MiB size constraint.

### Consequences

Good, because we allow and support customizing the favicon, css, background image and loading animation.  
Bad, because we provide files as ConfigMaps - which makes sense for string data - but not for a favicon.  
Good, because we still allow the operator to point items in the `custom.css` to MinIO or any other location.  
Good, because the operator can still add more `extraVolumes` and `extraVolumeMounts` to the `portal-frontend` to add more files.  

### Risks

- ConfigMaps can only contain up to 1 MiB of data stored.
- Updates in ConfigMaps ship an annotation (`kubectl.kubernetes.io/last-applied-configuration`) with the previous state in JSON. Thus, updates of the ConfigMaps would fail.
- Charts must be smaller than 1M because of the storage limitations of Kubernetes objects. [Source](https://helm.sh/docs/chart_template_guide/accessing_files/).

## More information

- https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/#how-to-create-objects
- https://helm.sh/docs/chart_template_guide/accessing_files/
