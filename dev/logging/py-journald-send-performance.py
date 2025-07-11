#!/usr/bin/env python3

#
# Send 10.000 random log messages directly to journald.
#
# ### Installation dependencies:
# apt install python3-systemd
#
# ### Start script:
# python3 py-journald-performance.py
# ### Output:
# Logged 10000 messages without delay between messages using journald.send() in 0.715 sec (14.0/ms) [7282bbbc92b84d77bd0e5e14e6928802].
#
# When checking if the messages were received, you can use the 'UUID' field to filter:
#   journalctl UUID=<uuid> | wc -l
# Beware that the result will be 1 to high, as the output starts with a line
# -- Logs begin at ...
#

import random
import time
import uuid

from systemd import journal


NUM_MSG_BULK = 10_000
WORDS = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eget nisl eu erat semper pellentesque "
    "ut at eros. Curabitur vel porttitor nunc. Mauris ultrices ipsum ut neque porta sollicitudin. Morbi "
    "semper fermentum nulla, ut commodo nulla mollis vel. Praesent quis purus ut metus suscipit dapibus."
    " Vivamus eget scelerisque nibh, sit amet elementum sapien. Cras nec lectus felis. In ut sagittis "
    "augue."
).split()

messages = [" ".join(random.choices(WORDS, k=20)) for _ in range(NUM_MSG_BULK)]
log_levels = [2, 3, 4, 6, 7]

uuid_s = uuid.uuid4().hex
t0 = time.time()

for count, msg in enumerate(messages, start=1):
    msg = f"{uuid_s}|{count}|{msg}"
    level = random.choice(log_levels)
    journal.send(
        msg,
        SYSLOG_FACILITY=1,
        PRIORITY=level,
        SYSLOG_IDENTIFIER="py-journald-performance",
        UUID=uuid_s,
    )

td = time.time()-t0
print(
    f"Logged {NUM_MSG_BULK} messages without delay between messages using journald.send() in"
    f" {td:.3f} sec ({NUM_MSG_BULK / td / 1000:.1f}/ms) [{uuid_s}]."
)
