# Structured Logging

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
- related ADR: [0004 Logging Topology](0004-logging-topology.md), [0005 Log Levels](0005-log-levels.md), [0006 Log Format](0006-log-format.md), [0007 Log Messages](0007-log-messages.md)

---

[[_TOC_]]

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](https://git.knut.univention.de/univention/internal/research-library/-/blob/07df7be3a61f5eeab776309f19c3abb7c943ff44/research/logging_concept/README.md)
describes, besides a logging architecture, what and how to log: message content and metadata.

This ADR specifies how UCS' components use structured logging.

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0006 Log Format](0006-log-format.md) defines the content and format of log messages.
- [0007 Log Messages](0007-log-messages.md) defines the content and metadata of log messages.
- [0008 Structured Logging](0008-structured-logging.md) defines the use of structured logging.

## Decision Drivers

- Homogeneity…
  - of reading and analysing logs (for humans and machines).
- Simplicity of configuration…
  - of logging library (for developers).
  - for operator (parsing structured data).
- Compatibility of solutions…
  - for UCS software running in the UCS host and in an App Center Docker container.
  - for UCS and Nubus.
- Accessibility and searchability of log messages…
  - interactively with a CLI.
  - non-interactively by USI.
  - through an API to realize a UMC module (no concrete plans, just an idea).
  - by a log collector for transport into a customers log aggregator.

## Motivation

As noted in section _Log messages_ of ADR [0007 Log Messages](0007-log-messages.md),
log messages SHOULD name the event and additional data separately (e.g. `Missing file. path='/foo/bar'`).
That simplifies parsing, classification, filtering and counting.
It also keeps the log lines more consistent, which allows a human reader to consume a log file faster.

Structured logging is also recommended, because UCS products produce very few metrics
that customers can use to observe and predict system behavior.
UCS also supports tracing only very sparingly,
together with the lack of metrics leading to a low _observability_.

Structured logs allow customers to configure their log aggregators to extract data relevant for them.
Being able to create their own metrics from parsed logs allows them to get answers
without Univention having to know the questions and providing new interfaces.

## Contextualized loggers

But structured logging is not only about the output.
Libraries also offer a convenient way to assemble the data to log, by _contextualizing_ the logger
instance:

```python
logger = logger.bind(ip="192.168.0.1", user="someone")
# ..
logger = logger.bind(groups=[".."])
# ..
logger.info("Started new task.", task_id=132)

# <timestamp> | INFO | Started new task. | ip="192.168.0.1" user="someone" groups=[".."] task_id=132 
```

## Output formatting

When using structured logging, we have the option to store each line as a JSON object.
That format is very easy to parse and analyse for log aggregators.
But reading JSON is not very comfortable for humans.
As a compromise between readability for humans and machines the encoding of _only_ the data part is
RECOMMENDED.

The example script [logging/log_errors.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/log_errors.py) can log in a pure JSON-serialized form
and in two "hybrid" modes.
Change the value of the `DATA_FORMAT` and `SERIALIZE` constants to test it.

### Option 1: All JSON

Edit the script (at the bottom) to format each log line in as a JSON object:

```python
setup_logging(
    serialize=True,      # allowed values: True, False.
    data_format="JSON",  # allowed values: "JSON", "LOGFMT". Will be ignored if SERIALIZE==True.
)
```

```text
./dev/logging/log_errors.py  2>&1 | head -1
{"text": "Handling queue item.\n", "record": {"elapsed": {"repr": "0:00:00.005476", "seconds": 0.005476}, "exception": null, "extra": {"item": {"a": "A"}, "queue_id": "681ef37b"}, "file": {"name": "log_errors.py", "path": "/home/dtroeder/git/decision-records/dev/logging/log_errors.py"}, "function": "main", "level": {"icon": "🐞", "name": "DEBUG", "no": 10}, "line": 42, "message": "Handling queue item.", "module": "log_errors", "name": "__main__", "process": {"id": 1791761, "name": "MainProcess"}, "thread": {"id": 140443741970432, "name": "MainThread"}, "time": {"repr": "2024-03-07 16:11:48.831920+01:00", "timestamp": 1709824308.83192}}}
```

Prettified:

```json
{
  "text": "Handling queue item.\n",
  "record": {
    "elapsed": {"repr": "0:00:00.005476", "seconds": 0.005476},
    "exception": null,
    "extra": {"item": {"a": "A"}, "queue_id": "681ef37b"},
    "file": {"name": "log_errors.py", "path": "/home/dtroeder/git/decision-records/dev/logging/log_errors.py"},
    "function": "main",
    "level": {"icon": "🐞", "name": "DEBUG", "no": 10},
    "line": 42,
    "message": "Handling queue item.",
    "module": "log_errors",
    "name": "__main__",
    "process": {"id": 1791761, "name": "MainProcess"},
    "thread": {"id": 140443741970432, "name": "MainThread"},
    "time": {"repr": "2024-03-07 16:11:48.831920+01:00", "timestamp": 1709824308.83192}
  }
}
```

### Option 2: Human-readable header and message, data as JSON

Edit the script (at the bottom) to format a log line with a human-readable header and message
and with a JSON data part:

```python
setup_logging(
    serialize=False,     # allowed values: True, False.
    data_format="JSON",  # allowed values: "JSON", "LOGFMT". Will be ignored if SERIALIZE==True.
)
```

```text
./dev/logging/log_errors.py  2>&1 | head -2
2024-03-07 16:09:57.899 +0100 | DEBUG | 1791400 | log_errors.main | Handling queue item. | {"item":{"a":"A"},"queue_id":"ecfa8c00"}
2024-03-07 16:09:57.899 +0100 | WARNING | 1791400 | log_errors.queue_iter | Reading queue file: Parsing queuing file: Expecting value: line 1 column 1 (char 0) | {"path":"/tmp/bbb.json","queue_id":"1dfde36e"}
```

### Option 3: Human-readable header and message, data as Logfmt

Edit the script (at the bottom) to format a log line with a human-readable header and message
and with a Logfmt data part:

```python
setup_logging(
    serialize=False,      # allowed values: True, False.
    data_format="LOGFMT",  # allowed values: "JSON", "LOGFMT". Will be ignored if SERIALIZE==True.
)
```

```text
./dev/logging/log_errors.py  2>&1 | head -2
2024-03-07 16:10:28.880 +0100 | DEBUG | 1791555 | log_errors.main | Handling queue item. | item="{'a': 'A'}" queue_id=02c82876
2024-03-07 16:10:28.880 +0100 | WARNING | 1791555 | log_errors.queue_iter | Reading queue file: Parsing queuing file: Expecting value: line 1 column 1 (char 0) | queue_id=f57ed43f path=/tmp/bbb.json
```

Both hybrid variants can be parsed by log aggregators like this:

```text
<timestamp> | <log level> | <PID> | <module> | <message> | <structured data (json/logfmt)>
```

### Reversibility

JSON and Logfmt both have weaknesses when used to encode arbitrary data:

- JSON can safely reverse any encoded object and keep the data types intact.
  There is only one small problem:
  In JSON keys of objects must be strings.
  But Python supports any hashable object as a key in a dict.
  In our example we solve this (using the `orjson` library) by encoding all non-string keys as strings.
  When reading the JSON string, we cannot use the decoded result as input for the same software anymore
  (in a debug session) because keys of type int or bool will have become strings.
  But for the more common use case of log aggregators this is not a problem.
  They'd store those keys as strings anyway.
  Non-string keys are generally a very niche problem.
- Logfmt has no problems encoding non-string keys.
  Instead, it has a general big problem decoding its own format.
  For readability and brevity it does not surround strings with quotation marks.
  When reading a Logfmt string, there is no way to distinguish a string from any other type.
  So all keys and values are converted to strings: bool, int, float, dict, list - everything is a string.

If the above is a problem or not depends on the use case.
IMHO there are very few situations that require a correct value type.
The most common use cases are reading logs by humans and indexing logs by machines.
For humans Logfmt is more efficient, for log aggregation it is enough.
If a customer uses values in structured data to create statistics and needs to interpret values as int,
float and bool, they will know what keys and values to read and how to convert they to the required types.

Customers using log aggregators profit from a standardized format like JSON.
All software products offer efficient input filters for it.
Logfmt is often also supported, but it has not been standardized.

### Decision

When structured logging is used _Option 3: Human-readable header and message, data as Logfmt_ SHOULD
be the preferred format.
The Univention logging library MAY offer the possibility to switch the message format and data encoding
to options 2 or 3.
The example code in [logging/log_errors.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/log_errors.py) shows how easy it is to implement that.

## Configuration: Human-readable JSON or Logfmt or completely JSON

The UCRVs SHOULD be stored in DCD when it is available.
So, the log format is consistent for all services and in the whole domain.
This is especially important for customers using log aggregators.

The UCR key schema is `logging/structured/<application>=<option>`.

- `<application>` is the name of the program / script / service the format should be defined for.
  - The special name `default` means that it will be defined for _all_ applications.
- `<option>` has one of the following three values:
  - `json`: _Option 1: All JSON_.
  - `hybrid-json`: _Option 2: Human-readable header and message, data as JSON_.
  - `hybrid-logfmt`: _Option 3: Human-readable header and message, data as Logfmt_.
    This is the default, when the UCRV is unset.
  - Other values are ignored and the default is used.

When the program `foo` starts, the logging library will:

1. Apply the setting stored in `logging/structured/foo` if it exists and is valid. Otherwise, continue to 2.
2. Apply the setting stored in `logging/structured/default` if it exists and is valid. Otherwise, continue to 3.
3. Apply the default for `logging/structured/default`: `hybrid-logfmt`.

## Python library

There are currently four Python libraries that can be used for structured logging with different
features, cons and pros.

### Standard library "logging" module (cookbook)

The "Python logging cookbook" describes in section ["Implementing structured logging"](https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging)
how structured log output (hybrid and pure-json) can be created using only the Python standard library.

It involves changing every log line to wrap the regular arguments of a logging call in an object,
which will be passed to the logging library.
The object will render all arguments into a single string that is passed as the message to the logging
library.

- Good, because no additional software dependencies.
- Good, because using the standard library "logging" module will result in the highest compatibility
  with other Python libraries.
- Good, because can be used to generate all three output formats (pure-json, hybrid-json, hybrid-logfmt).
- Bad, because all key-value arguments will be lost when rendered into the message string.
  There is no way for a Handler to access and forward them separately anymore,
  as log collectors like [pygelf](https://github.com/keeprocking/pygelf) do.

### python-json-logger

[python-json-logger](https://github.com/madzak/python-json-logger) is a Formatter of the standard library
logging module that also allows adding separate fields using a dedicated `extra` argument when logging.

- Good, because using the standard library "logging" module will result in the highest compatibility
  with other Python libraries.
- Good, because key-value arguments can be added to an `extra` argument and those will result in separate
  fields in the pure-json output.
- Good, because logs from third party Python libraries will automatically be included
  (as long as they use the standard library "logging" module).
- Neutral, because one additional software dependency.
- Bad, because can only be used to generate pure-json output.
- Bad, because no release since one year.
- Bad, because not available as Debian package.

There are more examples in a [stackoverflow thread](https://stackoverflow.com/questions/48170682/can-structured-logging-be-done-with-pythons-standard-library)
how pure-json log lines (non-hybrid) can be created using the standard library logging module.
_python-json-logger_ is IMHO the most promising.

### Loguru

Loguru is a library which aims to make logging in Python enjoyable.
Structured logging is only one of its features.
It comes with useful defaults,
"sinks" (handlers) are async-safe, thread-safe and multiprocessing-safe.
It offers colored output to the terminal,
nicely formatted tracebacks, optionally including local variables,
is very easy to configure,
and more.
See [Loguru docs](https://loguru.readthedocs.io/en/stable/overview.html).

Besides the `bind()` method to bind a key-value pair to logger, Loguru offers two convenience functions:

`catch()` can be used as decorator or as context manager:

```python
@logger.catch
def f(x):
    100 / x

f(0)
# <timestamp> | ERROR | An error has been caught in function 'f', process 'Main' (367), thread 'ch1' (1398):
# Traceback (most recent call last):
# ..
# ZeroDivisionError: division by zero
```

```python
filename = "/etc/shadow"
logger = logger.bind(filename=filename)

with logger.catch(message="Reading configuration file.", level="ERROR", reraise=True):
    cfg = open(filename, "r").read()

# <timestamp> | ERROR | Reading configuration file. | filename="/etc/shadow"
```

`contextualize()` is a context manager that reduces the need to create new loggers for select pieces of
code and uses contextvars for contexts unique to each thread and asynchronous task:

```python
logger.info("Before...")

with logger.contextualize(task=task_id):
    # ...
    logger.info("Working on task.")

logger.info("Doing something else.")

# <timestamp> | INFO | Before... |
# <timestamp> | INFO | Working on task. | task=4e21ab6
# <timestamp> | INFO | Doing something else. |
```

- Good, because the API is compatible with Python logging.
- Good, because can be used to generate all three output formats (json, hybrid-json, hybrid-logfmt).
- Good, because logging API is kept and all kwargs arguments of regular log messages will result in
  separate fields in the pure-json/hybrid-json/hybrid-logfmt output.
- Good, because brings additional improvements (async/thread/mp-safety, colors, better tracebacks,
  easy configurability).
- Neutral, because entirely compatible with standard logging:
  - Built-in logging Handlers can be used as Loguru sinks.
  - Standard logging messages (of other Python libraries) can be redirected into Loguru.
  - Loguru can propagate its messages to standard logging.
  - See in file [logging/univention_logging.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/univention_logging.py) how it is done.
    (Instructions and example execution in comment block at the top.)
- Good, because very active community.
- Good, because available as Debian package.
- Good, because experience using it in production exists in the UCS@school team.
- Neutral, because one additional software dependency, two for colored output.
- Bad, because Loguru only supports `{}`-style formatting.
  When migrating existing code, we'd have to replace `logger.debug("Some variable: %s", var)` with
  `logger.debug("Some variable: {}", var).`.
  Not a big problem though. For structured logging we want to replace that line with
  `logger.debug("Some variable.", var=var).` anyway.

### Logfmter

[Logfmter](https://github.com/jteppinette/python-logfmter) is a Formatter for the standard library
logging module, just like the _python-json-logger_ described above.

- Good, because using the standard library "logging" module will result in the highest compatibility
  with other Python libraries.
- Good, because key-value arguments can be added to an `extra` argument and those will result in separate
  fields in the pure-json output.
- Good, because logs from third party Python libraries will automatically be included
  (as long as they use the standard library "logging" module).
- Neutral, because one additional software dependency.
- Bad, because can only be used to generate pure-logfmt output...
  That is not even one of the options from above.
  Example log line: `at=ERROR when="2024-03-07 16:10:28.880 +0100" msg="Hello World" key1=value`
- Bad, because small community.
- Bad, because not available as Debian package.

### structlog

[structlog](https://www.structlog.org/) was designed from the start as a library for structured logging.
Log entries are dictionaries, that bind key-value pairs to Loggers.

The log entries then go through a processor pipeline that works on the dictionary.
Each processor manipulates the dictionary, e.g., adding a timestamp or call stack information etc.
The log entry is passed on to a Formatter.
Being basically a dictionary it can be rendered into a colored text for the terminal, JSON, Logfmt or
be forwarded to a log aggregator or a database.
The result can be output to a terminal, file or another logging library.

Loggers and contexts are by default thread-safe and can be configured to not block in async applications.

Structlog is _highly_ configurable.
So much, that it's a bit daunting.
But it's very well documented.

For example by default it does not have log levels.
But a processor exists that adds the standard logging library levels and behavior.

Structlog can receive from and send to the standard logging library.
It's a bit difficult to configure, but it's well documented.

- Good, because the API can be made compatible with Python logging.
- Good, because can be used to generate all three output formats (json, hybrid-json, hybrid-logfmt).
- Good, because logging API is kept and all kwargs arguments of regular log messages will result in
  separate fields in the pure-json/hybrid-json/hybrid-logfmt output.
- Good, because brings additional improvements (async/thread-safety, colors, better tracebacks,
  high configurability).
- Good, because can be used as drop-in replacement for standard logging.
- Neutral, because can be made mostly compatible with standard logging:
  - Standard logging messages (of other Python libraries) can be redirected into structlog for formatting
    and then be returned for output to standard logging.
  - Structlog can propagate its messages to standard logging.
- Good, because very active community.
- Good, because available as Debian package.
- Neutral, because one additional software dependency, two for colored output.
- Bad, because getting structlog to play nicely with 3rd party software using standard logging is very
  complex to configure.

## Decision

[Loguru](https://loguru.readthedocs.io/) and [structlog](https://www.structlog.org/) are logging
libraries meant to replace the Python logging library.
[Logfmter](https://github.com/jteppinette/python-logfmter) and [python-json-logger](https://github.com/madzak/python-json-logger) are "plugins" (Formatters) for the standard libraries
logging module.

The chosen library must not only fulfill the requirements in this ADR (on structured logging),
but also those listed in the other ADRs on logging:
[0004 Logging Topology](0004-logging-topology.md), [0005 Log Levels](0005-log-levels.md),
[0006 Log Format](0006-log-format.md) and [0007 Log Messages](0007-log-messages.md).

Structlog focuses primarily on the data part of structured logging, but does not prevent regular logging.
It can be combined with the standard logging library for writing output and with a 3rd party library to
write to the terminal.
Structlog support out-of-the-box pure-json, pure-logfmt, hybrid-json and hybrid-logfmt.

Loguru is a general purpose logging library with batteries included that focuses on developer
friendliness.
Out-of-the-box, besides regular logging, its own structured logging output only support pure-json,
but it can be configured to generate all three output formats
(see example script [logging/log_errors.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/log_errors.py)).

Using Logfmter and python-json-logger the standard library can log pure-logfmt or pure-json.
The recipie in section _Standard library "logging" module (cookbook)_ describes a (hacky) way to also
create hybrid output.

- Disqualified: Logfmter and python-json-logger.\
  They do not produce human friendly hybrid output.
  (They are also not available in Debian, but I think Univention could fix that.)
- Third place goes to Python Logging Cookbook solution.\
  While at first glance it seemed to be the most standard way, its manipulation of the logging input
  using a wrapper _in the client code_ is actually pretty destructive, making post-processing and code
  maintenance harder.
- Second place goes to structlog.\
  It has all desired features.
  Its data-centric way and high configurability warms my nerdy heart.
  But it is also why it missed the first place.
  Assume that the Univention logging library does all the complex configuration to cover the requirements
  of all ADRs.
  When you program a software that wants to do something that extends the defaults - say add a file
  output additionally to the STDERR output - you're in for an hour-long read of the documentation.
- The winner is Loguru.\
  It has all desired features,
  and brings additional useful features that are very welcome,
  all while being easier to configure than any of the alternatives (including the standard logging library).
  See in file [logging/univention_logging.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/univention_logging.py) how easy it was to implement
  most of what is required.
  It is highly compatible with the standard library logging module.
  Besides the standard logging library it has the highest likelihood of new developers already knowing
  it, and the UCS@school team is already using it in production code.
