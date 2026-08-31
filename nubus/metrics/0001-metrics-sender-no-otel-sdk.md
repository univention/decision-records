# Use pure Python and `requests` for metrics sender MVP in nubus

- status: accepted
- supersedes: -
- superseded by: -
- date: 2026-04-30
- author: @fbotner
- approval level: low
- coordinated with: nubus core, @dtroeder
- source: https://git.knut.univention.de/univention/dev/internal/team-nubus/-/work_items/1620
- scope: ADR is only valid as a workaround until the Debian environment is upgraded to a version supporting modern OpenTelemetry dependencies.

> Note: Before being moved here,
> this file was accidentally stored as `nubus/0002-metrics-sender.md`
> in the internal decision records repository `univention/dev/internal/decision-records`
> ([original commit](https://git.knut.univention.de/univention/dev/internal/decision-records/-/blob/f71cb39f8f09f7a3ce515f91389221bafc866d2e/nubus/0002-metrics-sender.md)).

[[_TOC_]]

## Context and Problem Statement

We need to implement a Minimum Viable Product (MVP) for sending OpenTelemetry (OTel) metrics to our observability backend. Our current infrastructure is restricted by an older Debian version that lacks the necessary dependencies for the official OpenTelemetry Python SDK, and we wish to avoid the overhead of managing a local OTel Collector or insecure backports at this stage. How can we emit OTLP-compliant metrics with minimal architectural friction and zero changes to our base OS?

## Decision Drivers

- **Simplicity:** Minimize new infrastructure and complex configuration for the initial release.
- **Security:** Avoid introducing unverified backports into the Debian environment which would require additional security monitoring.
- **Speed to Market:** Enable metric collection immediately without waiting for a full OS upgrade.
- **Standardization:** Ensure data is sent in a format (OTLP) that allows for future migration to official libraries.
- **Maintainability:** Choose a solution that, in the long run, avoids growing development efforts that eat away at the time savings of initially-quicker solutions.

## Considered Options

- Pure Python (using `requests`)
- Official OpenTelemetry SDK (`python-opentelemetry`)
- OTel Collector (Sender-side/Sidecar)

## Pros and Cons of the Options

### Pure Python (using `requests`)

Manually constructing OTLP/JSON payloads and using the `requests` library to POST data to Univention's OpenTelemetry Collector.

- Good, because it introduces no new system-level dependencies.
- Good, because it is extremely lightweight and easy to deploy.
- Bad, because we must manually maintain the OTLP schema in our code.
- Bad, because it lacks built-in SDK features like automatic retries, batching, and asynchronous exporting.

### Official OpenTelemetry SDK (`python-opentelemetry`)

Utilizing the industry-standard libraries provided by the OpenTelemetry project.

- Good, because it is robust, feature-complete, and the industry standard.
- Bad, because it's not available in our current Debian version, and using backports would either introduce significant security monitoring debt or require investment in infrastructure.

### OTel Collector (Sender-side/Sidecar)

Running a dedicated collector process alongside the application to handle ingestion and forwarding.

- Good, because it represents the best-practice architecture for scaling.
- Good, because it offloads processing and retry logic from the application.
- Bad, because it requires "way too much effort" for a first MVP implementation.
- Bad, because it introduces new infrastructure components that must be managed and monitored.

## Decision Outcome

Chosen option: **"Pure Python (using `requests`)"**, because it is the only option that meets our K.O. criteria of requiring no OS-level changes or backports while remaining within the "low effort" requirement for an MVP. By using the OTLP/JSON format, we maintain compatibility with the OTel standard for a future drop-in replacement with the official SDK.

### Consequences

- Good, because we can deploy metrics immediately without waiting for infrastructure upgrades.
- Good, because the security posture of the Debian environment remains unchanged.
- Bad, because we incur technical debt by manually implementing a subset of the OTLP specification.
- Neutral: We expect the OTLP specification to be highly stable, so that part will be low-maintenance.
- Bad, because we risk further development efforts for robustness features that the other solutions offer.
- Neutral: Although synchronous `requests` calls can introduce slight latency into applications, the application that is currently planned for sending data is a dedicated job without performance requirements.

## More Information

This decision should be revisited as soon as a Debian OS upgrade is scheduled. Upon upgrade, this custom implementation must be decommissioned and replaced with the official `opentelemetry-python` SDK -> https://git.knut.univention.de/univention/dev/ucs/-/work_items/3504.
