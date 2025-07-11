#!/usr/bin/env python3

# ### Install:
# python3 -m venv venv
# . venv/bin/activate
# pip install logfmter loguru orjson
#
# ### Run:
# ./level_conf.py


import os.path
import sys

import uni.adm.hand.groups
import uni.adm.hand.users
import uni.adm.hook.captain
import uni.listen.er
import uni.radius.net
from univention_logging import get_module_log_levels, logger, set_module_log_levels, setup_logging


def do_stuff():
    logger.debug("Debug in level_conf_aaa.py::do_stuff()")
    logger.info("Info in level_conf_aaa.py::do_stuff()")
    logger.warning("Warning in level_conf_aaa.py::do_stuff()")
    logger.error("Error in level_conf_aaa.py::do_stuff()")


if __name__ == "__main__":
    print(f"*** Starting log level test in {os.path.basename(__file__)!r}.", file=sys.stderr)
    print("*** Will configure logging, then call in order:", file=sys.stderr)
    print("  <this script>.do_stuff()", file=sys.stderr)
    print("  uni.adm.hand.groups.do_stuff()", file=sys.stderr)
    print("  uni.adm.hand.users.do_stuff()", file=sys.stderr)
    print("  uni.adm.hook.captain.do_stuff()", file=sys.stderr)
    print("  uni.listen.er.do_stuff()", file=sys.stderr)
    print("  uni.radius.net.do_stuff()", file=sys.stderr)
    print("*** The log levels have been configured in the following way:", file=sys.stderr)
    print("  root logger: 'TRACE'", file=sys.stderr)
    lvl_config = get_module_log_levels()
    for package in sorted(lvl_config):
        print(f"  {package!r}:  {lvl_config[package]!r}", file=sys.stderr)

    setup_logging()
    do_stuff()
    uni.adm.hand.groups.do_stuff()
    uni.adm.hand.users.do_stuff()
    uni.adm.hook.captain.do_stuff()
    uni.listen.er.do_stuff()
    uni.radius.net.do_stuff()

    print("*** Changing level (via UCR;) of 'uni.adm.hand.groups' to 'ERROR' and 'uni.radius' to default...")
    filter_cfg = get_module_log_levels().copy()
    filter_cfg["uni.adm.hand.groups"] = "ERROR"
    del filter_cfg["uni.radius"]
    set_module_log_levels(filter_cfg)
    setup_logging()
    print("*** The log levels are now configured in the following way:", file=sys.stderr)
    print("  root logger: 'TRACE'", file=sys.stderr)
    lvl_config = get_module_log_levels()
    for package in sorted(lvl_config):
        print(f"  {package!r}:  {lvl_config[package]!r}", file=sys.stderr)

    print("*** Executing functions...")
    do_stuff()
    uni.adm.hand.groups.do_stuff()
    uni.adm.hand.users.do_stuff()
    uni.adm.hook.captain.do_stuff()
    uni.listen.er.do_stuff()
    uni.radius.net.do_stuff()

    print("*** Changing name of application (as if this were another file / app / service) to one that has")
    print("    been configured (via UCR;) to log at level WARNING...")
    setup_logging("level_conf_warn.py")

    print("*** Executing functions...")
    do_stuff()
    uni.adm.hand.groups.do_stuff()
    uni.adm.hand.users.do_stuff()
    uni.adm.hook.captain.do_stuff()
    uni.listen.er.do_stuff()
    uni.radius.net.do_stuff()
