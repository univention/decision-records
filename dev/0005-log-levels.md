# Log Levels

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
- related ADRs: [0004 Logging Topology](0004-logging-topology.md), [0006 Log Format](0006-log-format.md), [0007 Log Messages](0007-log-messages.md), [0008 Structured Logging](0008-structured-logging.md)

---

[[_TOC_]]

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](https://git.knut.univention.de/univention/internal/research-library/-/blob/07df7be3a61f5eeab776309f19c3abb7c943ff44/research/logging_concept/README.md)
describes, besides a logging architecture, what and how to log: message content and metadata.

This ADR specifies what log levels exist in UCS' components, their purpose, and how to configure them.

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0006 Log Format](0006-log-format.md) defines the content and format of log messages.
- [0007 Log Messages](0007-log-messages.md) defines the content and metadata of log messages.
- [0008 Structured Logging](0008-structured-logging.md) defines the use of structured logging.

## Decision Drivers

- Homogeneity…
  - of used log levels.
  - of how sensitive data is handled.
  - of reading and analysing logs (for humans and machines).
- Simplicity of configuration…
  - of logging library (for developers).
  - for operator.

## Log levels

Six log levels exist.
Univention developers MUST use them according to the following rules.
See ADR [0007 Log Messages](0007-log-messages.md) for the content of messages and examples at each log level.

- `TRACE`: Information about a system-internal event or state without business context.
  Audience: developer.
  - When the used logging library doesn't support a native `TRACE` level, use the `DEBUG` level instead.
- `DEBUG`: Information about a technical event or state with business context. Audience: support.
- `INFO`: Information about a successful application/business event. Audience: operator.
- `WARNING`: Information about a potential danger, an unexpected error that could be handled by the
  software, reduced performance or feature set. Audience: operator.
  - Do not use it for _expected_ problems, like wrong user input, as that is not an error of the
    software. Log expected events at `DEBUG` or `INFO` level, except if they pose a danger.
- `ERROR`: Information about an erroneous event of any (internal to business) level that cannot be
  handled automatically but does not hinder the continued operation of the service as a whole.
  Audience: operator.
- `CRITICAL`: Information about an erroneous event that affects not only the current transaction
  but all future transactions, too. Audience: operator.

The creation of additional log levels is discouraged.
We suggest adding additional labels to log lines instead.
When found in other languages or libraries level `NOTICE` should be mapped to `INFO` and level `FATAL`
should be mapped to `CRITICAL`.

### Journald

Journald uses Syslog priorities to qualify log messages.

The above log levels can be mapped to Syslog priorities (`man 3 syslog`) following [RFC 5424 section 6.2.1](https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1) in the following way:

- `TRACE` and `DEBUG` → Priority `7` (Debug)
- `INFO` → Priority `6` (Informational)
- `WARNING` → Priority `4` (Warning)
- `ERROR` → Priority `3` (Error)
- `CRITICAL` → Priority `2` (Critical)

Syslog priorities `0` (Emergency), `1` (Alert) and `5` (Notice) are not used.

Transporting log level from the shell and from Python into the journald database is tricky.
It is discussed in sections _Preserving log level of messages from..._ in
ADR [0004 Logging Topology](0004-logging-topology.md).

## Configuration of log levels

Often it is enough to configure one log level for an entire application.
But for complex software projects it can be beneficial for operators and developers to have more
fine-grained control.
With hierarchical loggers, Python logging frameworks already have the required infrastructure.

A to-be-written Univention logging library SHOULD offer operators a consistent and effortless
configuration of an application-wide log level.
It SHOULD also give engineers the ability to configure a log level per submodule.

A UCR key schema is used to store the default log level of each process
and individual log levels for each of their submodules.

The UCRVs MAY be stored in DCD when it is available.
So, the log levels are consistent when a service is deployed multiple times in the domain.
Using DCD additionally allows services to reconfigure themselves when values change without restarting.

The UCR key schema is `logging/level/<application>/<logger>=<level>`.

- `<application>` is the name of the program / script / service the log level(s) should be defined for.
  - The special name `default` means that it will be defined for _all_ applications.
- `<logger>` is the name of a Python package or module,
  e.g. `univention.admin.handlers.users.user` (a single module) or `univention.admin` (a package which includes all handlers, utils, etc.).
  Logger names form a period-separated hierarchie (like the Python package hierarchy) where higher level loggers receive the output of lower level loggers (see [Python logging documentation](https://docs.python.org/3.12/library/logging.html#logger-objects)).
  - The special name `default` means that it defines the applications default log level,
    technically the log level of the `root` logger.

| UCR key                                  | Meaning                                                                                                                               |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `logging/level/default=<level>`                | The default log level of _all_ applications (program / script / service), when no dedicated configuration exists. Defaults to `INFO`. |
| `logging/level/default/<logger>=<level>`       | The log level of the logger named `<logger>` (e.g. `univention.admin.utils`), when used in _any_ application.                         |
| `logging/level/<application>/default=<level>`  | The default log level of the application `<application>`.                                                                             |
| `logging/level/<application>/<logger>=<level>` | The log level of the logger named `<logger>` (e.g. `univention.admin.handlers.users.user`), when used in application `<application>`. |

When the program `foo` starts, the logging library will apply values from top to bottom,
skipping missing keys:

1. Set the `root` logger to `logging/level/default=<level>`.
2. For each `<module>` in `logging/level/default/<module>=<level>` create a logger and set its log level.
3. Set the `root` logger to `logging/level/foo/default=<level>`.
4. For each `<module>` in `logging/level/foo/<module>=<level>` create a logger and set its log level.

All logger instances are singletons.
So "creating" a logger a second time is just modifying the previously created one.

Creating a logger instance that is never used (e.g., for the Python module `univention.mail.dovecot` in a
UCS@school script), is a tiny waist of memory, but nothing else.
Still, that feature should be used with care.

Example:

- UCRVs:
  - `logging/level/default=INFO`
  - `logging/level/foo/default=WARNING`
  - `logging/level/foo/univention.admin.handlers=DEBUG`
- The application `foo` will generally log at level `WARNING` and above (`WARNING`, `ERROR` and `CRITICAL`).
    Except when a UDM handler (e.g. `univention.admin.handlers.users.user` for UDM module `users/user`) logs.
    All modules and packages below `univention.admin.handlers` will log at `DEBUG` level.
- All other applications will log at level `INFO` and above (`INFO`, `WARNING`, `ERROR` and `CRITICAL`).
  When they use a module below `univention.admin.handlers` they will also log at level `INFO` and above.

Setting the log level of a package for all our applications (`logging/level/default/<logger>=<level>`) will happen very rarely.
A setting like `logging/level/default/requests.packages.urllib3=DEBUG` is _dangerous_,
as it'll make _all_ our Python applications log HTTP requests at `DEBUG` level, including sensitive data.
A valid and good use case is to enable such a UCRV for one of our own libraries during a Jenkins run.
E.g.:

```shell
ucr set logging/level/default/ucsschool.lib.models=DEBUG
ucs-test -s ucsschool
```

---

If an application wishes to support dynamic reconfiguration (without application restart) of its log
levels, the logging library MAY offer to register a callback for UCR keys with DCD.
When a monitored key changes, the library simply executes the four steps mentioned earlier again.

## Proof of concept

The configurability per app and module has been implemented in a proof of concept logging library:
[univention_logging.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/univention_logging.py).

There is also a package hierarchie and a test script that can be executed to verify its functionality: [level_conf.py](https://git.knut.univention.de/univention/internal/research-library/-/blob/main/research/logging_concept/adr_poc/level_conf.py):

It simulates the following situation:

```text
### Python packages:
uni
├── __init__.py
├── adm
│   ├── __init__.py
│   ├── hand
│   │   ├── __init__.py
│   │   ├── groups.py
│   │   └── users.py
│   └── hook
│       ├── __init__.py
│       └── captain.py
├── listen
│   ├── __init__.py
│   └── er.py
└── radius
    ├── __init__.py
    └── net.py

### UCRVs:
ucr set \
    logging/level/default=INFO
    logging/level/default/uni=INFO
    logging/level/level_conf.py/default=TRACE
    logging/level/level_conf.py/uni.adm.hand=DEBUG
    logging/level/level_conf.py/uni.listen=WARNING
    logging/level/level_conf.py/uni.radius=ERROR
    logging/level/level_conf_warn.py/default=WARNING
```

It then changes the UCRVs:

```text
ucr set   logging/level/level_conf.py/uni.adm.hand.groups=ERROR
ucr unset logging/level/level_conf.py/uni.radius
```

And finally simulates being a different script (`level_conf_warn.py`)
for which a UCRV had configured to log at WARNING (`logging/level/level_conf_warn.py/default=WARNING`).

```text
./level_conf.py 
*** Starting log level test in 'level_conf.py'.
*** Will configure logging, then call in order:
  <this script>.do_stuff()
  uni.adm.hand.groups.do_stuff()
  uni.adm.hand.users.do_stuff()
  uni.adm.hook.captain.do_stuff()
  uni.listen.er.do_stuff()
  uni.radius.net.do_stuff()
*** The log levels have been configured in the following way:
  root logger: 'TRACE'
  'uni':  'INFO'
  'uni.adm.hand':  'DEBUG'
  'uni.listen':  'WARNING'
  'uni.radius':  'ERROR'
2024-03-13 10:39:47.558 +0100 |   DEBUG | 2278639 | level_conf.do_stuff | Debug in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.558 +0100 |    INFO | 2278639 | level_conf.do_stuff | Info in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.558 +0100 | WARNING | 2278639 | level_conf.do_stuff | Warning in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.558 +0100 |   ERROR | 2278639 | level_conf.do_stuff | Error in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.558 +0100 |   DEBUG | 2278639 | groups.do_stuff | Debug in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.558 +0100 |    INFO | 2278639 | groups.do_stuff | Info in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.559 +0100 | WARNING | 2278639 | groups.do_stuff | Warning in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |   ERROR | 2278639 | groups.do_stuff | Error in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |   DEBUG | 2278639 | users.do_stuff | Debug in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |    INFO | 2278639 | users.do_stuff | Info in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.559 +0100 | WARNING | 2278639 | users.do_stuff | Warning in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |   ERROR | 2278639 | users.do_stuff | Error in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |    INFO | 2278639 | captain.do_stuff | Info in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.559 +0100 | WARNING | 2278639 | captain.do_stuff | Warning in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.559 +0100 |   ERROR | 2278639 | captain.do_stuff | Error in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.560 +0100 | WARNING | 2278639 | er.do_stuff | Warning in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.560 +0100 |   ERROR | 2278639 | er.do_stuff | Error in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.560 +0100 |   ERROR | 2278639 | net.do_stuff | Error in uni.radius.net.do_stuff() | 
*** Changing level (via UCR;) of 'uni.adm.hand.groups' to 'ERROR' and 'uni.radius' to default...
*** The log levels are now configured in the following way:
  root logger: 'TRACE'
  'uni':  'INFO'
  'uni.adm.hand':  'DEBUG'
  'uni.adm.hand.groups':  'ERROR'
  'uni.listen':  'WARNING'
*** Executing functions...
2024-03-13 10:39:47.564 +0100 |   DEBUG | 2278639 | level_conf.do_stuff | Debug in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.564 +0100 |    INFO | 2278639 | level_conf.do_stuff | Info in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.564 +0100 | WARNING | 2278639 | level_conf.do_stuff | Warning in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.564 +0100 |   ERROR | 2278639 | level_conf.do_stuff | Error in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.564 +0100 |   ERROR | 2278639 | groups.do_stuff | Error in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.564 +0100 |   DEBUG | 2278639 | users.do_stuff | Debug in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.564 +0100 |    INFO | 2278639 | users.do_stuff | Info in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.564 +0100 | WARNING | 2278639 | users.do_stuff | Warning in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |   ERROR | 2278639 | users.do_stuff | Error in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |    INFO | 2278639 | captain.do_stuff | Info in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.565 +0100 | WARNING | 2278639 | captain.do_stuff | Warning in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |   ERROR | 2278639 | captain.do_stuff | Error in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.565 +0100 | WARNING | 2278639 | er.do_stuff | Warning in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |   ERROR | 2278639 | er.do_stuff | Error in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |    INFO | 2278639 | net.do_stuff | Info in uni.radius.net.do_stuff() | 
2024-03-13 10:39:47.565 +0100 | WARNING | 2278639 | net.do_stuff | Warning in uni.radius.net.do_stuff() | 
2024-03-13 10:39:47.565 +0100 |   ERROR | 2278639 | net.do_stuff | Error in uni.radius.net.do_stuff() | 
*** Changing name of application (as if this were another file / app / service) to one that has
    been configured (via UCR;) to log at level WARNING...
*** Executing functions...
2024-03-13 10:39:47.569 +0100 | WARNING | 2278639 | level_conf.do_stuff | Warning in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.569 +0100 |   ERROR | 2278639 | level_conf.do_stuff | Error in level_conf_aaa.py::do_stuff() | 
2024-03-13 10:39:47.569 +0100 | WARNING | 2278639 | groups.do_stuff | Warning in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.569 +0100 |   ERROR | 2278639 | groups.do_stuff | Error in uni.adm.hand.groups.do_stuff() | 
2024-03-13 10:39:47.569 +0100 | WARNING | 2278639 | users.do_stuff | Warning in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.569 +0100 |   ERROR | 2278639 | users.do_stuff | Error in uni.adm.hand.users.do_stuff() | 
2024-03-13 10:39:47.570 +0100 | WARNING | 2278639 | captain.do_stuff | Warning in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.570 +0100 |   ERROR | 2278639 | captain.do_stuff | Error in uni.adm.hook.captain.do_stuff() | 
2024-03-13 10:39:47.570 +0100 | WARNING | 2278639 | er.do_stuff | Warning in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.570 +0100 |   ERROR | 2278639 | er.do_stuff | Error in uni.listen.er.do_stuff() | 
2024-03-13 10:39:47.570 +0100 | WARNING | 2278639 | net.do_stuff | Warning in uni.radius.net.do_stuff() | 
2024-03-13 10:39:47.570 +0100 |   ERROR | 2278639 | net.do_stuff | Error in uni.radius.net.do_stuff() | 

```
