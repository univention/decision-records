#!/usr/bin/env python3

#
# Send 10.000 random log messages to STDERR.
# System will forward them to journald.
#
# Installation:
# cp service-sd-daemon-prefix.service /etc/systemd/system/py-stderr-performance.service
# vim /etc/systemd/system/py-stderr-performance.service
# -> adapt path to py-stderr-performance.py
# systemctl restart py-stderr-performance
#
# systemctl status py-stderr-performance | tail -1
# Feb 28 10:45:46 primary py-stderr-performance.py[21759]: Logged 10000 messages to STDERR without delay between messages in 0.407 sec (24.6/ms) [847be28e54094a0eaa9fbc3a29ee944a].
#
# journalctl -n 15000 | grep 847be28e54094a0eaa9fbc3a29ee944a | grep -v "Logged 10000 messages to STDERR" | wc -l
# 10000
#


import random
import sys
import time
import uuid


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
    print(msg, file=sys.stderr)

td = time.time()-t0
print(
    f"Logged {NUM_MSG_BULK} messages to STDERR without delay between messages in"
    f" {td:.3f} sec ({NUM_MSG_BULK / td / 1000:.1f}/ms) [{uuid_s}]."
)
