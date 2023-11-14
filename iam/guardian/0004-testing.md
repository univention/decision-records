# Testing Concept for Guardian Backend

---

- Status: Accepted
- Supersedes: -
- Superseded by: -
- Date: 2023-10-19
- Author: UCS@school Team
- Approval level:

---

## Context and Problem Statement

As we aim to deliver high-quality, robust, and reliable software for the Guardian Backend, it's essential we establish a clear and sound testing concept to effectively test our software, increasing our confidence in the system's functionality, performance, and robustness.

## Decision Drivers

- Assuring high-quality software delivery
- Need for verifying system's performance
- Ensuring the API's robustness
- Requirement of integration tests

## Considered Options

- Option 1: Run all tests (unit, integration, e2e, performance) in GitLab pipelines
  The tests will run in the GitLab pipelines, using the existing Docker Compose files for LDAP and UDM created by the Open DES / SWP team:
  
  - https://git.knut.univention.de/univention/customers/dataport/upx/container-ldap
  - https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest
  
  Performance tests will probably take longer, so they can only run on the main branch or manually.
- Option 2: Run unit tests in GitLab pipelines, and all other tests in Jenkins
- Option 3: Run all tests (unit, integration, e2e) in GitLab pipelines and performance tests in Jenkins.

## Pros and Cons of the Options

### Option 1: Run all tests in GitLab pipelines

- Good, because it's easy to set up and maintain
- Good, because it's easy to integrate with GitLab
- Good, because it's easy to run tests in parallel
- Good, because we have fewer points of truth about our tests. The time until tests are fixed could decrease through this.
- Bad, Integration tests will not mirror the actual environment existing on a customer installation (docker containers vs current UCS deployment).
- Bad, there's some uncertainty about the LDAP and UDM Docker images setup and capabilities.

### Option 2: Run unit tests in GitLab pipelines, and all other tests in Jenkins

- Good, because more complex setups can be used which allows us to test the actual environment existing on a customer installation
- Bad, because it's more difficult to set up and maintain
- Bad, because it's not directly integrated with GitLab
- Bad, because it's more difficult to run tests in parallel

## Decision Outcome

Chosen option: "Option 2: Run unit tests in GitLab pipelines, and all other tests in Jenkins", since it doesn't need the LDAP and UDM Docker images, and allows us to test the actual environment existing on a customer installation.

### Consequences

- Unit tests will run in GitLab pipelines.
- Integration tests will run in GitLab pipelines if possible, otherwise in Jenkins.
- E2E tests will run in Jenkins.
- Performance tests will run in Jenkins.
- We need to configure the Jenkins jobs from “scratch”.
- We need to define performance tests.

### Risks

- None known.

## More Information

### Unit Tests

Already exist, and have a coverage of 100%. We will keep the goal of 100% coverage.

### Integration Tests

Already exist but are not currently running automatically. We need to run them on the Jenkins job(s).

Additionally, there should be at least some smoke tests with the supported database backend (PostgreSQL) to ensure that the database connection works.

### E2E Tests

Already exist but are not currently running automatically. We need to run them on the Jenkins job(s).

Additionally, we need to ensure that there is at least one test for each API endpoint that verifies the endpoint's functionality and data models. This is currently the case and it should be kept that way.

### Performance Tests

We need to define performance tests, and run them with a Jenkins job. They should ensure that the performance requirements are met.
