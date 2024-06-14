
# Extension bundles for Nubus

---

- status: accepted
- date: 2024-06-14
- author: jbornhold, jlohmer
- approval level: low
- coordinated with: Nubus Dev Team
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/443

---

## Context and Problem Statement

Various components in Nubus do have an existing mechanism to load extensions.
This mechanism has been inherited from the UCS applience. So far the extensions
have been added directly into the images at build-time. This did only work
because the set of needed extensions for the context of openDesk was known at
build-time. This approach was a decision taken end of 2023, it allowed the
development of Nubus to first focus on having the stack fully containerized.

Now we want to allow to configure a list of extensions at deployment-time, e.g.
by specifying the desired extensions through the values of the Nubus Helm chart.

How should extension for Nubus look like?

## Decision Drivers

- We want to keep compatibility with the current extensions in UCS and avoid a
  bigger refactoring need in the first step.
- The distribution of artifacts shall use the established path of container
  images.
- We have a preference for keeping the possibility to put extensions in at build
  time. This is because we are not certain that all users are fine with the
  shuffling of code through volumes at run-time.

## Considered Options

- Allow extensions only via network based APIs
- Place extension code into container images which have a loader script
- Have a loader download and unpack extensions, possibly from a container image
- Use the existing mechanisms to distribute code through the LDAP directory

## Pros and Cons of the Options

### Extensions only via network based APIs

- Good, because it avoids shuffling any code around at runtime.
- Blocking bad, because we would have to do major changes to all components
  which support extensions.

### Place extension code into container images which have a loader script

- Good, because the upstream components do not need any change for this.
- Good, because this is compatible with bundling extensions at build-time.
- Good, because extension bundles are based on container images.
- Good, loading an extension is a simple copy operation in the file-system.
- Good, because we don't have to build any additional active components
- Bad, shuffling code around at run-time may be unwanted by users.

### Have a loader download and unpack extensions

- Good, because extensions can be packaged in any container format, e.g.
  container image or ZIP file.
- Bad, because we have to build a loader component with logic for download,
  verification and unpacking of the artifacts.
- Bad, because we introduce an additional path of artifacts into the deployment
  which may not be compatible with a user's internal policies.

### Distribute extensions via LDAP

- Good, because we use an existing mechanism.
- Bad, because we would have to adapt extensible containers so that they can
  receive the code.
- Bad, because we would have to add listeners for the changes through the LDAP
  directory.
- Bad, because we would have to implement a reloading mechanism for the affected
  containers.

## Decision Outcome

We chose the option to place extension code into container images which have a
loader script.

During the investigation we found that this pattern is successfully applied in
public charts like Bitnami's Nginx chart and the Helm chart of Velero. An
experimental implementation has shown that this approach does also work in the
Nubus context.

### Current view on the structure of the images

```text
# The plugin loader "API"
/bin/loader

# The sources SHOULD BE in a well known place
/plugins/{plugin-type}/

# The target paths are part of the loader "API"
/target/{plugin-type}/
```

### Current view on the "loader API"

There must be an API contract around the plugin loader.

#### Calling the loader

The plugin loader will be called as executable via the following path:

```text
/bin/loader
```

The usage of `stdin`, `stdout` and `stderr` is not specified. It may be that we
will define this if a need arises to put further customization in.

#### Target paths

The target paths are fixed and defined according to the following schema:

```text
/target/{plugin-type}
```

The plugin loader has to place the assets per `plugin-type` into the respective
target folder.

#### Source paths

These SHOULD BE set up according to the following pattern:

```text
/plugins/{plugin-type}
```

### Conclusion

A specific definition of the extension structure will have to be added into the
Nubus manual. This work is planned at
https://git.knut.univention.de/groups/univention/-/epics/756 and shall take
benefit from the implementation of the first internal extensions.

This decision is considered to be a transitional step. Additional efforts will
have to be taken to develop a target architecture for a cloud-native extension
mechanism. This is out of scope of this decision.

## Consequences

- Good, this extension concept is compatible with the current extensions in UCS.
- Good, because the implementation can be done without a need for any upstream changes.
- Bad, because the loader inside of the extension is not under our control.

## Risks

During the presentation of the approach within the Nubus Dev Team we found two
related aspects which need special consideration.

### The loader is not under our control, how can we handle required changes?

An alternative approach could be to mount a loader into the extension bundle and
then run it inside. This would cause new challenges though, since we would
require either a strictly fixed structure of the sources within the extension
bundle or additional meta-information so that the loader can find the sources.
Also the loader would have to be a static binary or we would have to make
additional requirements about the content of the extension bundle, e.g. a
specific shell to be present.

We assume that the taken approach can be extended in a way so that the loader is
not in the extension bundle anymore, this is why we consider the risk of taking
the simpler approach for the first step to be low.

### How can changes in the extension mechanism be handled?

There are various scenarios how extensions in the context of Nubus can evolve:

1. Changes in the approach itself, e.g. implementing support for extensions
   purely based on network APIs.

2. Incompatible changes, e.g. renaming `/bin/loader` or changing the pattern in
   the target folder structure.

3. Compatible changes, e.g. adding a new plugin type.

### Conclusion

Both stated Risks can be handled if there is a mechanism to carry the
information that an extension does adhere to a specific version of the API or
the mechanism itself.

This information has to be present at deployment-time, because the list of
active extensions is defined at deployment-time.

This can be accomplished by adding a version specific new element into the
configuration values of the Nubus helm chart as illustrated in the following
example:

```yaml
extensions:
  - extension-a
extensions_v2:
  - extension-b
```

## More information

Further details have been captured into the Nubus Infocenter and can be found in
the following place:
<https://git.knut.univention.de/univention/internal/nubus-infocenter/-/tree/main/topics/extensions?ref_type=heads>
