# Log Messages

<!--
- Max line length: 120
- Each sentence on a new line for better diffs
-->

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2024-03-22
- author: @dtroeder
- approval level: low (see [explanation](https://git.knut.univention.de/univention/decision-records/-/blob/main/adr-template.md?ref_type=heads&plain=1#L19) | Low impact on platform and business. Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.)
- coordinated with: **TODO** {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- source: [Logging concept](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/README.md)
- scope: ALL Univention software products.
  New products in Docker containers or in the host on UCS 5.2 MUST adhere to the ADR immediately.
  Existing software MUST be migrated gradually in errata and point releases of UCS 5.2.
- resubmission: -
- related ADR: [0004 Logging Topology](0004-logging-topology.md), [0005 Log Levels](0005-log-levels.md), [0006 Log Format](0006-log-format.md), [0008 Structured Logging](0008-structured-logging.md)

---

[[_TOC_]]

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](https://git.knut.univention.de/univention/internal/research-library/-/blob/07df7be3a61f5eeab776309f19c3abb7c943ff44/research/logging_concept/README.md)
describes, besides a logging architecture, what and how to log: message content and metadata.

This ADR specifies various details about how UCS' components must produce log messages:

- Message text
- Metadata
- Handling of sensitive data
- Formatting of a log line
- Configurability

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0006 Log Format](0006-log-format.md) defines the content and format of log messages.
- [0007 Log Messages](0007-log-messages.md) defines the content and metadata of log messages.
- [0008 Structured Logging](0008-structured-logging.md) defines the use of structured logging.

## Decision Drivers

- Homogeneity…
  - of what to expect at each log level.
  - of how sensitive data is handled.
  - of reading and analysing logs (for humans and machines).
- Simplicity of configuration…
  - of logging library (for developers).
  - for operator (sensitive data).
- Compatibility of solutions…
  - for UCS software running in the UCS host and in an App Center Docker container.
  - for UCS and Nubus.
- Accessibility and searchability of log messages…
  - interactively with a CLI.
  - non-interactively by USI.
  - through an API to realize a UMC module (no concrete plans, just an idea).
  - by a log collector for transport into a customers log aggregator.

## Log messages

When developing and writing log messages do _not_ assume knowledge of the context (the code) surrounding
the logging call.
Most readers (including the future you) of the message will _not_ know it.

The content of a log message should match the log level and _audience_.
See ADR [0005 Log Levels](0005-log-levels.md) about log levels.

- **Logs lines intended _only_ for developers and support** (`TRACE` and `DEBUG`):
  - … can assume intimate technical knowledge of the application.
  - The context such a message SHOULD include is that of a _technical subsystem_.
  - E.g. for a message about opening a network connection, it must be clear that we're in the _database
    port_, but there is no need to include a wider context like that we are in the process of reading
    a group object.
  - E.g., `TRACE Cleared ucsschool.lib School objects cache.`
  - E.g., `TRACE Loaded plugin. name='foo.py'`
  - E.g., `DEBUG Opened connection to configuration database. host='foo.bar' port=3210`
  - E.g., `DEBUG Received IP address. ip='10.20.30.40'`
  - Messages in these log levels MAY include sensitive data (such as passwords or tokens)
    if a _dedicated_ configuration option has been enabled.
    Otherwise, they MUST NOT include sensitive data.
- **Logs lines intended for operators** (everything from `INFO` until `CRITICAL`):
  - … must _not_ assume internal technical knowledge of the application.
  - The context such a message SHOULD include is that of a _business use case_.
  - `INFO`: The message can often be short, as its "context" is the business use case itself.
    It should include only the event and relevant data.
    - E.g.: `INFO Created user. dn='uid=foo,cn=...'`
    - E.g.: `INFO Finshed … task. duration=1.32 items=47`
  - `WARNING`: The message should include the problem and if available a hint how to avoid it in the
    future.
    - E.g.: `WARNING Deactivating … feature. Install <package> and set UCRV <k>=<v> to enable it. plugin='<name>.py'`
    - E.g.: `WARNING Changing membership took 30s. Avoid more than 5.000 members, check system load, try raising worker count. dn='cn=Domain Users,cn=...'`
    - E.g.: `WARNING UCRV 'logging/sensitive/<application>/log-passwords' is enabled. Unset URV and restart app to prevent logging sensitive data.`
  - `ERROR`: The message should include (besides the business case during which it was logged) as much
    information about the problem as possible, without divulging sensitive data.
    Purely internal error messages without business context should be avoided.
    See example a few paragraphs below.
    - E.g.: `ERROR Failed to change group membership: permissionDenied: Zugriff verweigert. dn='cn=group,dc=...' old_users=['uid=..', '..'], new_users=..`
  - `CRITICAL`: Besides everything that is written for `ERROR` it should include the information _why_
    the software cannot continue. It should be written so that an operator understands _why_ the software
    is shutting down.
    - E.g.: `CRITICAL Failed to load configuration, aborting: Error reading configuration file: Parsing JSON at line 1. path='/foo/bar.xml'`
    - E.g.: `CRITICAL Cannot connect to <service>, shutting down: TimeoutError: Connection timed out: errno 110 host='10.20.30.40' port=22 errno=110 ttl=60`

Understanding log messages SHOULD NOT depend on previous log messages, as those may not be logged with the
same log level, be extracted to a different file or in asynchronous / multi-threaded applications may
appear interleaved or way before the one being read.
See section _Logging errors_ for how to ensure that when errors happen.

Log messages SHOULD name the event and additional data separately (e.g. `Missing file. path='/foo/bar'`).
That simplifies parsing, classification, filtering and counting.
It also keeps the log lines more consistent.

Structured logging SHOULD be used.
It will programmatically support the separation of event and data.
Instead of `log("An event with num: %d.", num)` you'll write `log("An event.", num=num)`
and the logging library will take care of redering it so humans and machines can comfortably read it.
See ADR [0008 Structured Logging](0008-structured-logging.md) about that.

## Sensitive data

What is "sensitive data" and how to handle it?
Please read [section _Sensitive data_ in the logging concept](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/README.md#sensitive-data).

Generally, sensitive data SHOULD NOT be logged.

Sensitive data MUST NOT be logged at log levels `INFO` and above.

Only when a _dedicated_ configuration option has been enabled,
messages in the log levels `TRACE` and `DEBUG` MAY include sensitive data.
An application MAY register one or more UCRVs for that purpose.

The UCR key schema is `logging/sensitive/<application>/log-<object>=<bool>`.

- `<application>` is the name of the program / script / service the logging should be defined for.
  - The special name `default` is NOT allowed.
- `<object>` is what should be logged.
  The name should be specific, so customers know what they are doing.
- Using multiple UCR keys is encouraged to allow fine-grained control.

Examples:

```text
logging/sensitive/<application>/log-hashes=<bool>
logging/sensitive/<application>/log-passwords=<bool>
logging/sensitive/<application>/log-tokens=<bool>
logging/sensitive/<application>/log-user-data=<bool>
```

- The UCRVs MUST be disabled by default.
- The documentation MUST clearly describe the benefits and warn of the dangers associated with them.
- To reduce boilerplate code, the Univention logging library SHOULD support developers with a dedicated
  function for logging sensitive data.
- A System Diagnose module SHOULD be written that warns customers when any UCRV starting with
  `logging/sensitive/` is enabled.

## Logging errors

When an operation in a called function fails, the function can only log what it knows.
It may not be able to log information about the wider context.
Do _not_ pass the context into the function.
Instead, use exceptions and add information on each level.
For example:

Call chain: `main() -> queue_iter() -> parse_queue_item() -> parse_file(path) -> parse_json(string)`

- `parse_json()` encounters an error parsing the passed in string.
  - It won't log it. The logs reader wouldn't know where it came from.
  - The JSON library raises `ValueError("Parsing JSON at line 12.")` or similar and `parse_json()`
    doesn't handle it.
- `parse_file()` catches the `ValueError` and adds what it knows: the filesystem path.
  - It won't log it. Maybe it's OK it happens. Maybe it happens 10000 times. It cannot decide or handle it.
  - It raises: `FormatError(str(exc), path=path) from exc` so the caller can handle it.
- `parse_queue_item()` adds the business context (that a _queueing_ file was being read).
  - It raises: `QueueItemError(f"Parsing queuing file: {exc!s}", **exc.kwargs) from exc` because it also
    doesn't know what to do about it.
- `queue_iter()` catches the `QueueItemError` and knows how to handle it.
  - It logs a WARNING (because it is an error that could be handled by the software) adding the ID of
    the transaction (`queue_id`):
    `logger.warning(f"Reading queue file: {exc!s}", queue_id=queue_id, **exc.kwargs)`

This example exists as a script that you can run: [logging/log_errors.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/log_errors.py).
Please read the instructions in the comment block at its top on how to install it.

When executed, the output of the warning message will be a single log line containing all information:

```text
2024-03-07 09:27:14.606 +0100 | DEBUG | 1746339 | log_errors.main | Handling queue item. | {"item":{"a":"A"},"queue_id":"5034eb43"}
2024-03-07 09:27:14.606 +0100 | WARNING | 1746339 | log_errors.queue_iter | Reading queue file: Parsing file: Expecting value: line 1 column 1 (char 0) | {"path":"/tmp/bbb.json","queue_id":"c293da11"}
2024-03-07 09:27:14.606 +0100 | DEBUG | 1746339 | log_errors.main | Handling queue item. | {"item":{"c":"C"},"queue_id":"1d019e14"}
```

## Structured logging

As noted in section _Log messages_, log messages SHOULD name the event and additional data separately
(e.g. `Missing file. path='/foo/bar'`).
This practice has several benefits and is a precondition for _structured logging_.
For a discussion of this topic, please read ADR [0008 Structured Logging](0008-structured-logging.md).
