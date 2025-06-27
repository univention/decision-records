# Playwright for E2E testing in UCS

- status: accepted
- date: 2023-13-07
- deciders: tech-intern
- consulted: IAM/Bitflip/SouvAP Team
- informed:  IAM/Bitflip/SouvAP Team/service-intern@univention.de

---

## Context and Problem Statement

End-to-end (E2E) tests verify the behavior of a system by testing use cases
from an outside/user perspective. It is black-box testing, as only the
external, public entry points (like a website) are used.

Univention development currently uses "Selenium" for UI tests.

The usage of Selenium is cumbersome, and the team wishes to evaluate
alternatives. With the SouvAP team using Playwright, an evaluation has become
more urgent, as using the same tools has benefits.

Should we switch to https://playwright.dev/ as the main tool for E2E testing
(instead of using selenium) in UCS?

This is not about preventing someone from using another tool if its better for
the task at hand. This about the default tool in ucs-test for E2E testing.

## Decision Drivers

- make an informed decision about what tool we are using for E2E testing
- current selenium tests are sometimes hard to maintain and debug
- current selenium tests are slower (compared to the alternatives)
- make E2E testing fun again

## Considered Options

- selenium
- playwright
- cypress

## Consideration criteria

- End-to-End testing for the web UI for Univention products
- Integration into pytest, because most of our tests are written in
  python (pytest)
- Existing know-how in the company
- Debugging, tracing and reporting tools
- Easy to install

## Decision Outcome

Chosen option: The migration to playwright as a proof-of-concept was successful
and the ADR has been acctepted. From now on we will use playwright for E2E testing
as default (instead of selenium) in SouvAP and ucs-test. Other tools are of course
allow if they fit better for the given purpose.

The final decision depends on the proof-of-concept (currently bitflip is trying
to migrate some of the test in UCS to playwright to see if playwright keeps its
promises). If that is successful we will switch to playwright for
E2E testing in UCS.

### Positive Consequences

- improves quality of our tests
- makes writing tests easier
- Get rid of Selenium and the associated negative feelings

### Negative Consequences

- we need to migrate our existing tests
- Learn a new tool

## Pros and Cons of the Options

### Selenium

- Good, because we don't need to re-write the tests
- Bad, because it is hard to write good test with our current selenium tools/libs
- Bad, high learning curve
- Bad, no built-in reporting capabilities

### Playwright

- Good, because it is faster and reduces test execution time, especially for longer and complex tests
- Good, because writing test will become easier
- Good, because it has feature that are missing in selenium (e.g. video capture)
- Good, no webdrivers needed (uses the browsers dev tools protocol)
- Good, no more xpath expressions (selectors can identify elements based on their aria roles and labels)
- Good, playwright has an auto-wait feature
- Good, playwright's test generator can generate test scripts automatically based on user actions
- Good, has best-in-class debugging, tracing and reporting tools
- Good, has an official pytest plugin (developed by the core Playwright team) which supports multi-browser testing, parallel testing, device emulation (mobile browser testing), tracing, video recording, snapshotting, slow motion testing, reporting etc. out of the box
- Good, extensive knowledge about playwright in the SouvAP team
- Bad, does not yet have as broad a range of support for browsers/languages or community support
- Bad, no debian packages
- Bad, yet another tool

### Cypress

- Good/Bad, may be helpful for front-end developers, but not as a general (e2e) testing framework
- Bad, only supports JavaScript
- Bad, yet another tool
- Bad, can’t test multiple tabs or multiple browser windows at the same time
- Bad, no integration with pytest

## More Information

- Supported browsers:
  - playwright[¹]:
    chromium, Chrome, Chrome-beta, Msedge, Msedge-beta, Msedge-dev, Firefox, Webkit
  - selenium[²]: Chrome, Edge, Firefox, Internet Explorer, Safari

- https://playwright.dev/python/
- https://www.cypress.io/
- https://www.selenium.dev/

[¹]: from `playwright install --help` of version 1.30.0

[²]: from https://www.selenium.dev/documentation/webdriver/browsers/
