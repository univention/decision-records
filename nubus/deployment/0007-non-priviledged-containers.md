
# Containers will run as user `app` with `uid 1000`

---

- status: accepted
- deciders: jconde, jbornhold
- date: 2024-03-13
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/409

---

## Context and Problem Statement

We want to run containers as non-privileged users to reduce the risk of container breakouts.
At the same time, we want to execute containers with read-only access to the host filesystem.

We have seen that running containers with a `uid` that does not exist on the container
leads to containers with username `I have no name!`. At the same time, we have noticed
how `cracklib` fails to run under such scenario, as the non existing `uid` cannot
access the `/etc/passwd` file.

## Decision Outcome

We add a user `app` with uid `1000` to our images and specify this user to run
the production stage of the image. From the helm chart, the uid `1000` will be
specified as the user to run the container.

This will happen whenever possible, but there are some exceptions such as ldap.

User `root` will still be used for the `development` and `test` stages of the image.

### Consequences

- A user with uid `1000` must exist on the container.
- The user will exist in the `/etc/passwd` file of the container

### Risks

Thorough testing is required to ensure that the containers run as expected
with the new user, as well as on the read-only filesystem.

## More information

- The QA that discovered the issue:
  <https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/-/merge_requests/91#note_306668>
- The implementation in the udm-rest-api image:
  <https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/-/blob/b583b5ed5a27fe5d932a8e8e186e5c1906c4e2cb/docker/udm-rest-api/Dockerfile#L272>
- The implementation in the udm-rest-api helm chart:
  <https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/-/blob/b583b5ed5a27fe5d932a8e8e186e5c1906c4e2cb/helm/udm-rest-api/values.yaml#L65>
