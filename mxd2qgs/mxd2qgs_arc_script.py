# mxd2qgs_arc_script
# https://github.com/fitnr/mxd2qgs
# This file is for use in a ArcMap toolbox

# Copyright (c) 2014 Neil Freeman, except for portions (c) 2011 Allan Maungu
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import mxd2qgs
import sys
import arcpy

print 'Converting mxd to qgs'

try:
    converter = mxd2qgs.mxd2qgs("CURRENT")

except Exception, e:
    print 'Error reading mxd file: ' + e.message
    sys.exit(1)

try:
    with open(arcpy.GetParameterAsText(0), 'wb') as handle:
        qgs = converter.convert()
        handle.write(qgs)

except Exception, e:
    print 'Error saving qgs file: '+ e.message
    sys.exit(1)

print 'Done: QGS file saved to ' + arcpy.GetParameterAsText(0)
