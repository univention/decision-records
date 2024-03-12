# Log Format

<!--
- Max line length: 120
- Each sentence on a new line for better diffs
-->

---

- status: draft
- supersedes: -
- superseded by: -
- date: 2024-02-22
- author: @dtroeder
- approval level: low (see [explanation](https://git.knut.univention.de/univention/decision-records/-/blob/main/adr-template.md?ref_type=heads&plain=1#L19) | Low impact on platform and business. Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.)
- coordinated with: **TODO** {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- source: [Logging concept](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/README.md)
- scope: ALL Univention software products.
  New products in Docker containers or in the host on UCS 5.2 MUST adhere to the ADR immediately.
  Existing software MUST be migrated gradually in errata and point releases of UCS 5.2.
- resubmission: -
- related ADR: [0004 Logging Topology](0004-logging-topology.md), [0005 Log Levels](0005-log-levels.md), [0007 Log Messages](0007-log-messages.md), [0008 Structured Logging](0008-structured-logging.md)

---

[[_TOC_]]

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](https://git.knut.univention.de/univention/internal/research-library/-/blob/07df7be3a61f5eeab776309f19c3abb7c943ff44/research/logging_concept/README.md)
describes, besides a logging architecture, what and how to log: message content and metadata.

This ADR specifies how UCS' components format a log line.

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0006 Log Format](0006-log-format.md) defines the content and format of log messages.
- [0007 Log Messages](0007-log-messages.md) defines the content and metadata of log messages.
- [0008 Structured Logging](0008-structured-logging.md) defines the use of structured logging.

## Decision Drivers

- Homogeneity…
  - of reading and analysing logs (for humans and machines).
- Compatibility of solutions…
  - for UCS software running in the UCS host and in an App Center Docker container.
  - for UCS and Nubus.
- Accessibility and searchability of log messages…
  - interactively with a CLI.
  - non-interactively by USI.
  - through an API to realize a UMC module (no concrete plans, just an idea).
  - by a log collector for transport into a customers log aggregator.

## Log format

- Log lines SHOULD be formatted so that all required fields are at the beginning and have a fixed width.
  This "table-like" view allows humans to parse logs faster.
- Log lines MUST start with a timestamp.
  - Timestamps MUST contain a time zone.
  - The time zone SHOULD be UTC, but it can be local. All log files MUST use the same time zone.
  - Timestamps MUST have sub-second accuracy, by default microseconds.
  - Timestamps MUST conform to ISO 8601: `YYYY-MM-DDTHH:MM:SS.ffffff+HH:MM[:SS[.ffffff]]`
- Log lines MUST contain the severity (log level). See ADR [0005 Log Levels](0005-log-levels.md).
- Log lines MUST contain the source package and module name where they originate from.
  Developers and operators need to know this value (`<package>.<module>`) for fine-grained log level
  configuration (see section _Configuration of log levels_ of ADR [0005 Log Levels](0005-log-levels.md)).
- Log lines MAY contain the source file and line number where they originate from, especially for debug/trace levels.
- Log lines MAY contain the process ID (PID)
- Log lines MAY contain a correlation/reference ID. Operators use it to track and correlate requests and
  events across service and network boundaries. They may also use it to correlate log lines of services
  that process multiple requests in parallel.
- Classifying data that is not provided by all software, for example log facilities, would mess up an
  otherwise homogenous header.
  Thus, it SHOULD NOT be added to the header, but it MAY be added to the data part.
- Log lines MUST contain the log message.
  - Structured logging is encouraged.
    In that case, the log message SHOULD contain only the event, not the data.
- Log lines MAY contain a section (visually separated from the message) with data in a JSON-parsable
  or [logfmt](https://brandur.org/logfmt)-parsable format.
  - In structured logging, this section is required.

The values in rules starting with _Log lines MAY contain_ can either be part of the metadata section
left of the message or of the structured data.

Examples:

```text
2023-10-27T08:22:57.275138+00:00 INFO  13825 31f863092ade app.main.loop | modified group | dn='...' old={..} new={..}
2023-10-27T08:22:58.123454+00:00 DEBUG 13825 b0ca915ec433 app.net.http | received request | headers={..} method='POST' json={..}
2023-10-27T08:22:58.351345+00:00 TRACE 13825 b0ca915ec433 app.backend.cache | cache hit | hash='...' ttl=...
```

The above example stores the Python module (MUST), a request ID (MAY) and the process ID (MAY) in the header section.
Below is the same example with that information stored in the data section:

```text
2023-10-27T08:22:57.275138+00:00 INFO  | modified group | dn='...' old={..} new={..} module=app.main.loop pid=13825  request_id=31f863092ade
2023-10-27T08:22:58.123454+00:00 DEBUG | received request | headers={..} method='POST' json={..} module=app.net.http pid=13825 request_id=b0ca915ec433
2023-10-27T08:22:58.351345+00:00 TRACE | cache hit | hash='...' ttl=... module=app.backend.cache pid=13825 request_id=b0ca915ec433
```

## Configuration of log format

The log format SHOULD NOT differ between applications and machines of the same domain.
Homogeneously formatted log messages are easier to read for both humans and machines.

The log format of different domains MAY differ.
It is possible to create a UCRV schema that allows configuring the message format
(header, text, and data), as well as the data to store in the data section.
The format would be valid for all applications.
The Univention logging library would interpret the settings and configure the `Formatter`
and the process-wide `extra` data accordingly.

The benefit of the described configurability is doubtful.
Until there is a customer request that justifies an implementation, Univention will NOT support it.

## Logging library

Univention SHOULD create Python and shell logging libraries to ensure the creation of log messages with
a consistent format.
For Python look at ADR [0008 Structured Logging](0008-structured-logging.md), as the requirements of
structured logging demand a decision among logging libraries.
