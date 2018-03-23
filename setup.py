#===============================================================================
# StockView
# Copyright (C) 2018 Damir Akhmetzyanov
# 
# This file is part of StockView
# 
# StockView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# StockView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from distutils.core import setup
import py2exe
import os, glob, sys
from babel.messages import frontend as babel

def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

python_path = os.path.dirname(sys.executable)

setup(
    cmdclass = {'compile_catalog': babel.compile_catalog,
                'extract_messages': babel.extract_messages,
                'init_catalog': babel.init_catalog,
                'update_catalog': babel.update_catalog},
    windows = [
        {
            "script": "StockView.py",
            "icon_resources": [(1, "icons/main.ico")]
        }
    ], 
    zipfile='lib/library.zip', 
    options={"py2exe":{"includes":["sip"]}},
    data_files=find_data_files('', '', [
        'LICENSE.txt',
        'COPYING',
        'icons/*',
        'Finam_data/*'
    ]) + [('imageformats', [ python_path + r'\Lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll' ])]
)