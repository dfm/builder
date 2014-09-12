# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["Eigen3"]

import os

from .builder import Library


class Eigen3(Library):

    name = "Eigen3"
    header_pattern = os.path.join("Eigen", "Dense")
    version_header = os.path.join("Eigen", "src", "Core", "util", "Macros.h")
    version_re_list = [
        "#define EIGEN_WORLD_VERSION (.+)",
        "#define EIGEN_MAJOR_VERSION (.+)",
        "#define EIGEN_MINOR_VERSION (.+)",
    ]
    include_dirs = [
        "/usr/local/include/eigen3",
        "/usr/local/homebrew/include/eigen3",
        "/opt/local/var/macports/software/eigen3",
        "/opt/local/include/eigen3",
        "/usr/include/eigen3",
        "/usr/include/local",
    ]
