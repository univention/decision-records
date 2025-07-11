import logging

logger = logging.getLogger(__name__)


def do_stuff():
    logger.debug("Debug in uni.adm.hand.groups.do_stuff()")
    logger.info("Info in uni.adm.hand.groups.do_stuff()")
    logger.warning("Warning in uni.adm.hand.groups.do_stuff()")
    logger.error("Error in uni.adm.hand.groups.do_stuff()")
