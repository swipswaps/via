# -*- coding: utf-8 -*-

# This module is not used directly but is referenced by config.yaml.
# This must be imported before `pywb` is imported in `via.app`.
import via.rewriter  # noqa: F401
from via._version import get_version

__all__ = ("__version__",)
__version__ = get_version()
