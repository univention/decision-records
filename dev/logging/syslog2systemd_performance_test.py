#!/usr/bin/env python3

#
# Send 10.000 random log messages to syslog2systemd server.
#

#
# docker run --rm -it -v $(pwd):/app python python3 /app/syslog2systemd_performance_test.py
#
# Bulk:  Logged 10000 messages with 0.1 ms delay between messages to Syslog in 1.876 sec (5.3/ms) [be12d19cc1bc404695b22ad3b8203afe].
# Burst: Logged 100 messages without delay between each message to Syslog in 7.663 ms (13.1/ms) [420f34f1ef534f289add5d6c4654059a].
# Burst: Logged 100 messages without delay between each message to Syslog in 7.644 ms (13.1/ms) [a9895b737325474b85feed448b3b2f48].
# Burst: Logged 100 messages without delay between each message to Syslog in 7.622 ms (13.1/ms) [a264e8a261fe4354a1015a0e502a964b].
# To verify the result, run on host: journalctl -t MyApp -S -5m | grep <UUID> | wc -l
#
# journalctl -t MyApp -S -5m | grep be12d19cc1bc404695b22ad3b8203afe | wc -l
# 10000
# journalctl -t MyApp -S -5m | grep 420f34f1ef534f289add5d6c4654059a | wc -l
# 100
#

#
# After the test ran, on the server:
# Parsed 10200 messages.
# Parsed 10300 messages.
# ^C
# Shutting down sender thread.
# Shutting down UDP server.
# Received 10300 messages.
# Parsed 10300 messages.
# Cache stats: CacheInfo(hits=10295, misses=5, maxsize=1024, currsize=5)
# Parsing (min/avg/max): 0.000/0.002/0.029 ms.
# Sending (min/avg/max): 0.000/0.040/0.350 ms.
#

import logging.handlers
import random
import time
import uuid

ADDRESS = "172.17.42.1"
PORT = 5140
APP_ID = "MyApp"

MSG_DELAY = 0.0001  # Seconds to wait between log messages.
                    # At 8k msg/s, the limiting factor is probably the network stack.
NUM_MSG_BULK = 10_000
NUM_MSG_BURST = 100
WORDS = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eget nisl eu erat semper pellentesque "
    "ut at eros. Curabitur vel porttitor nunc. Mauris ultrices ipsum ut neque porta sollicitudin. Morbi "
    "semper fermentum nulla, ut commodo nulla mollis vel. Praesent quis purus ut metus suscipit dapibus."
    " Vivamus eget scelerisque nibh, sit amet elementum sapien. Cras nec lectus felis. In ut sagittis "
    "augue."
).split()


handler = logging.handlers.SysLogHandler(address=(ADDRESS, PORT))
handler.setLevel(logging.DEBUG)
handler.ident = f"{APP_ID}|"
# handler.facility = logging.handlers.SysLogHandler.LOG_MAIL

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
# logger.addHandler(logging.StreamHandler())

messages = [" ".join(random.choices(WORDS, k=20)) for _ in range(max(NUM_MSG_BURST, NUM_MSG_BULK))]
log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

uuid_s = uuid.uuid4().hex
t0 = time.time()

for count, msg in enumerate(messages, start=1):
    time.sleep(MSG_DELAY)
    msg = f"{uuid_s}|{count}|{msg}"
    level = random.choice(log_levels)
    logger.log(level, msg)

td = time.time()-t0
print(
    f"Bulk:  Logged {NUM_MSG_BULK} messages with {MSG_DELAY * 1000:.1f} ms delay between messages to "
    f"Syslog in {td:.3f} sec ({NUM_MSG_BULK / td / 1000:.1f}/ms) [{uuid_s}]."
)

for _ in range(3):
    time.sleep(0.5)
    uuid_s = uuid.uuid4().hex
    t0 = time.time()

    for count, msg in enumerate(messages[:NUM_MSG_BURST], start=1):
        msg = f"{uuid_s}|{count}|{msg}"
        level = random.choice(log_levels)
        logger.log(level, msg)

    td = time.time()-t0
    print(
        f"Burst: Logged {NUM_MSG_BURST} messages without delay between messages to Syslog in "
        f"{td*1000:.3f} ms ({NUM_MSG_BURST / td / 1000:.1f}/ms) [{uuid_s}]."
    )

print(f"To verify the result, run on host: journalctl -t {APP_ID} -S -5m | grep <UUID> | wc -l")
