# Build distroless base images from UCS sources with Bazel

- status: proposed
- supersedes: -
- superseded by: -
- date: 2026-08-28
- author: Marius Meschter
- approval level: medium (see [approval_level.md](../approval_level.md))
- coordinated with: Team Horizon
- source: [nubus-helm#27](https://git.knut.univention.de/univention/dev/nubus-for-k8s/nubus-helm/-/work_items/27)
  "[SPIKE] Explore distroless images for containers"
- scope: Base images for Python components whose running container needs
  nothing beyond the base image and the files copied in from a build stage.
  Components whose App Center app runs in-container interface scripts
  use the shell variant.
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

Nubus container images are built by installing UCS packages into `ucs-base`,
a Debian root filesystem produced with debootstrap from the UCS apt repositories.
That design is deliberate and it works.
A component that needs a UCS package adds it to a Dockerfile.
The image behaves like a small UCS system,
with a shell for debugging and `apt` for extension at build time.

The cost of that design shows up in the security process rather than at build time.
`ucs-base-python` carries 96 Debian packages,
of which the Python services use a handful.
The rest arrive because debootstrap installs Debian's Essential set,
and because `apt` and `dpkg` bring their own dependencies.
Every one of them is scanned, reported, and triaged.
A Perl interpreter ships inside Python services this way:
nothing declares a dependency on `perl-base`,
it is `Essential: yes` and therefore present by definition.

The question is how to produce a base image
that contains only what a Python service actually needs,
while keeping the packages sourced from the UCS repositories
and keeping the package inventory readable by Trivy and Dependency-Track.

## Decision Drivers

- **Provenance:** Do the packages in the image come from the UCS repositories,
  on the UCS release and errata cadence?
  Who decides what ships, and can that decision be re-derived by a reviewer?
- **Inventory accuracy:** Does the image carry a package database
  that Trivy and Dependency-Track read correctly,
  so that the SBOM describes what is really installed?
  Can every component be traced to a stated reason for its presence?
- **Attack surface:** What can an attacker run inside a container
  after gaining code execution?
- **Maintainability:** What does it cost to add a package,
  to follow a UCS release, or to onboard a service?
  What expertise does the team need, and how many people need to have it?
- **Upstream health:** Is the tooling maintained, permissively licensed,
  and likely to still exist and receive security fixes in three years?
- **CI and operational fit:** Does it run in the existing GitLab CI
  without privileged runners, a Docker daemon, or additional infrastructure?

## Considered Options

- Keep `ucs-base-python` unchanged
- Strip `ucs-base` down inside a Dockerfile
- Buy hardened base images from a vendor
- Use Google's distroless images directly
- Build a sliced root filesystem with Canonical's Chisel
- Assemble the image with a hand-written script over `dpkg-deb`
- Assemble the image with Bazel, `rules_distroless` and `rules_oci`

## Pros and Cons of the Options

### Keep `ucs-base-python` unchanged

Continue to build every Python service on the debootstrap image.

- Good, because it is understood by everyone and needs no additional tooling.
- Good, because a shell and `apt` are available
  for debugging and for build-time extension.
- Neutral, because the image is correct;
  the objection is to its size and its component count, not to its behavior.
- Neutral, because part of it can be removed in place.
  `apt-get remove --allow-remove-essential perl-base gzip diffutils hostname`
  succeeds and keeps the package database consistent.
  It clears the critical findings,
  which is the cheapest fix available
  if the critical count is the only concern.
- Bad, because the CVEs reported against a Python service
  come almost entirely from the base image
  rather than from its Python dependency tree.
  The base image is the only lever on the CVE count for these services.

### Strip `ucs-base` down inside a Dockerfile

Remove packages with `apt-get remove`,
or copy a subset out of `ucs-base` in a multi-stage build.

- Good, because it needs no tooling the team does not already run.
- Good, because a removal made through `apt` goes through `dpkg`,
  so `/var/lib/dpkg/status` stays consistent and the SBOM stays accurate.
- Bad, because it stops well short of the goal.
  Debian's Essential set is interlocked:
  `util-linux` pre-depends on `libpam-modules`,
  so `apt` refuses the transaction that would remove the shell userland,
  and `dpkg --remove dpkg` reports dependency problems.
  The floor is a little over 90 packages, against 25 for a curated closure.
- Bad, because going below that floor means deleting files behind dpkg's back.
  `/var/lib/dpkg/status` then stops describing the image,
  Trivy reports zero operating system packages,
  and the SBOM is wrong while the scan looks perfect.

### Buy hardened base images from a vendor

Buy minimal, maintained base images from a supplier such as Chainguard.

- Good, because it needs no build work,
  and the supplier rebuilds on a published cadence,
  more consistently than the team would manage it.
- Good, because the supplier carries the triage effort
  that this decision is trying to reduce.
- Bad, because the packages come from the supplier's distribution, not from UCS.
- Bad, because the SBOM of every Nubus container becomes a supplier artifact,
  on the supplier's rebuild cadence and CVE policy.
- Bad, because it makes every Nubus container depend on a commercial agreement
  staying in place.

### Use Google's distroless images directly

Use `gcr.io/distroless/python3-debian13` as the base for Python services.

- Good, because it needs no build work
  and is maintained by someone else,
  more consistently than the team would manage it.
- Good, because measurement confirms the quality:
  the image built here reaches CVE parity with Google's,
  the difference being the package versions each archive carried on the day.
- Bad, because the packages come from Debian, not from UCS.
  Nubus images are built from UCS sources,
  and mixing two package universes puts two errata streams in one image.
- Bad, because the SBOM of every Nubus container becomes a third-party artifact,
  on the vendor's rebuild cadence and CVE policy.

### Assemble the image with a hand-written script over `dpkg-deb`

Download the `.deb` files, unpack them with `dpkg-deb -x`,
write a `/var/lib/dpkg/status` file, and tar the result.

- Good, because it introduces no additional toolchain
  and is auditable in an afternoon.
- Bad, because the short script is the smallest part of the work.
  Dependency resolution, Debian version comparison,
  the `status` database format, layer construction
  and deterministic tar ordering are the rest of it,
  and the team would own every bug in them.
- Bad, because that code already exists, is tested, and is maintained elsewhere.

### Build a sliced root filesystem with Canonical's Chisel

[Chisel](https://github.com/canonical/chisel) cuts Debian packages
into file-level slices and installs only the slices a component needs,
so an image can hold part of a package rather than all of it.

- Good, because slicing goes below package granularity,
  which can produce a smaller image than one built from whole packages.
- Good, because the project is active and permissively usable as a build tool
  (AGPL-3.0).
- Neutral, because it is _unknown_ whether Trivy and Dependency-Track
  report a Chisel manifest correctly.
  Until that is measured, the option carries the same inventory-accuracy risk
  that rules out stripping a Dockerfile.
- Bad, because the slice definitions are curated per release in
  [canonical/chisel-releases](https://github.com/canonical/chisel-releases),
  which carries Ubuntu branches only.
  There are no Debian or UCS definitions,
  so the team would write and maintain a slice definition for every package
  instead of listing package names.
- Bad, because a sliced root filesystem holds partial packages.
  Chisel writes its own manifest rather than a dpkg status database.

### Assemble the image with Bazel, `rules_distroless` and `rules_oci`

Resolve UCS packages and unpack them into layers without running `dpkg`,
writing a synthetic `/var/lib/dpkg/status`
so that scanners still find a package database they can read.
Prototyped and measured during the spike.

Only the team maintaining `ucs-base-image` works with Bazel.
Component teams never do.
Adding a package to an image is an edit to a YAML list.
Starlark is touched only when the way an image is assembled changes,
which should be rare.

For a component, the build stage does not change.
It still assembles its virtual environment on `ucs-base-python`
with `apt`, `pip` or `uv`, exactly as today.
What changes is the runtime stage:
it starts from the distroless image, so it cannot run `apt`, `pip` or `uv`,
and `RUN` does not work there because there is no shell.
That stage holds only what the build stage copies into it.

- Good, because packages come from the UCS apt repositories,
  so provenance is unchanged from `ucs-base`.
- Good, because it is the machinery Google uses for its own distroless images,
  pointed at the UCS mirror.
  That project states its images "are built using bazel"
  and that it tracks Debian releases.
- Good, because the SBOM stays correct.
  `rules_distroless` writes the package database that Trivy reads,
  so the inventory describes what is installed.
- Good, because the package list is a reviewable artifact.
  Each of the 25 packages carries a comment stating why it is present,
  and `resolve_transitive = False` means the list is exactly what ships.
- Good, because CI guards the package list.
  `tools/check-drift.sh` resolves the same list with transitive resolution
  enabled and fails when the manifest is missing a dependency,
  so the hand-written closure cannot fall behind without anyone noticing.
- Good, because the build needs no Docker daemon and no privileged runner.
- Neutral, because Bazel is a large tool for a small job.
  It is confined to one directory of one repository,
  pinned by `.bazelversion`, and run inside a published Bazel container image.
  Adding a package means editing a YAML list, not writing Starlark.
- Neutral, because component teams integrating the distroless base image
  do not need to read or write Bazel.
- Bad, because it's not a 1:1 swap against the UCS base-image.
  The already existing Dockerfiles will need modifications
  and an `apt install` in the Dockerfile will not work anymore.
- Bad, because it adds a build system that Team Horizon has not used before.
- Bad, because the default and `-ldap` variants have no shell,
  which removes `kubectl exec` and the `/entrypoint.d/` mechanism.
  See *Consequences*.
- Bad, because a UCS App Center app whose definition ships in-container
  interface scripts (`configure`, `store_data`, `restore_data`)
  needs a shell and a coreutils-equivalent to run them.
  Those components use the `-shell` variant.

### Using the result

The build stage does not change.
A component still builds its virtual environment on `ucs-base-python`,
with `apt`, `uv` or `pip` as it does today.
Only the final stage differs:
it starts from the distroless image, copies the virtual environment in,
and declares an exec-form `ENTRYPOINT`.

```dockerfile
FROM ${UCS_BASE_IMAGE}:${TAG} AS build
RUN uv sync --locked --no-dev

FROM ${UCS_DISTROLESS_IMAGE}:${TAG} AS final
COPY --from=build /app/myservice /app/myservice
ENTRYPOINT [ "/app/myservice/.venv/bin/myservice" ]
```

There is no `RUN` step in the final stage, because there is no shell to run it.
`distroless/README.md` documents the rest:
PID 1 signal handling, probes without a shell, and the checks
to run against a virtual environment before migrating a component.

## Decision Outcome

> **Draft.** The author confirms or replaces this section.

Chosen option: "Assemble the image with Bazel, `rules_distroless` and `rules_oci`",
because it is the only option that satisfies the provenance driver
and the inventory-accuracy driver at the same time.
Vendor and Google images fail provenance,
because the packages come from someone else's distribution.
Dockerfile stripping keeps both, but reaches only about 92 packages.
Chisel would satisfy provenance,
but it has no Debian slice definitions
and its manifest format is untested against our scanners.
The remaining candidate, a hand-written script,
reaches the same place by reimplementing code that is already maintained.

### What the decision produces

One build, one set of manifests, and a family of variants.
A component picks the one its requirements call for.

| variant | contains | for |
|---|---|---|
| default | CPython and the libraries its standard library links | components that need only their own files at runtime |
| `-ldap` | the default, plus `python-ldap`'s native dependencies and krb5 | components that talk LDAP or authenticate with SASL or Kerberos |
| `-shell` | the default, plus `busybox-static` and a symlink per applet | components whose App Center app runs in-container interface scripts, and `kubectl debug` |

The shell variant is part of this decision rather than an exception to it.
It is built by the same rules from the same package lists,
and it stays far smaller than `ucs-base-python`.
Google publishes an image similar like our `-shell` image titled `:debug`.

Arguments below that refer to the absence of a shell
describe the default and `-ldap` variants.

### Sustainability of the chosen tooling

Checked on 2026-08-28.

- `rules_distroless` is Apache-2.0, developed at
  [bazel-contrib/rules_distroless](https://github.com/bazel-contrib/rules_distroless),
  with 36 contributors and 17 open issues.
  Eight releases were published between 2026-03-16 (v0.7.0) and 2026-08-21 (v0.9.4),
  and the last commit was 2026-08-25.
- `rules_distroless` describes itself as beta,
  without a stable public API, while listing production adopters.
  Google's own distroless images are built with it.
- `rules_oci` is Apache-2.0, at
  [bazel-contrib/rules_oci](https://github.com/bazel-contrib/rules_oci),
  last commit 2026-08-28.
- Both live under `bazel-contrib`,
  the community organization that also holds `rules_python` and `rules_go`,
  rather than under a single vendor.
  `rules_distroless` moved there from `GoogleContainerTools`.
- Bazel publishes a major LTS release roughly every 12 months
  and supports each one for about three years.
  Bazel 8, which this build pins, is in maintenance until December 2027;
  Bazel 9 is supported until December 2028.
- The exposure is bounded.
  If either rule set were abandoned,
  what it produces is an ordinary OCI image and a tar file.
  The package list, which carries the decisions,
  is plain YAML and would survive a change of build tool.

### Consequences

- Neutral, because container images are built in at least two stages.
  The first is based on the standard `ucs-base-python`
  and assembles the Python dependencies into a virtual environment,
  using `apt`, `pip` or `uv` as it does today.
  The second is based on the distroless image
  and copies that virtual environment in.
- Good, because the base image drops from 96 to 25 packages,
  and reported CVEs fall by roughly half, with no critical findings left.
- Good, because the image contains exactly one executable,
  `/usr/bin/python3.13`, down from 272.
- Good, because the base image drops from 252 MB to 55 MB on disk,
  and the migrated services roughly halve.
- Good, because the CI cost is unchanged in practice:
  the build takes 125 s, the push 35 s and the drift check 66 s,
  against 64 s to 75 s for each existing `ucs-base` job.
- Neutral, because the few components that run scripts inside their container,
  such as an App Center app's `configure`, `store_data` or `restore_data`,
  can use the variant that ships busybox.
  Most ship no such scripts and stay on the default image.
  An app with all three was installed on a UCS system on the shell variant,
  with each script executing and the UCS CA reaching the container.
- Bad, because there is no shell in the default variant.
  `kubectl exec … sh` no longer works,
  and debugging uses `kubectl debug` with the shell variant.
- Bad, because the `/entrypoint.d/` plugin points decided in
  [nubus/deployment/0001](../nubus/deployment/0001-plugin-points-around-entrypoint-scripts.md)
  cannot work in an image without a shell.
  That record dates from 2023,
  when shell-based customization was the only extension mechanism available,
  and it remains correct for the `ucs-base` images it was written for.
  Distroless images set an exec-form `ENTRYPOINT` pointing at an executable.
  Where configuration templating is needed,
  the short-term replacement is an init container,
  and the long-term one is configuration rendered by the Helm chart
  into a mounted file.
- Bad, because `tini` is gone,
  so the service binary runs as PID 1
  and has to install its own SIGTERM handler and reap orphaned processes.
- Bad, because components that install UCS packages at image build time
  cannot migrate.
  `udm-listener` runs `apt-get build-dep`, builds a `.deb` in the image,
  and drives `univention-config-registry`;
  it needs a package manager by construction.
- Bad, because components whose App Center app ships in-container interface
  scripts cannot use the default variant either.
  They can use `-shell`, or move those scripts to `configure_host`
  or into the service's own startup.
- Neutral, because
  [nubus/deployment/0007](../nubus/deployment/0007-non-priviledged-containers.md)
  is satisfied unchanged:
  the base image declares user `app` with uid 1000 and home `/app`.
  Services built on it inherit that user
  instead of creating a per-service one in a `RUN` step,
  as the images on `main` still do.

### Risks

- A medium risk exists that the curated package list falls behind
  what the services need,
  producing a runtime failure rather than a build failure.
  A missing shared library does not always fail loudly:
  without `libstdc++6`, `import frozenlist` still succeeds
  and silently falls back to a pure-Python implementation.
  The drift check covers dependency completeness, not this class of problem.
- A medium risk exists that Bazel knowledge stays with one person.
  Adding a package does not require it; changing the assembly does.
- A small risk exists that `rules_distroless` diverges from our needs
  or is abandoned.
  The build pins 0.8.0 while 0.9.4 is current,
  so an upgrade path already needs walking.

### Confirmation

- CI builds all three variants and pushes them from the default branch.
- `tools/check-drift.sh` runs on every change under `distroless/`
  and on a schedule,
  and fails the pipeline when the curated closure is incomplete.
- The Nubus end-to-end suite passes with migrated services on these images.
- An App Center app with in-container interface scripts installs and runs
  on a UCS system using the shell variant,
  with its `configure`, `store_data` and `restore_data` scripts executing.
- A reviewer can re-derive the component and CVE figures with
  `trivy image --image-src podman --scanners vuln <image>`,
  and the executable count from the flattened root filesystem
  by classifying ELF headers rather than execute bits.

## More Information

- Implementation and documentation:
  [ucs-base-image!109](https://git.knut.univention.de/univention/dev/projects/ucs-base-image/-/merge_requests/109),
  directory `distroless/`.
- Reference migrations:
  [provisioning!400](https://git.knut.univention.de/univention/dev/projects/provisioning/-/merge_requests/400)
  for the base variant,
  and the `mmeschter/distroless-base` branch of `directory-importer`
  for the LDAP variant.
- Figures come from the [spike write-up](https://git.knut.univention.de/univention/dev/internal/team-horizon/-/blob/09bc7f5f6b871a03b57be855b13fbe4cfdeba5e6/spikes/2026-08-24_distroless-base-images.md), which records the scanner version,
  the vulnerability database timestamp and the method for each one.
  CVE counts move with the database, so this record states directions
  and keeps the dated numbers where they can be re-measured.
  Severity counts differ between Debian and NVD scores,
  so any figure quoted outside the team must name the authority it came from.
  Sizes are those of the flattened root filesystem.
