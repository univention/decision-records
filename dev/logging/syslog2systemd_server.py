#!/usr/bin/env python3

#
# Syslog server that forwards messages to journald.
#
# Detects the Syslog ident, facility and priority if the "ident" attribute is set,
# and a pipe (|) character is appended to the name.
# E.g.:
# handler = logging.handlers.SysLogHandler(address=("172.17.42.1", 5140))
# handler.ident = "My App|"
#
# The Syslog facility is by default set to 1 (LOG_USER).
# It can be set on the handler object:
# handler.facility = logging.handlers.SysLogHandler.LOG_MAIL
#
# RFC: https://www.rfc-editor.org/rfc/rfc5424.html#section-6.2.1
#
# UDP receiver runs in the main thread and just writes into a queue.
# Sender runs in a separate thread, consumes the queue, parses and sends result to journald.
#
# Configure firewall:
# ucr set security/packetfilter/package/Syslog2Systemd/udp/5140/all=ACCEPT \
#   security/packetfilter/package/Syslog2Systemd/udp/5140/all/en=Syslog2Systemd
# systemctl restart univention-firewall.service
#
# ### Installation dependencies:
# apt install python3-netifaces python3-systemd
# or for a venv:
# apt install libsystemd-dev && pip install netifaces systemd
#
# ### Start server:
# python3 syslog2systemd_server.py
#

import functools
import queue
import re
import socketserver
import time
import threading
from typing import NamedTuple, Tuple

import netifaces
from systemd import journal


IFACE_NAME_DOCKER = "docker0"
PORT = 5140
RE_MSG = re.compile(r"^<(?P<prio>.+?)>(?P<ident>.+?)$", re.MULTILINE)
SHUTDOWN_MSG = b"$$QUIT$$"


class Metadata(NamedTuple):
    ident: str
    facility: int
    priority: int


class SyslogHandler(socketserver.DatagramRequestHandler):

    queue = queue.Queue(maxsize=10_000)
    statistics= {
        "messages_parsed": 0,
        "messages_received": 0,
        "parsing_max": 0.0,
        "parsing_min": 100.0,
        "parsing_total": 0.0,
        "sending_max": 0.0,
        "sending_min": 100.0,
        "sending_total": 0.0,
    }

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def tags_to_metadata(tags: str) -> Metadata:
        msg_p = RE_MSG.match(tags)
        if msg_p:
            prio = msg_p.groupdict()["prio"]
            ident = msg_p.groupdict()["ident"]
        else:
            print(f"Error parsing metadata string: {tags!r}")
            prio = "14"
            ident = "1"
        try:
            prio = int(prio)
        except ValueError:
            prio = 14  # default: fac=1, prio=6
        facility = prio // 8
        priority = prio % 8
        return Metadata(ident=ident, facility=facility, priority=priority)

    @classmethod
    def parse_msg(cls, line: str) -> Tuple[Metadata, str]:
        # Pattern matching is expensive, so we cache it in tags_to_metadata().
        pipe_pos = line.find("|")
        if pipe_pos > 0:
            tags = line[:pipe_pos]
            msg = line[pipe_pos+1:]
            return cls.tags_to_metadata(tags), msg
        else:
            print(f"Error parsing message: {line!r}")
            return Metadata(ident="", facility=1, priority=6), line

    @classmethod
    def update_stats(cls, td: float, stats_type: str) -> None:
        cls.statistics[f"{stats_type}_total"] += td
        if td < cls.statistics[f"{stats_type}_min"]:
            cls.statistics[f"{stats_type}_min"] = td
        elif td > cls.statistics[f"{stats_type}_max"]:
            cls.statistics[f"{stats_type}_max"] = td

    @classmethod
    def parse_and_send_worker(cls) -> None:
        while True:
            addr, data_b = cls.queue.get()
            # print(f"Got raw data from queue: {data_b!r}")
            if data_b == SHUTDOWN_MSG:
                cls.queue.task_done()
                break
            t0 = time.time()
            data_s = data_b.rstrip(b"\x00").strip().decode()
            metadata, msg = cls.parse_msg(data_s)
            cls.statistics["messages_parsed"] += 1
            cls.update_stats(time.time() - t0, "parsing")
            # print(
            #     f"Parsed message from {addr!r} to: priority: {metadata.priority!r} "
            #     f"facility: {metadata.facility!r} ident: {metadata.ident!r} msg: {msg!r}"
            # )
            t0 = time.time()
            journal.send(
                msg,
                SYSLOG_FACILITY=metadata.facility,
                PRIORITY=metadata.priority,
                SYSLOG_IDENTIFIER=metadata.ident
            )
            cls.update_stats(time.time() - t0, "sending")
            if cls.statistics["messages_parsed"] % 100 == 0:
                print(f"Parsed {cls.statistics['messages_parsed']} messages.")
            cls.queue.task_done()

    def handle(self) -> None:
        data_b = self.rfile.read(4096)
        # print(f"Received raw data via UDP: {data_b!r}")
        self.statistics["messages_received"] += 1
        self.queue.put((self.client_address[0], data_b))


if __name__ == "__main__":
    host = netifaces.ifaddresses(IFACE_NAME_DOCKER)[2][0]["addr"]
    server = socketserver.UDPServer((host, PORT), SyslogHandler)

    print("Starting sender thread.")
    parse_and_send_worker = threading.Thread(target=SyslogHandler.parse_and_send_worker).start()

    print(f"Starting UDP server on {host}:{PORT}.")
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down sender thread.")
        SyslogHandler.queue.put(("bye bye", SHUTDOWN_MSG))
        SyslogHandler.queue.join()
        print("Shutting down UDP server.")
        server.shutdown()

    print(f"Received {SyslogHandler.statistics['messages_received']} messages.")
    print(f"Parsed {SyslogHandler.statistics['messages_parsed']} messages.")
    print(f"Cache stats: {SyslogHandler.tags_to_metadata.cache_info()!r}")
    if SyslogHandler.statistics['messages_parsed'] > 0:
        p_avg = SyslogHandler.statistics["parsing_total"] *1000 / SyslogHandler.statistics["messages_parsed"]
        s_avg = SyslogHandler.statistics["sending_total"] *1000 / SyslogHandler.statistics["messages_parsed"]
        print(
            f"Parsing (min/avg/max): {SyslogHandler.statistics['parsing_min']:.3f}/"
            f"{p_avg:.3f}/"
            f"{SyslogHandler.statistics['parsing_max'] * 1000:.3f} ms."
        )
        print(
            f"Sending (min/avg/max): {SyslogHandler.statistics['sending_min']:.3f}/"
            f"{s_avg:.3f}/"
            f"{SyslogHandler.statistics['sending_max'] * 1000:.3f} ms."
        )
