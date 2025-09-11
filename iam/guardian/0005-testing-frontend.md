
# Testing Concept for Guardian Frontend

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2023-11-03
- author: UCS@school team
- approval level: low
- coordinated with: {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- scope: -
- resubmission: -

---

## Context and Problem Statement

We want to make sure the Guardian frontend supports all expected use cases.
Tests are a way to document those, make sure they are robust and performant, and prevent future work
from affecting already published features.

To reveal untested code path we also want to add code coverage to the tests.

## Considered Options

1: Which end-to-end test framework to use
- Option 1.1: Playwright
- Option 1.2: Cypress

2: Which Unit test framework to use
- Option 2.1: Vitest
- Option 2.2: Jest

3: What test type is preferred
- Option 3.1: Only use end-to-end tests against production environment
- Option 3.2: Only use end-to-end tests with mock data
- Option 3.3: Use both end-to-end tests with mock data and production environment

4: Do we use unit tests
- Option 4.1: Code paths that can be tested with end-to-end tests should be tested that way
- Option 4.2: If an end-to-end test exists for a code unit, additional unit tests are allowed for that path
- Option 4.3: Code paths may be tested by unit test only

5: Where do tests run
- Option 5.1: All tests run in GitLab pipelines
- Option 5.2: Run end-to-end tests against production environment in Jenkins and the rest in GitLab pipelines

## Pros and Cons of the Options

### Option 1.1: Playwright

- Good, because it's already used for other product parts ([ADR](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0001-playwright-for-ete-testing.md?ref_type=heads))
- Good, supports test coverage

### Option 1.2: Cypress

- Good, because we already used it in other Vue projects (BSB RAM, Univention Portal) and have experience with it.
- Bad, because it moves us away from company standardization of frontend testing tools.

### Option 2.1: Vitest

- Good, because it is a Vite-native (bundles with Vite) testing tool, and we use Vite (no extra dependency)
- Good, supports test coverage

### Option 2.2: Jest

- Good, because we use it in other Vue projects (Univention Portal).
- Neutral, we don't have anyone in the UCS@School team that has Jest experience.
- Good, supports test coverage

### Option 3.1: Only use end-to-end tests against production environment

- Good, because all tests will run, how the end user would encounter them
- Bad, running tests needs more complex test setup
- Bad, tests are more likely to fail for different reasons than what is supposed to be tested (e.g. Test fails already at login)

### Option 3.2: Only use end-to-end tests with mock data

- Good, easier test setup
- Good, tests could be more streamlined (e.g. skipping login)
- Bad, possible false positives. Passing tests using mock data might fail in production environment
- Bad, no production scenario is tested

### Option 3.3: Use both end-to-end tests with mock data and production environment

- Good, can use most appropriate test depending on what is being tested. (e.g. visual screenshot test does not necessarily need production environment)
- Bad, more complexity due to 2 test setups

### Option 4.1: Code paths that can be tested with end-to-end tests should be tested that way

- Good, the code path is tested how it is actually encountered in production (via different browsers)
- Bad, getting to the code path via browser might be cumbersome and the test is prone to fail for unrelated reasons

### Option 4.2: If an end-to-end test exists for a code path, additional unit tests are allowed for that path

- Good, production scenario is covered and additional test parametrization can be tested faster with unit tests
- Bad, possibility that some test parametrization has different/unintended outcome in GUI and is not caught

### Option 4.3: Code paths may be tested by unit test only

- Good, unit tests are easier to write and are resistant to unrelated influences in the stack (e.g. login failed)
- Neutral, there probably exist code paths that have no direct effect on the GUI and are fine to test with unit tests only

### Option 5.1: All tests run in GitLab pipelines

- Good, because it's easy to set up and maintain
- Good, because it's easy to integrate with GitLab
- Good, because it's easy to run tests in parallel
- Good, because we have fewer points of truth about our tests. The time until tests are fixed could decrease through this.
- Bad, Integration tests will not mirror the actual environment existing on a customer installation (docker containers vs current UCS deployment).
- Bad, there's some uncertainty about the LDAP and UDM Docker images setup and capabilities.

### Option 5.2: Run end-to-end tests against production environment in Jenkins and the rest in GitLab pipelines

- Good, because more complex setups can be used which allows us to test the actual environment existing on a customer installation
- Bad, because it's more difficult to set up and maintain
- Bad, because it's not directly integrated with GitLab
- Bad, because it's more difficult to run tests in parallel

## Decision Outcome

### Chosen option for "Which end-to-end test framework to use": "Option 1.1: Playwright"

We already have an [ADR](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0001-playwright-for-ete-testing.md?ref_type=heads)
to use Playwright for other product parts, and we don't want to use too many different tools.
Also using Playwright has no visible downside to cypress feature wise and supports code coverage out of the box
(visualization of the code coverage data needs extra dependency though and support for vue out of the box
is not fully tested).

### Chosen option "Which Unit test framework to use": "Option 1.1: Vitest"

As we already use Vite as build tool/dev server, using Vitest, which is a Vite-native (bundled with Vite) testing tool, reduces
the amount of dependencies configuration and maintenance of an additional tool. Vitest has also built-in code coverage support.

### Chosen option for "What test type is preferred": "Option 3.3: Use both end-to-end tests with mock data and production environment"

Due to the nature of ports and adapters using a production environment is not strictly necessary
to test certain features. Using tests against mock data also allows for isolated local testing (not auth/data api setup needed)
and makes the tests less flaky.

Tests against production environment are still wanted to reduce false positive mock data tests.

### Chosen option for "Do we use unit tests": "Option 4.3: Code paths may be tested by unit test only"

Even if a code path can be entered through the UI it does not necessarily need to be tested through the UI to be valid.
E.g. a function that creates a string based on some input might be shown in the UI but can still be correctly tested via a unit test.
This will also reduce the runtime of the tests.

### Chosen option for "Where do tests run": "Option 5.2: Run end-to-end tests against production environment in Jenkins and the rest in GitLab pipelines"

It doesn't need the LDAP and UDM Docker images, and allows us to test the actual environment existing on a customer installation.
