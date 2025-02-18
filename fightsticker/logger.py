from logging import Formatter, getLogger, StreamHandler
from sys import stdout

logger = getLogger("Fightsticker")
logger.setLevel("INFO")
_hdlr = StreamHandler(stdout)
_hdlr.setFormatter(Formatter("%(levelname)s: %(message)s"))
logger.addHandler(_hdlr)
