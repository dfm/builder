# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["Glog"]

import os

from .builder import Library


class Glog(Library):

    name = "Glog"
    header_pattern = os.path.join("glog", "logging.h")
    library_pattern = "libglog.*"
    library_name = "glog"
