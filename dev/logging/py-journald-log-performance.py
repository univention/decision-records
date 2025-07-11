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
# Logged 10000 messages without delay between messages using JournalHandler in 3.174 sec (3.2/ms) [4a1ce75b21fc4aefbad59724f08ba2d2].
#
# When checking if the messages were received, you can use the 'UUID' field to filter:
#   journalctl UUID=<uuid> | wc -l
# Beware that the result will be 1 to high, as the output starts with a line
# -- Logs begin at ...
#

import logging
import random
import time
import uuid

from systemd.journal import JournalHandler


NUM_MSG_BULK = 10_000
WORDS = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eget nisl eu erat semper pellentesque "
    "ut at eros. Curabitur vel porttitor nunc. Mauris ultrices ipsum ut neque porta sollicitudin. Morbi "
    "semper fermentum nulla, ut commodo nulla mollis vel. Praesent quis purus ut metus suscipit dapibus."
    " Vivamus eget scelerisque nibh, sit amet elementum sapien. Cras nec lectus felis. In ut sagittis "
    "augue."
).split()

messages = [" ".join(random.choices(WORDS, k=20)) for _ in range(NUM_MSG_BULK)]
log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
uuid_s = uuid.uuid4().hex

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = JournalHandler()
logger.addHandler(handler)

t0 = time.time()

for count, msg in enumerate(messages, start=1):
    msg = f"{uuid_s}|{count}|{msg}"
    level = random.choice(log_levels)
    logger.log(level, msg)

handler.flush()

td = time.time()-t0
print(
    f"Logged {NUM_MSG_BULK} messages without delay between messages using JournalHandler in"
    f" {td:.3f} sec ({NUM_MSG_BULK / td / 1000:.1f}/ms) [{uuid_s}]."
)
