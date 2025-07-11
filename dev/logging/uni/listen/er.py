import logging

logger = logging.getLogger(__name__)


def do_stuff():
    logger.debug("Debug in uni.listen.er.do_stuff()")
    logger.info("Info in uni.listen.er.do_stuff()")
    logger.warning("Warning in uni.listen.er.do_stuff()")
    logger.error("Error in uni.listen.er.do_stuff()")
