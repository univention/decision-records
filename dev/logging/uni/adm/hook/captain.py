import logging

logger = logging.getLogger(__name__)


def do_stuff():
    logger.debug("Debug in uni.adm.hook.captain.do_stuff()")
    logger.info("Info in uni.adm.hook.captain.do_stuff()")
    logger.warning("Warning in uni.adm.hook.captain.do_stuff()")
    logger.error("Error in uni.adm.hook.captain.do_stuff()")
