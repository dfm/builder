# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["Ceres"]

import os

from .builder import Library
from .eigen3 import Eigen3
from .glog import Glog


class Ceres(Library):

    name = "Ceres"
    header_pattern = os.path.join("ceres", "ceres.h")
    library_pattern = "libceres.*"
    library_name = "ceres"
    version_header = os.path.join("ceres", "version.h")
    version_re_list = [
        "#define CERES_VERSION_MAJOR (.+)",
        "#define CERES_VERSION_MINOR (.+)",
        "#define CERES_VERSION_REVISION (.+)",
    ]
    dependencies = [
        Eigen3(),
        Glog(required=False),
    ]

    def find_libraries(self, *args, **kwargs):
        library_dirs, libraries = super(Ceres, self).find_libraries(*args,
                                                                    **kwargs)

        # Deal with versions of Ceres compiled with miniglog.
        _, include_dirs = self.find_include()
        fn = os.path.join(include_dirs[-1], "ceres", "internal", "miniglog")
        if os.path.exists(fn):
            if kwargs.get("verbose", True):
                print("Using miniglog")
            libraries.remove("glog")

        return library_dirs, libraries
