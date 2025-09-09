# Log Format

<!--
- Max line length: 120
- Each sentence on a new line for better diffs
-->

---

- status: accepted
- supersedes: [0006 Log Format](0006-log-format.md)
- superseded by: -
- date: 2025-09-20
- author: @dtroeder
- approval level: medium (see [explanation](https://git.knut.univention.de/univention/dev/decision-records/-/blob/main/adr-template.md?plain=1&ref_type=heads#L19))
- coordinated with: @fbest, @steuwer
- source: [Epic "Logging of LDAP-Objects"](https://git.knut.univention.de/groups/univention/-/epics/913)
- scope: ALL Univention software products.
  New products in containers or in the host on UCS 5.2 and Kubernetes MUST adhere to the ADR immediately.
  Existing software MUST be migrated gradually in errata and point releases of UCS 5.2+ and Nubus for Kubernetes.
- resubmission: -
- related ADR: [0004 Logging Topology](0004-logging-topology.md), [0005 Log Levels](0005-log-levels.md), [0007 Log Messages](0007-log-messages.md), [0008 Structured Logging](0008-structured-logging.md)

---

[[_TOC_]]

## ADR Update

This ADR supersedes [0006 Log Format](0006-log-format.md).
It is an updated copy of all of its content.
The main difference to the previous ADR is that the format of a log record (line) is now defined more exact.

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](logging/logging_concept.md)
describes, besides a logging architecture, what and how to log: message content and metadata.

This ADR specifies how Nubus' components format a log line.

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0010 Log Format](0010-log-format.md) defines the content and format of log messages.
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
  - by a log collector for transport into a customer's log aggregator.

## Log format

- Log lines SHOULD be formatted so that all required fields are at the beginning and have a fixed width.
  Padding MAY be used to produce fixed width columns.
  This "table-like" view allows humans to parse logs faster.
  We assume log aggregators strip white space left and right of the values.
- Log lines MUST start with a timestamp.
  - Timestamps MUST contain a time zone.
  - The time zone SHOULD be UTC, but it can be local (an offset from UTC). All log files MUST use the same time zone.
  - Timestamps MUST have sub-second accuracy, milliseconds or microseconds.
  - Timestamps MUST conform to ISO 8601: `YYYY-MM-DDTHH:MM:SS.fff[fff]+HH:MM`
- Log lines MUST contain the severity (log level). See ADR [0005 Log Levels](0005-log-levels.md).
- Log lines MUST contain a reference to the source code that produced the message.
  This _source code reference_ help developers and supporters finding the responsible source code
  and understanding the applications control flow.
  - The format of the source code reference can differ between applications.
    It MUST include the name of the source code file (Python module) and the line number of the log function call.
  - Developers and operators can also use this information for fine-grained log level configuration
  (see section _Configuration of log levels_ of ADR [0005 Log Levels](0005-log-levels.md)).
- Log lines MAY contain the process ID (PID). In multiprocessing applications this value is _required_ (MUST).
- Log lines SHOULD contain a correlation/reference ID.
  Operators use it to track and correlate requests and events across service and network boundaries.
  They also use it to correlate log lines of services that process multiple requests in parallel.
  - To produce a consistent format, this field will always be in logs, even when applications don't use reference IDs.
  - In cases where there is no reference ID, regardless if it's an entire application or only one log record,
    a dash `-` is written as reference ID.
- Classifying data that is not provided by all software, for example log facilities, would mess up an
  otherwise homogenous header.
  Thus, it SHOULD NOT be added to the header, but it MAY be added to the data part.
- Log lines MUST contain the log message.
  - Structured logging is encouraged.
    In that case, the log message SHOULD contain only the event, not the data.
- Tracebacks SHOULD be written in multiple lines following the error message at ERROR level.
  This format is convenient for human readers.
- Tracebacks MAY be added as a single string value to the data section of the log record.
  This format is convenient for log aggregators.
- Log lines MAY contain a section (visually separated from the message) with data in a JSON-parsable
  or [logfmt](https://brandur.org/logfmt)-parsable format.
  - In structured logging, this section is required.
  - The data section MAY repeat values from the header section. This can simplify writing parsers for log aggregators.

The values in rules starting with _Log lines MUST_ SHOULD be part of the metadata section left of the message.
The _source code reference_ is not interesting for operators, so it SHOULD be part of the structured data section.
The values in rules starting with _Log lines MAY_ SHOULD be part of the structured data section.

Thus, log lines SHOULD be formatted in the following way:

- The MUST values timestamp, severity, and request ID are stored in the header section.
  Padding and brackets are used to create vertically aligned columns.
- This is followed by the message (MUST).
- If a data section exists, it is separated by a tab, a pipe, and a space (`\t| `) from the message.
- When using structured logging, the data section contains besides application data, the remaining MUST and MAY values.

Resulting template without structured logging (the brackets around the request ID are literal):

```text
<timestamp> <severity:8> [<request ID>] <message>
```

Resulting template with structured logging (the brackets around the request ID are literal,
in the data section they mean their content is optional):

```text
<timestamp> <severity:8> [<request ID>] <message>\t| <app data> <source code reference> [PID] [log facility] [traceback]
```

Example:

In this example, additionally to application specific data, the Python module and the process ID are in the data section.
The request ID is shortened to 10 characters in the header section. The data section contains it in full length.

```text
2023-10-27T08:22:57.275138+00:00 INFO     [31f863092a] modified group	| dn="..." old="{..}" new="{..}" module=app.main.loop pid=13825 request_id=31f863092ade1cb
2023-10-27T08:22:58.123454+00:00 DEBUG    [         -] received request	| headers={..} method="POST" json={..} module=app.net.http pid=13825 request_id=-
2023-10-27T08:22:58.351345+00:00 TRACE    [b0ca915ec4] cache hit	| hash="..." ttl=... module=app.backend.cache pid=13825 request_id=b0ca915ec433a21
```

### Parsing

Such a log line can be split into _timestamp_, _severity_, _request ID_, _message_, and _data_
with a regular expression.
From left ot right:

- A log line starts with an IS8601 date string. It contains no white space.
- The date is followed by one or more spaces (depending on left or right alignment of the severity).
- The severity is one word and contains no white space.
- The severity is followed by one or more spaces (depending on its left or right alignment).
- The request ID is enclosed in square brackets.
  Any printable character, except the closing square bracket (`]`), is allowed between the brackets.
  It is recommended to limit its length to 10 characters, but it is allowed to be shorter or longer.
  It should never be empty. A missing request ID should be written as a dash (`-`).
- The closing square bracket of the request ID is followed by a single space.
- The message can contain any character. But newlines and the separator to the data section are escaped (see next section).
- The message is followed by a tab, a pipe, and a space.
- The data section comprises key-value pairs, and stretches until the end of the line.

This can be implemented using the following Python regular expression:

```python
ADR0010_REGEX = (
    r"^(?P<date>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,6}\+\d{2}:?\d{2}) +"
    r"(?P<level>\w+?) +\[(?P<request_id>.*?)\] (?P<message>.+?)\t\| (?P<data>.*?)$"
)
```

### Escaping

We escape tabulator and newline symbols in the message, to ensure it's safely parsable as described above.

Newlines are printed as `\n`.
The entire message may be enclosed in quotes.

The separator between message and data is a tab, a pipe, and a space.
If this character sequence is found in the message, it must be changed.
<!-- pyml disable-next-line no-space-in-code-->
For example by adding a backslash before the pipe (`\t\| `).

## Configuration of log format

The log format SHOULD NOT differ between applications and machines of the same domain.
Homogeneously formatted log messages are easier to read for both humans and machines.

The log format of different domains MAY differ.
But the benefit of this configurability is doubtful.

Thus, until there is a customer request that justifies an implementation,
Univention will NOT support the configuration of the log format.

There is one exception: During transition phases customers can switch between an old and a new format.

## Logging libraries

Univention SHOULD create Python and shell logging libraries to ensure the creation of log messages with
a consistent format.
For Python look at ADR [0008 Structured Logging](0008-structured-logging.md), as the requirements of
structured logging demand a decision among logging libraries.
