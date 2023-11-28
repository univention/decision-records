
# Container image considerations

---

- status: generally considered a good idea
- deciders: anyone affected
- date: 2023-11-28
- source: https://git.knut.univention.de/univention/decision-records/-/issues/9

---

## Context and Problem Statement

Currently Dockerfile can be located in a variety of different places in relation to the project root:
- `./Dockerfile`
- `./docker/somename/Dockerfile`
- `./docker/${IMAGE_NAME}/Dockerfile`
- `./docker/myfrontend/docker/mfyrontend/Dockerfile`
etc.

Currently images are pushed to registries with different path styles:
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-server:1.2.3`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-server-debug:1.2.3`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-frontend:1.2.3`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-frontent-debug:1.2.3`

A uniform convention for Dockerfile locations and paths on registires should be considered.

## Decision Outcome

TBD, but there hasn't been any pushback so far.

We still need to come up with a solution for child pipelines.

Do we apply the same Dockerfile/imagepath relation to the root of the project or relative to the .gitlab-ci.yml?
See "Risks".

### Consequences

- Good, reduces risk of annoying errors downstream
- Good, further streamlines the use of common-ci
- Bad?, in some cases the build-context (think: workdir of the tool building the image) would be equal to the project root
- Bad, `foo-server/foo-server` looks ugly

### Risks

If applied uniformly the path to an image will be ... well uniform.

In the case of univention portal this would mean the the current:
- `./docker/portal-listener/Dockerfile`
- `./docker/portal-udm-extensions/Dockerfile`
- `./docker/deb-builder/Dockerfile`
- `./docker/wait-for-dependency/Dockerfile`
- `./docker/keycloak/Dockerfile`
- `./docker/portal-server/Dockerfile`
- `./docker/reverse-proxy/Dockerfile`
- `./frontend/Dockerfile`
- `./notifications-api/Dockerfile`

Would have to become either:
- `./docker/portal-listener/Dockerfile`
- `./docker/portal-udm-extensions/Dockerfile`
- `./docker/deb-builder/Dockerfile`
- `./docker/wait-for-dependency/Dockerfile`
- `./docker/keycloak/Dockerfile`
- `./docker/portal-server/Dockerfile`
- `./docker/reverse-proxy/Dockerfile`
- `./docker/portal-frontend/Dockerfile`
- `./docker/notifications-api/Dockerfile`

and
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/deb-builder`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-frontend`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-frontend-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-frontend-test-runner-ui`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/notifications-api`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/notifications-api-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-server`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-server-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-udm-extensions`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/wait-for-dependency`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-listener`

Or:
- `./docker/portal-listener/Dockerfile`
- `./docker/portal-udm-extensions/Dockerfile`
- `./docker/deb-builder/Dockerfile`
- `./docker/wait-for-dependency/Dockerfile`
- `./docker/keycloak/Dockerfile`
- `./docker/portal-server/Dockerfile`
- `./docker/reverse-proxy/Dockerfile`
- `./frontend/docker/portal-frontend/Dockerfile`
- `./notifications-api/docker/notifications-api/Dockerfile`

and
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/deb-builder`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/frontend/portal-frontend`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/frontend/portal-frontend-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/frontend/portal-frontend-test-runner-ui`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/notifications-api/notifications-api`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/notifications-api/notifications-api-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-server`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-server-test-runner`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-udm-extensions`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/wait-for-dependency`
- `gitregistry.knut.univention.de/univention/customers/dataport/upx/univention-portal/portal-listener`

## More Information

### Path of container images in relation to the project root

A decision needs to be made with regard to path to image names.

Currently they differ on single and multiple container projects.

#### Single Dockerfile, single container projects

It is assumed that every project could eventually become a multi-container project.

As such even on a single container project named `foo-server` the path of the image would be:
`gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-server/foo-server:1.2.3`

The Dockerfile should reside at `docker/foo-server/Dockerfile`.

#### Single Dockerfile, multiple container projects

If multiple containers are build from a single Dockerfile the path should follow this naming scheme:
`gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-frontend:1.2.3`
`gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-frontent-debug:1.2.3`

The Dockerfile should reside at `docker/foo-frontend/Dockerfile`.

#### Multiple Dockerfile, multiple container projects

On a multi container project named `foo-portal`the paths of the images `foo-frontend` and `foo-backend` should be:
`gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-frontend:1.2.3`
`gitregistry.knut.univention.de/univention/customers/dataport/upx/foo-portal/foo-server:1.2.3`

The Dockerfiles should reside at `docker/foo-frontend/Dockerfile` and `docker/foo-server/Dockerfile` respectively.

### SouvAP GitLab / other target repositories

Images that are being pushed to the SouvAP GitLab and other target repositories (for example `docker-registry.software-univention.de`) currently are "flattened" to `registry.souvap-univention.de/souvap/tooling/images/univention/SOUVAP_IMAGE_NAME`.

This needs to be changed to incorporate the aforementioned naming scheme.

`registry.souvap-univention.de/souvap/tooling/images/univention/PROJECT_NAME/IMAGE_NAME`.

A deviation of `SOUVAP_IMAGE_NAME` from `IMAGE_NAME` should not be possible.
