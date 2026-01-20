# Versioning of APIs and artifacts

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2023-11-29
- author: @dtroeder
- approval level: "medium": The approval of the product owner is requested and the decision is made jointly.
- coordinated with: @arequate, @jbornhold, @dtroeder, @fbest, @jkoeniger, @jleadbetter, @ngulden, @phahn, @steuwer
- source: https://git.knut.univention.de/univention/requirements-management/-/issues/246
- scope: All Univention software products starting with UCS 5.2-0.
- resubmission: -

[[_TOC_]]

## Context and Problem Statement

We create a lot of APIs: Python APIs, CLI arguments, Web APIs, UCR variables etc.
Those APIs are comprised of a syntactic part (the signature) and a behavioural part.
Users of our APIs depend on the stability of both parts.
Users of our APIs also expect them to evolve.
Versioning can be used to handle this contradiction.

We also put version labels on artifacts like Debian packages, Docker images, Helm charts, Git commits
and App Center apps.

Versioning of APIs and artifacts serves multiple goals in all stages of its lifecycle:

- The version communicates a state of the API or artifact with a set of features to the customer, the
  user and a software client.
- Version _changes_ are used to communicate how an API or artifact changed, for example a bug fix, an
  added feature, or a breaking change.
  - This is important for customers so that they know what to expect from a new version and if they need
    to adapt.
  - It's also important for the developing team, to validate whether new tests were written for new or
    deprecate features, bug fixes etc.
- Knowledge of the version(s) is required in support scenarios for problem reproduction.
- The support of multiple versions of an API is a way to evolve it without affecting apps and other third
  parties who aren't able to make the switch right away.

## Decision Drivers

- **Stability**:
  - Customers, users, and software clients expect a product to be "stable". That encompasses all
    functional and non-functional attributes and qualities that it offers. For an API this doesn't only
    mean the APIs signature but also includes behavior, side effects, performance etc. "Stability" is a
    hard requirement, because customers base long-term investments upon it.
  - But both customers and Univention also want software to evolve. That requirement is _detrimental_
    to the stability expectation.
  - To resolve this contradiction, a "contract" can be made between the provider of an API or an artifact
    and its user:

    a) The stability of the product will only be guaranteed for a certain version range.

    b) The stability guarantee can be softened a bit by allowing a limited set of non-breaking changes
    like security fixes.
- **Documentation**: When a software gains new features, those and their use must be documented. But not all
  users of that software will switch to the new release at the same time. Thus, it's necessary to
  mention different states of the software with different features and behaviors in the documentation.
  This is usually done by referencing a version.
- **Compatibility**: Software clients break if the signature or behavior of an API changes in an incompatible
  way. As the operators of software clients and APIs may not be the same, clients must be created in a
  robust way. That means, that they need a way to determine if it's safe to use an API.
- **Standardization**: As software developers and vendor we should use a notation for versioning that is
  widely accepted (and serves our purpose). That will reduce misunderstandings and improve development
  speed.
- **Dependency resolution**: Software dependencies should not be too strict or too loose. Clients depend on  
  promises an API makes. If dependencies are too strict, development is hampered. If dependencies are too
  loose, the API may change in a way that destabilizes the client. A desirable expression has been found,
  when the API is allowed to evolve, as long as it doesn't break its promises to the software client.
- **Customer relations**: A product name and its version string should motivate customers to buy or switch
  to the new version.
- **Modularity**: To support reusability, scalability, testability and distributed development, software is
  developed as multiple components. Those components have borders, which form APIs. As components evolve,
  compatible and incompatible combinations arise. To build a stable software product, compatible releases
  of all of its parts must be combined. To describe such a recipe, an API and package versions are used.
  The more modular a software is, the more it depends on proper versioning.

## Considered Options

- **Semantic versioning** ([SemVer](https://semver.org/)): `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`
  - MAJOR version when you make incompatible API changes
  - MINOR version when you add functionality in a backward compatible manner
  - PATCH version when you make backward compatible bug fixes
  - A pre-release version MAY be denoted by appending a hyphen and a series of dot separated identifiers
    immediately following the patch version.
  - Build metadata MAY be denoted by appending a plus sign and a series of dot separated identifiers
    immediately following the patch or pre-release version.
- **UCS Debian package versioning** ([dev-handbook](https://univention.gitpages.knut.univention.de/dev/internal/dev-handbook/packages/build.html#version-number-scheme)): `A.B.C-D`
  - A: For every minor and major release of UCS, increment this number `A`. Reset `B` and `C` to `0` and
    `D` to `1`.
  - B: This number `B` is always `0` for UCS releases. Only increment it for customer specific
       modifications, so that official updates that aren’t minor or major release don’t overwrite the
       customer specific modifications.
  - C: You must increment this number `C` during the preparations for a patch level release. Reset `D` to
    `1`.
  - D: For every errata release after a UCS patch level release, you must increment this number `D`.
  - This schema differs from the version schema in Debian GNU/Linux. The upstream version defines
    `A.B.C`. Increase `D` for each Debian specific change in the directory `debian` of the package.
- **Free versioning**: `XP 3001`
  - An unrestricted combination of letters, numbers and special characters is chosen.

## Pros and Cons of the Options

### Semantic versioning

- Good, because widely accepted in the development community.
- Good, because well documented ([semver.org](https://semver.org/))
- Good, because SemVer allows automatic dependency management.
- Bad, because SemVer may not be compatible with the requirements of sales, public relations or product
  management for the highest-level artifacts like apps and products like UCS and UCS@school.

### UCS Debian package versioning

- Good, because using this schema, the forking of a UCS Debian package for a customer and preventing it
  from being overwritten by regular updates, has successfully been practiced in the Univention
  development department.
- Bad, because it differs from the regular Debian versioning schema.
- Bad, because it doesn't convey any sense of the impact of a change.
- Bad, because UCS Debian package versioning may not be compatible with the requirements of sales, public
  relations or product management for the highest-level artifacts like apps and products like UCS and
  UCS@school.

### Free versioning

- Good, because it allows sales, public relations and product management to choose the version string
  that will lead to the most customer upgrades. The earlier customers upgrade the less maintenance work
  has to be done. This also produces the best economical outcome. A steady flow of income is important to
  ensure future development.
- Bad, because it doesn't convey any sense of the technical impact or realizes any of the other
  qualities in section "Decision Drivers".

## Decision Outcome

Chosen option(s): "Semantic versioning (SemVer)" for all APIs and artifacts, except a) UCS Debian
packages with release specific build-time dependencies, like Python C-extensions or other compiled
binaries and b) highest-level artifacts like apps.
Rationale:

- SemVer is the de facto standard for software development today. It fulfills all the above-mentioned
  requirements except handling differing architecture-dependent binary data in artifacts created from the
  same source code and PM/PR needs.
  - SemVer is used for pure-Python, pure-shell and configuration-only Univention Debian packages.
    Customer specific modifications ("forks") are supported using "apt pinning", instead of limiting the
    use of the `MINOR`/`B` version component. The rule for `B` is not applied. See the proof of concept
    evaluation [apt-pinning.md in the research-library](https://git.knut.univention.de/univention/dev/internal/research-library/-/blob/main/personal/dtroeder/apt-pinning.md).
- "SemVer with extension" (for UCS Debian packages with release specific build-time dependencies) is
  SemVer with two additions: The rules of "UCS Debian package versioning" for `A` and `C` are _added_ to
  the rules for `MAJOR` and `MINOR`:
  For every minor and major release of UCS, increment the `MAJOR` version.
  For every patch level release, increment the `MINOR` version.
  According to SemVer those version increments are unnecessary, but we'll have to compromise.
  - This schema ensures that packages can be updated independently in different UCS versions.
  - Please note that the SemVer rules for the `MAJOR` version still apply. That means, that if breaking
    changes are introduced, it can be raised without a UCS release. In a corporate Linux distribution
    this is not expected to happen, especially not on an old version. This would introduce the risk of
    overtaking a version in a newer UCS release.
  - Please note, that the versions of the APIs of software _inside_ a Debian package are still subject to
    regular SemVer and are _not_ changed during a minor and major release of UCS.
  - Please note, that when Univention software is distributed in Debian packages and does not bear a
    version of its own, then the software's version is assumed to be the same as the package version.
- "Free versioning" for the highest-level artifacts (apps and top-level products like UCS and UCS@school)
  sales, public relations and product management may decide on a different versioning schema. They are
  advised to employ a compatible schema though:
  - Versions should have a numerical component.
  - Newer releases should have a numerically higher version string.
  - Compatibility breaking changes or removal of features should lead to an increased top-level number.
  - The "free versioning" schema is for the _non-technical_ artifact: The "business product", used for
    communication on a high level.
    It will most often be accompanied by one or more _technical_ artifacts: A Debian package, Docker
    image, Git tag, Debian repository, Helm chart etc.
    Technical artifacts must use SemVer or SemVer with extension.
    A "free" version may refer to a range of technical versions and artifacts.

### Consequences

- "SemVer" as the default for APIs and artifacts (including UCS Debian packages):
  - Good, because it's the de facto standard for software development today, so the expectations of
    developers and operators are met.
  - Good, because it lowers the onboarding barrier for new team members, be they freelancers or new
    colleagues.
  - Good, because then Univention handles their Debian packages the same way Debian does.
  - Bad, because the apt "pinning" or "holding" mechanisms have to be introduced in customer projects for
    customer forks.
    Those mechanisms are less transparent than the current one. They will probably also require some sort
    of pre-update test before minor and major UCS upgrades, to prevent blockages.
    A [proof of concept](https://git.knut.univention.de/univention/dev/internal/research-library/-/blob/main/personal/dtroeder/apt-pinning.md) shows how to
    implement this.
- "SemVer with extension" for UCS Debian packages build-time dependencies (C sources):
  - Good, because it conveys the same meaning as regular SemVer _during_ a UCS release cycle.
- "Free versioning" for top-level products:
  - Good, because if there are no technical dependencies, there is no reason to limit the freedom of
    choice.

### Risks

<!-- It's OK to repeat points from the above "Cons of the Options". -->
<!-- Maybe use "Risk storming" to identify risks. -->

- If _breaking_ changes were allowed to happen in a minor/errata release, a version in a previous UCS
  release could overtake the version in a later release.  

### Confirmation

- "SemVer" as the default: Compare the version differences of public and private APIs, Python packages
  etc. and look at the code changes (with Conventional Commits this can be automated). Have feature
  additions lead to raising the `MINOR` version etc.?
- "SemVer with extension" for UCS Debian packages: Read the `debian/changelog` of packages and evaluate
  if the package versions were raised accordingly.
- "Free versioning" for top-level products: no validation needed.

## More Information

### Git repository tags

If a Git repository contains only one project or artifact, then the commit from which a release was
produced should optionally be tagged with the same version that was used for the released thing.
Prefixing with `v` is allowed but discouraged (see [SemVer](https://semver.org/#is-v123-a-semantic-version)).

If a Git repository contains multiple projects or artifacts, then tags should also be used for releases.
The version should however be prefixed with the project's or the artifact's name, separated by an
underscore.

### Artifact types

Non-exhaustive list of artifact types:

- Helm Chart
- Docker image
- Software library
  - Debian package
  - pip package
  - node package
- Service (middleware, backend)
- App (Frontend, UCS App Center app)
- Documentation related to one of the above-mentioned artifacts

#### Artifacts containing exactly one software

If an artifact is used to distribute exactly _one_ software, such as a library or a service, the version
of the artifact, like for example Helm chart, Docker image, Debian or Python package, should be the same
as the one of the packaged software. This makes it easier to recognize the content.

But, if the artifact does a significant environment-dependent setup, then it's probably better to give it
its own version. If, for example, the simplicity to configure a service is increased, then the version of
the Docker file or Debian package should be increased, even if no change was done to the service's code
at all.

In such cases consider moving the artifact and its creation code into separate repositories per
environment.

#### Semantic Version interpretation per artifact type

- Helm Chart
  - Major: Removing, renaming of `values.yaml` attributes or attributes in configmap and secrets.
  - Minor: Adding and deprecating `values.yaml` attributes or attributes in configmap and secrets,
    provisioning of new infrastructure features (ingress, etc.).
  - Patch: Version changes in dependencies (charts, images).
  - Please note that a Helm charts `version` attribute isn't the same as `appVersion`. The `appVersion`
    is about the software to publish and can be used as tag for the main Docker image. The version of
    the Helm chart itself is in `version`, and is what we're talking about in the context of this ADR.
- Docker images
  - Major: Removing, renaming environment variables, major version jumps of the primary application
    service.
  - Minor: Adding and deprecating environment variables, minor version jumps of the primary application
    service.
  - Patch: Version changes in dependencies (base image, libs, packages, app build), bugfixes of the
    images itself (entrypoint scripts, etc.).
- Software library
  - Major: API changes (removed, renamed).
  - Minor: Feature added, something added to the API, deprecated API feature.
  - Patch: Bugfix, dependency update.
- Service
  - Major: API changes (removed, renamed), major business logic changes.
  - Minor: Feature added, addition to the API, deprecated API feature.
  - Patch: Bugfixes, dependency update.
- WebApp / App Center App
  - Major: Product Management driven - bigger redesigns and changes in underlying technology, user
    experience changes.
  - Minor: Features added, changes, improvements.
  - Patch: Bugfixes.

No version change is necessary, when the versioned thing is not changed.
That happens for example, when only tests or linters are changed.
Changes to CI/CD are versioned, when they change the produced artifact.
No change is required, when they change only the how linters or tests are executed.

### Dependencies

To reliably (re)create the same system multiple times, exact versioning of all its components and
dependencies is necessary.

#### Notes on dependencies per artifact type

- Helm Chart
  - Defined directly in the Helm chart.
  - Locked by `Chart.lock`.
- Docker image
  - Defined in the `Dockerfile`.
  - The `FROM` reference can be used with a hash instead of a version to ensure that the image wasn't
    changed at the repository. A comment with the human-readable version should be added in that case.
  - A package manager should be used for external source dependencies, instead of installing it using
    a shell command, for example use `requirements.txt` instead of `pip install ...`).
  - When a dependency is retrieved from an external source during the build, it isn't guaranteed that
    every time the same content is received, unless a hash exists for comparison.
  - Entrypoint related files and scripts are versioned together with the Docker image.
- Software library
  - Debian package
    - No lock mechanism: no way to prevent updates of dependencies.
    - Versioning schema of Debian and UCS differ.
    - Best way to provide UCS Python libraries is by using Python packaging: Host it in a PyPI compatible
      repository and provide it to the consumers as Debian package and via `pip` to Docker images.
  - pip package
    - `requirements.txt`: no lock file, but `pip freeze` exists to track versions.
    - [pipenv](https://pipenv.pypa.io/): uses the [Pipfile](https://github.com/pypa/pipfile)
      format (TOML syntax) and `Pipfile.lock` as a replacement for `requirements.txt`, which is directly
      supported by `pip`, to track the versions of all dependencies. `pipenv` is an official
      [PyPA Project](https://packaging.python.org/en/latest/key_projects/#pipenv).
    - [poetry](https://python-poetry.org/):  uses a
      [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/) file,
      which is directly supported by `pip`, for dependency configuration. Allows to define Python
      versions. Tracks the versions of all dependencies in `poetry.lock`. Dependency resolution can take
      a long time.
    - `poetry` is preferred, because in Univention development experience exists.
  - node package
    - `npm` or `yarn` can be used.
    - Lock file available: `package-lock.json` or `yarn.lock`.

#### Dependency updates

The availability of updates for a project's or artifact's dependencies should be automated wherever
possible using software like `Dependabot`, `Renovate` etc.

### Apt Pinning

There is a proof of concept with copy and pastable commands for using apt-pinning available at
https://git.knut.univention.de/univention/dev/internal/research-library/-/blob/main/personal/dtroeder/apt-pinning.md
