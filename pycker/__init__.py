import logging
import sys


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)

_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.DEBUG)
_LOG.addHandler(_HANDLER)
