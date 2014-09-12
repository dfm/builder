# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["Library", "build_ext"]

import os
import re
import glob
import logging
from functools import wraps

from distutils.version import StrictVersion

try:
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    from distutils.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):

    def build_extension(self, ext):
        include_dirs = ext.include_dirs + self.compiler.include_dirs
        library_dirs = ext.library_dirs + self.compiler.library_dirs
        libs = list(ext.libraries)
        ext.libraries = []
        for lib in libs:
            if not hasattr(lib, "find_include"):
                ext.libraries += lib
                continue
            ext.include_dirs += lib.find_include(hint=include_dirs)[1]
            lds, libs = lib.find_libraries(hint=library_dirs)
            ext.library_dirs += lds
            ext.libraries += libs
            ext.extra_compile_args += lib.extra_compile_args()
        _build_ext.build_extension(self, ext)


class _cached(object):

    def __init__(self, k):
        self.k = k

    def __call__(self, f):
        @wraps(f)
        def wrapped(s, *args, **kwargs):
            v = getattr(s, self.k)
            if v is None:
                v = f(s, *args, **kwargs)
                setattr(s, self.k, v)
            return v
        return wrapped


class Library(object):

    name = None
    header_pattern = None
    library_pattern = None
    library_name = None
    version_header = None
    version_re_list = []
    include_dirs = [
        "/usr/local/include",
        "/usr/local/homebrew/include",
        "/opt/local/var/macports/software",
        "/opt/local/include",
        "/usr/include",
        "/usr/include/local",
    ]
    library_dirs = [
        "/usr/local/lib",
        "/usr/local/homebrew/lib",
        "/opt/local/lib",
        "/usr/lib",
    ]
    dependencies = []

    def __init__(self, min_version=None, required=True):
        assert self.name is not None, "Subclasses must have a name!"
        self.min_version = min_version
        self.required = required
        self._include = None
        self._libraries = None

    @_cached("_include")
    def find_include(self, hint=None, verbose=True):
        # Find the include directories for all the dependencies.
        include_dirs = [d for dep in self.dependencies
                        for d in dep.find_include()[1]]

        if self.header_pattern is None:
            return None, include_dirs

        # Loop over the possible search directories and look for the header.
        search_dirs = [] if hint is None else hint
        search_dirs += self.include_dirs
        for d in search_dirs:
            fns = glob.glob(os.path.join(d, self.header_pattern))
            if not len(fns):
                continue
            version = self.get_version(d)
            if (self.min_version is not None and
                    StrictVersion(version) < StrictVersion(self.min_version)):
                logging.warn("Found previous version of {0} in {1}"
                             .format(self.name, d))
                continue

            if verbose:
                if version is None:
                    print("Found {0} in {1}".format(self.name, d))
                else:
                    print("Found {0} in {1} [{2}]".format(self.name, d,
                                                          version))
            return version, include_dirs + [d]

        if self.required:
            raise RuntimeError("Couldn't find required headers for {0}"
                               .format(self.name))
        else:
            logging.warn("Couldn't find headers for {0}".format(self.name))

        return None, include_dirs

    @_cached("_libraries")
    def find_libraries(self, hint=None, verbose=True):
        # Find the include directories for all the dependencies.
        libraries, library_dirs = [], []
        for dep in self.dependencies:
            dirs, libs = dep.find_libraries()
            library_dirs += dirs
            libraries += libs

        if self.library_pattern is None:
            return library_dirs, libraries

        # Loop over the possible search directories and look for the header.
        search_dirs = [] if hint is None else hint
        search_dirs += self.library_dirs
        for d in search_dirs:
            fns = glob.glob(os.path.join(d, self.library_pattern))
            if not len(fns):
                continue

            if verbose:
                print("Found {0} library in {1}".format(self.name, d))

            return library_dirs + [d], libraries + [self.library_name]

        if self.required:
            raise RuntimeError("Couldn't find required library {0}"
                               .format(self.name))
        else:
            logging.warn("Couldn't find library {0}".format(self.name))
        return library_dirs, libraries

    def get_version(self, d):
        if self.version_header is None:
            return None
        fn = os.path.join(d, self.version_header)
        if not os.path.exists(fn):
            raise RuntimeError("The version header {0} doesn't exist"
                               .format(self.version_header))
        txt = open(fn, "r").read()
        v = [re.findall(pattern, txt)[0] for pattern in self.version_re_list]
        return ".".join(v)

    def extra_compile_args(self):
        return []
