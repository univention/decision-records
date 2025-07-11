# Logging Topology

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
- approval level: medium (see [explanation](https://git.knut.univention.de/univention/decision-records/-/blob/main/adr-template.md?ref_type=heads&plain=1#L19) | Decisions of medium scope, i.e. minor adjustments to the platform or strategic decisions regarding specifications. The approval of the product owner is requested and the decision is made jointly.)
- coordinated with: **TODO** {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- source: [Logging concept](logging/logging_concept.md)
- scope: ALL Univention software products.
  New products in Docker containers or in the host on UCS 5.2 MUST adhere to the ADR immediately.
  Existing software MUST be migrated gradually in errata and point releases of UCS 5.2.
- resubmission: -
- related ADR: [0005 Log Levels](0005-log-levels.md), [0006 Log Format](0006-log-format.md), [0007 Log Messages](0007-log-messages.md), [0008 Structured Logging](0008-structured-logging.md)

---

[[_TOC_]]

---

This ADR is uncommon in structure because
a) most decisions have already been made during the production of the concept paper
(see discussions in [merge request](https://git.knut.univention.de/univention/internal/research-library/-/merge_requests/19)),
and b) it has multiple topics.

The intention of this ADR is to
a) create binding decisions on technical details,
and b) for the combination of the decisions to produce a coherent result.

---

## Context and Problem Statement

The [logging concept accepted on 21.02.2024](logging/logging_concept.md)
describes a topology where all log messages in one way or the other end up in a hosts local journald
database `(*1)`.
It also describes different ways for operators to access the log messages in that database.

![Logging topology](logging/topology.png?ref_type=heads&inline=false "Logging topology")

This ADR specifies how UCS' systems and components must be configured or modified to realize this logging
architecture:

- Applications (log sources / producers)
- Forwarders
- Persistence
- Extractors and viewers
- Configurability

Different aspects of logging have been split into separate ADR:

- [0004 Logging Topology](0004-logging-topology.md) defines the logging architecture (what happens with log messages).
- [0005 Log Levels](0005-log-levels.md) defines what log levels exist and how to use them.
- [0006 Log Format](0006-log-format.md) defines the content and format of log messages.
- [0007 Log Messages](0007-log-messages.md) defines the content and metadata of log messages.
- [0008 Structured Logging](0008-structured-logging.md) defines the use of structured logging.

---

`(*1)` Please be aware that journald is not used in Kubernetes.
In Nubus log messages are persisted differently.
Sending logs to STDOUT/STDERR is best practice in Kubernetes and supported natively.
Sending logs _directly_ to journald should be avoided in Univention products, because they will have to
be adapted to run in Kubernetes / Nubus.

## Decision Drivers

- Homogeneity…
  - of used logging libraries and APIs.
  - of logging target ("Handler") configuration.
  - of reading and analysing logs (for humans and machines).
- Simplicity of configuration…
  - of logging library (for developers).
  - for operator (log level, log rotation).
- Compatibility of solutions…
  - for UCS software running in the UCS host and in an App Center Docker container.
  - for UCS and Nubus.
- Support for "interactive" output by…
  - CLI prompting user response.
  - CLI informative output for user _additionally_ to log.
  - CLI output for use in a UNIX shell pipe.
- Accessibility and searchability of log messages…
  - interactively with a CLI.
  - non-interactively by USI.
  - through an API to realize a UMC module (no concrete plans, just an idea).
  - by a log collector for transport into a customers log aggregator.

## Emitting logs

### Log targets

All Univention software, regardless of where it is installed (host, container)
and its implementation language (C, Python, shell),
SHOULD emit its log messages either to STDERR or send them directly to journald.

Non-interactive software MUST prefer logging to STDERR.

The output will be captured by the spawning process (usually systemd or Docker)
and SHOULD be forwarded to journald in UCS and whatever is configured in Kubernetes.

In Python a logging library MUST be used in production code.
The usage of `print()` for logging is not allowed.

A Univention logging library will be created that loads configuration, sets up Handlers etc.
It must have an interface compatible with Python logging.

Logging directly to journald SHOULD be avoided (except for interactive shell scripts, see below).
For services in certain situation (e.g., multiprocessing services) this possibility can be useful.
But it is not an option for software that runs in Kubernetes (Nubus)!
In Python `systemd.journal.JournalHandler` can be used to log directly to journald,
and `systemd-cat` in a shell.

### Usage of STDOUT in CLI

CLI that wish to emit text to be read by users or to be used by other software
(e.g., in a shell pipe), MUST send that text to STDOUT.
That text will _not_ be logged, unless _also_ sent to STDERR.

To make bash shell scripts write STDOUT to the terminal (or a pipe) and STDERR to journald:

```shell
#!/bin/bash

exec 2> >(systemd-cat  -t $(basename "$0"))

echo "This text goes to STDOUT (the terminal or a shell pipe)."
echo "This text will be logged by journald." >&2
echo "This text goes to both (STDOUT and journald)." | tee /dev/stderr
```

### Multi-processing applications

All processes of applications that consist of multiple processes (like the UMC and the UDM REST API)
SHOULD log to STDERR or if that's not possible to journald.

The main process (the one that was initially started) SHOULD pass on its file descriptors for STDOUT and
STDERR to the spawned process.
This way the STDOUT and STDERR of all processes will be sent to systemd or Docker.
Those will forward the output to journald or wherever Kubernetes sends it.

As the output of all processes will be merged into one stream, IDs MUST be added to every log line.
They can be used to split the logs later and to follow requests.
Typical IDs will be the process' ID and the request ID.

In the case of the UMC the name of the UMC module MUST also be logged.

```text
<timestamp> <log level> <UMC module> <process ID> <request ID> <message> | <structured data (logfmt)>
# or
<timestamp> <log level> <message> | umc-module='<UMC module>' request-id='<request ID>' pid=<process ID> <more structured data (logfmt)>
```

If a setup with the inheritance of STDOUT/STDERR is not possible then all processes MUST send their
logs directly to journald.
Use the Python `setproctitle` module to set a useful process name in each process.
It will end up in a dedicated key in journald that filters can use.
Avoid sending logs directly to journald as it doesn't exist in Kubernetes.

### Preserving log level of messages from the shell

The default log level for journald is INFO.
When the systemd option `SyslogLevelPrefix` is enabled (default), we can make use of the
[sd-daemon logging prefix](https://www.freedesktop.org/software/systemd/man/latest/sd-daemon.html)
to log at different log levels.
The journald log levels correspond to the Syslog priorities (`man 3 syslog`) following
[RFC 5424 section 6.2.1](https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1):

```shell
echo "<0>This text will be logged at priority 0 (Emergency)." >&2
echo "<1>This text will be logged at priority 1 (Alert)." >&2
echo "<2>This text will be logged at priority 2 (Critical)." >&2
echo "<3>This text will be logged at priority 3 (Error)." >&2
echo "<4>This text will be logged at priority 4 (Warning)." >&2
echo "<5>This text will be logged at priority 5 (Notice)." >&2
echo "<6>This text will be logged at priority 6 (Informational)." >&2
echo "<7>This text will be logged at priority 7 (Debug)." >&2
```

Use `journalctl --output verbose --output-fields MESSAGE,PRIORITY -n 10` to show the last 10 messages
recorded by journald including the Syslog priority.
Use `--no-pager` to not have a pager,
`-g <pattern>` to include only messages with a certain text,
and `-f` to make it keep printing new messages as they appear.

According to [section "Log levels" of the logging concept](logging/logging_concept.md#log-levels)
only six log levels should be used by Univention software: TRACE, DEBUG, INFO, WARNING, ERROR and
CRITICAL.
They MUST be mapped to Syslog priorities in the following way:

- `TRACE` and `DEBUG` → Priority `7` (Debug)
- `INFO` → Priority `6` (Informational)
- `WARNING` → Priority `4` (Warning)
- `ERROR` → Priority `3` (Error)
- `CRITICAL` → Priority `2` (Critical)

Syslog priorities `0` (Emergency), `1` (Alert) and `5` (Notice) are NOT used.

We should probably create functions for logging in our shell library like this:

```shell
ulog_t () {  # logs at TRACE level: mapped to DEBUG level
    ulog_d "$1"
}
ulog_d () {  # sends $1 to STDERR->journald with priority 7 (Debug)
    echo "<7>$1" >&2
}
ulog_i () {  # sends $1 to STDERR->journald with priority 6 (Informational)
    echo "<6>$1" >&2
}
ulog_w () {  # sends $1 to STDERR->journald with priority 4 (Warning)
    echo "<4>$1" >&2
}
ulog_e () {…}  # ERROR
ulog_c () {…}  # CRITICAL
```

See example shell script [shell-sd-daemon-prefix.sh](logging/shell-sd-daemon-prefix.sh).

### Preserving log level of messages from Python

Messages of Python applications started in systemd units written to STDOUT or STDERR end up at priority
6 (INFO), as that's the default for both.

This can be change using the same prefix mechanics (systemd `SyslogLevelPrefix`):

```python
print("<3>python to stdout 3")  # will be logged at prio 3 (ERROR)
print("<4>python to stderr 4", file=sys.stderr)  # will be logged at prio 4 (WARNING)
```

It doesn't matter if STDOUT or STDERR is used.
They have the same default priority.
And when the prefix is used, its value is applied.

Our Python logging library SHOULD use this mechanic to preserve the Python log level as
Syslog priority when writing to STDERR, so it ends up correctly in the journald database.
The Univention logging libraries for shell and Python SHOULD offer a configuration to disable the
prefixing, as it's useless when logging from Docker containers in both UCS and Nubus (see section
_Preserving log level of messages from Docker_).

An example showcasing the prefix mechanics with a systemd unit and a "service" is attached:
[service-sd-daemon-prefix.service](logging/service-sd-daemon-prefix.service),
[service-sd-daemon-prefix.py](logging/service-sd-daemon-prefix.py).

See in file [logging/univention_logging.py](logging/univention_logging.py) how it is done as a library:

- Run `./logging/log_errors.py` to see the colored output without prefix in the terminal.
- Run `./logging/log_errors.py 2>&1 | tee /dev/null` to see that the prefix is added for a non-terminal.
- Run `./logging/log_errors.py 2>&1 | systemd-cat` to redirect the (prefixed) output to journald.
  - Use `journalctl --output verbose --output-fields MESSAGE,PRIORITY --no-pager -n 10` to verify
    the entries have the correct Syslog priority in the journald database.

### Preserving log level of messages from Docker

Sadly the Docker journald and syslog logging drivers do not support the prefix mechanism
([Github issue](https://github.com/docker/for-linux/issues/127),
[Docker forums](https://forums.docker.com/t/apply-levels-to-log-messages-forwarded-to-journald/37810)).
It is not possible to configure _anything_ regarding the log level for it
([Journald logging driver docs](https://docs.docker.com/config/containers/logging/journald/)).
Only the default log level for all Docker logs can be set in the `daemon.json` with the `log-level` key.

This leaves us with only a few options:

1. All log messages from Docker containers have the same severity in journald.

   If we add the log level to every message (with the metadata on the left side or as key-value pair on
   the right side), readers can parse it.
   That works well for log aggregators as they have input tokenizers they apply before adding a log
   message to their own database.
   The CLI `journalctl` has the option `-g` that allows searching in the message text using regular
   expressions.
   (In UCS 5.0 journalctl is `Compiled without pattern matching support`, so a pipe and `grep` has to be
   used. In UCS 5.2 journalctl has pattern matching support.)
   So an operator can use for example
   `journalctl CONTAINER_NAME=epic_lalande -g '(WARNING|ERROR|CRITICAL)'`
   to find all messages from a Docker container with severity WARNING or higher.
   The Python library lacks the regular expression feature, supports only exact matching.
   A workaround would have to be found if the idea of a
   [UMC "Logs" module](logging/logging_concept.md#umc-logs-module)
   would be implemented.

2. Univention Docker applications use a log extractor (in a sidecar container).

    Log extractors are often used as "agents" of log aggregators that read log files from a local disk
    and send their content over the network to a central log aggregator.
    Unfortunately there is no log extractor that sends to journald.
    There are `systemd-journal-remote` and `systemd-journal-upload` that could be combined to create a
    forwarding solution.
    But that would require a journald instance with a volume to store a journal
    and a client that sends its logs there.
    Besides that being an overcomplicated sidecar, the Python `JournalHandler` does not support
    connecting to remote journald instances.
    Thus, a local journald in the main container would be required.
    That would require an init system (systemd) in the main container and then systemd-journal-upload
    could also run there - no sidecar or systemd-journal-remote needed anymore.

3. Univention Docker applications use a custom log forwarding solution.

    As a proof of concept I have written a Syslog server
    ([syslog2systemd_server.py](logging/syslog2systemd_server.py)) that parses and forwards messages to journald.
    It extracts the Syslog "severity" (log level), "facility" and "ident" (application ID) from the
    message and sends it together with the message directly to journald.
    It can easily be extended to also extract key-value pairs from structured logging, passing them to
    journald, where they will be stored for indexed searching.
    The server is accompanied by a performance test.
    See the comment block at the top of
    [syslog2systemd_performance_test.py](logging/syslog2systemd_performance_test.py) for the results of a run on
    a UCS 5.0 virtual machine.
    Using a Syslog server allows the Docker application to simply use the Python builtin
    `logging.handlers.SysLogHandler` without compromising on metadata.

#### Pros and cons of the options

##### All log messages from Docker containers have the same severity in journald

- Good, because logging to STDERR is best practice for Docker applications.
- Good, because logging to STDERR does not add any additional software or service dependency.
- Good, because the same configuration works for UCS and Nubus.
- Bad, because log levels are _not_ retained and thus journalctl cannot filter by log level.
  Thus, operators would have to sift through more output than desired and filter the output again,
  making the experience as awkward as reading listener or UMC logs when the debug level is set to `4`.
- Bad, because when log extractors read and forward logs to log aggregators their operators
  will have to add an input parser to overwrite the log level read from journald
  with the one parsed from the message text.

##### Univention Docker applications use a log extractor (in a sidecar container)

- Good, because using official journald components means having upstream support.
- Good, because the application could behave like in the host, writing to STDERR and preserving the log
  level (see section _Preserving log level of messages from Python_).
- Bad, because log levels are _not_ retained and thus journalctl cannot filter by log level.
- Bad, because a container with an init system (systemd) and two services (journald and
  systemd-journal-upload) is not best practice.
- Bad, because the application depends on an additional external service.
- Bad, because different configurations are necessary for UCS and Nubus.

##### Univention Docker applications use a custom log forwarding solution

- Good, because log levels are retained and thus journalctl can filter by log level.
- Good, because the application has no additional dependency (built-in Syslog logging handler).
- Good, because the application could behave normally, would not even have to use the `sd-daemon` prefix,
  as the Syslog logging handler support transporting the severity natively.
- Good, because the "syslog2systemd" server could easily be extended to also extract key-value pairs from
  structured logging, passing them to journald, where they will be stored for indexed searching.
  Thus, operators will not only be able to filter by log level, but also by request ID or username.
- Neutral, because this is exactly what log collectors like Logstash, Fluentbit, etc. do.
- Bad, because the application depends on an additional external service.
- Bad, because a new critical component has to be created that Univention has to maintain.
- Bad, because different configurations are necessary for UCS and Nubus.

##### Decision Outcome

Option two (log extractor) is not feasible, as starting an init system and multiple services in a
container is against BSI basic protection rules.

In my opinion, the comparison between option one (STDERR / all messages have same severity) and
option three (custom forwarding solution) boils down to a weighting between:

- Fewer dependencies but less useful logs than from applications in the host.
  - +homogeneity(devs), -homogeneity(operators), +simplicity of configuration(devs),
    +compatibility, -searchability
- Maintaining a custom log collector but gaining a rich log reading experience.
  - -homogeneity(devs), +homogeneity(operators), -simplicity of configuration(devs),
    -compatibility, +searchability

Please be aware that software in the host logging to STDERR does _not_ get its key-value pairs from
structured logging stored for indexed searching.
It would have to log directly to journald for that.
This could be accomplished by using the JournalHandler.
When the same software is used in Kubernetes it must instead log to STDERR.

The Univention logging library that will be created anyway (for various consistency reasons mostly found
in the ADR [0005 Log Messages](0005-log-messages.md)) can make the choice of logging handler configurable
for operators and transparent to developers.
The configuration would default in UCS to journald and in Nubus to STDERR.

While a solution that offers the best result in each environment sounds tempting,
and it is sad to not being able to use the full search feature set of journald,
we should choose for now the first option for Docker applications (STDERR / all messages have same
severity).

A reduction of complexity and maintenance cost should be the first priority in the Univention
development department right now.

There is no loss of comfort for readers (both of customers and Univention Dev, PS and Support) compared
to today, where the log level is also only available as text.

When or where the need arises to store severity and structured data for indexed searching,
it can be added later without changes to the application
by adding the configurability to the logging library
or by using a log aggregator that parses its input.

## Forwarding / Collecting

In UCS, software that starts applications MUST forward the applications STDOUT and STDERR to journald.

In Nubus it is enough to ensure the applications STDOUT and STDERR reach the container runtime.
Further processing is the responsibility of the operator.

The following is only valid for UCS:

- Services that are installed in a UCS host system MUST be started by systemd.
  No changes are necessary for those cases.
  - Services that are started by other init systems or process managers for historical or upstream
    reasons MUST either be migrated to systemd, or if that is not feasible it MUST be ensured in another
    way that the services' STDOUT and STDERR are sent to journald.
- Software that runs in a Docker container is started by the Docker daemon.
  The Docker daemon MUST be configured to use the `journald` Docker logging driver.
  Issues have already been created to implement the necessary changes:
  - [Bug 56058 - UCS should save Docker logs to journald](https://forge.univention.org/bugzilla/show_bug.cgi?id=56058)
  - [Bug 56131 - Appcenter should set labels when starting Docker container](https://forge.univention.org/bugzilla/show_bug.cgi?id=56131)
  - [Bug 56130 - incompatible defaults in UCR template daemon.json](https://forge.univention.org/bugzilla/show_bug.cgi?id=56130)

The following is valid for both UCS and Nubus:

- Univention software in Docker containers MUST log to STDERR or an alternative solution presented in
  section _Preserving log level of messages from Docker_.
- Third party software in Docker containers may send its log messages to a log collector in a sidecar.
  In UCS the log collector in the sidecar MUST be configured to forward the logs to STDOUT/STDERR.
  In Nubus that configuration is the responsibility of the operator.
- Third party software in Docker containers may store log files on a volume.
  It is RECOMMENDED that in such cases a sidecar container with a log collector / forwarder is started.
  It reads the logs from the primary container using a shared volume and forwards them to STDOUT/STDERR.
  Something like:

  ```shell
  docker run --name myapp --rm -v /var/log:/var/log:ro busybox:latest tail -F /var/log/myapp.log
  ```

### Performance

Logs to be stored in journald using to different ways have been benchmarked on a UCS 5.0 virtual machine.
Instruction for installing and running are in the comment block of each file.
For convenience the output of a run is also in the comments.

1. A systemd service writing to STDERR: [py-stderr-performance.py](logging/py-stderr-performance.py)
2. A Python script writing directly to journald using `systemd.journal.send()`:
  [py-journald-send-performance.py](logging/py-journald-send-performance.py)
3. A Python script writing directly to journald using `systemd.journal.JournalHandler`:
  [py-journald-log-performance.py](logging/py-journald-log-performance.py)
4. A Python script in a Docker container logging to the custom Syslog daemon that forwards to journald:
  [syslog2systemd_performance_test.py](logging/syslog2systemd_performance_test.py)

```text
1. Logged 10000 messages to STDERR without delay between messages in 0.407 sec (24.6/ms) [..].
2. Logged 10000 messages without delay between messages using journald.send() in 0.715 sec (14.0/ms) [..].
3. Logged 10000 messages without delay between messages using JournalHandler in 3.174 sec (3.2/ms) [..].
4. Bulk:  Logged 10000 messages with 0.1 ms delay between messages to Syslog in 1.876 sec (5.3/ms) [..].
4. Burst: Logged 100 messages without delay between each message to Syslog in 7.663 ms (13.1/ms) [..].
```

## Persisting

The primary storage for log messages are the journald databases.
rsyslog can be used to extract clear text files from them.
Logrotate is used to archive and purge clear text log files.

UCS operators are accustomed to configure logrotate to enforce their organizations data privacy
protection policy.
The UCS manual MUST be extended to contain instructions how those policies can be implemented for
journald.

Journald supports size-based and time-based policies for automatically purging old entries (see
[journald.conf man page](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html)).
Keeping entries from different sources for individual lengths of time is not supported.
Thus, the retention time for journald should be the minimum of all policies.
Longer retention times must be implemented by extracting logs with rsyslog and applying the policy
with logrotate.

If an application is migrated from logging to files or Syslog to logging to STDERR or journald
and the release is not part of a minor UCS release (e.g., 5.2-0)
then for backwards compatibility rsyslog extraction and logrotation SHOULD be configured.

If rsyslog is used to extract clear-text log files from journald, those files MUST be rotated using the
logrotate service.
In this case, logrotate will signal rsyslog to reopen the files.
No signal or restart of the original services is required, as that is logging to STDERR or journald.

If a log file is deprecated the manual MUST be extended with instructions how to retrieve the
applications logs from journald (e.g., using the `-u` or `-t` options) and how to configure rsyslog
extraction.

Product management MUST be consulted for each application to be migrated if pre-configured rsyslog
extraction is part of the release or not.

## Configuration

Operators of UCS installations must enforce their organizations data privacy protection policy.
To ensure the same policies are applied on all UCS systems the relevant settings MUST be stored in DCD.

### Journald

The default policy for eviction of journald database entries is size-based,
without restrictions on the age of messages.
For UCS and Nubus a time-based policy is required to fulfill data privacy policy requirements.
The value for `MaxRetentionSec`
in [journald.conf](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html)
MUST be configurable.
The default is `3month`.
This setting MUST be documented in the manual.

### Logrotate

When rsyslog is configured to extract logs from journald,
logrotate MUST be configured to rotate the resulting text files.
In UCS, a well-tried solution in the form of a UCR key schema already exists.
The only thing left is to migrate those keys to DCD for domain-wide consistency.

### Logging handler for Univention applications

In the future the need may arise to store severity and structured data for indexed searching.
It should then be possible to do that without changing the application,
just by configuring the Univention logging library.
The configuration would default in UCS to journald and in Nubus to STDERR.

This feature SHOULD NOT be implemented for now.
It is listed here just as a consequence of the _Decision Outcome_
from section _Preserving log level of messages from Docker_.

### Enable/Disable log level prefixing of log messages

When logging to STDERR from Python and the shell, our logging libraries can make use of the
[sd-daemon logging prefix](https://www.freedesktop.org/software/systemd/man/latest/sd-daemon.html)
to transport the log level to journald.

As the prefix is useless when logging from Docker containers in both UCS and Nubus (see section
_Preserving log level of messages from Docker_), the Univention logging libraries for shell and Python
SHOULD offer a configuration to disable the prefixing.

The configuration can be applied globally (disable prefixing in all of Nubus)
or per application (UCS support executing apps in the host and in Docker containers).

The UCR key schema is `logging/log-level-prefix/<application>=<option>`.

- `<application>` is the name of the program / script / service the prefixing should be defined for.
  - The special name `default` means that it will be defined for _all_ applications.
- `<option>` is a boolean and defaults to `True`, when not set.
  - Non-boolean values are ignored and the default is used.

When the program `foo` starts, the logging library will:

1. Apply the setting stored in `logging/log-level-prefix/foo` if it exists and is valid.
   Otherwise, continue to 2.
2. Apply the setting stored in `logging/log-level-prefix/default` if it exists and is valid.
   Otherwise, continue to 3.
3. Apply the default for `logging/log-level-prefix/default`: `True`.
