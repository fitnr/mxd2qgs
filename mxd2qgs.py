#-----------------------------------------------------------
#
# Mxd2Qgs ver 1.0
# Copyright (C) 2011 Allan Maungu
# EMAIL: lumtegis (at) gmail.com
# WEB  : http://geoscripting.blogspot.com
# Usage : Exporting current ArcMap document layers to Quantum GIS file
# The resulting file can be opened in Quantum GIS
# Tested on ArcMap 10, Python 2.6.5 and Quantum GIS 1.6.0
#-----------------------------------------------------------
#
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
#
#---------------------------------------------------------------------

# Import system modules
from xml.dom.minidom import Document
import xml.dom.ext
import string
import os
import arcpy

# Read input parameters from GP dialog
output = arcpy.GetParameterAsText(0)

# Create an output qgs file
f = open(output, "w")

# Create the minidom
doc = Document()

# Create the <qgis> base element
qgis = doc.createElement("qgis")
qgis.setAttribute("projectname", " ")
qgis.setAttribute("version", "1.6.0-Capiapo")
doc.appendChild(qgis)

# Create the <title> element
title = doc.createElement("title")
qgis.appendChild(title)

# Assign current document
mxd = arcpy.mapping.MapDocument("CURRENT")

print 'Converting mxd........'

# Dataframe elements

df = arcpy.mapping.ListDataFrames(mxd)[0]
unit = doc.createTextNode(df.mapUnits)
xmin1 = doc.createTextNode(str(df.extent.XMin))
ymin1 = doc.createTextNode(str(df.extent.YMin))
xmax1 = doc.createTextNode(str(df.extent.XMax))
ymax1 = doc.createTextNode(str(df.extent.YMax))
# srsid = doc.createTextNode
srid1 = doc.createTextNode(str(df.spatialReference.factoryCode))
srid2 = doc.createTextNode(str(df.spatialReference.factoryCode))
epsg1 = doc.createTextNode(str(df.spatialReference.factoryCode))
epsg2 = doc.createTextNode(str(df.spatialReference.factoryCode))
description1 = doc.createTextNode(str(df.spatialReference.name))
description2 = doc.createTextNode(str(df.spatialReference.name))
ellipsoidacronym1 = doc.createTextNode(str(df.spatialReference.name))
ellipsoidacronym2 = doc.createTextNode(str(df.spatialReference.name))
geographicflag1 = doc.createTextNode("true")
geographicflag2 = doc.createTextNode("true")

authid2 = doc.createTextNode("EPSG:" + str(df.spatialReference.factoryCode))
authid3 = doc.createTextNode("EPSG:" + str(df.spatialReference.factoryCode))

# Layerlist elements
lyrlist = arcpy.mapping.ListLayers(df)
count1 = str(len(lyrlist))


def map_canvas():
    # Create the <mapcanvas> element
    mapcanvas = doc.createElement("mapcanvas")
    qgis.appendChild(mapcanvas)

    # Create the <units> element
    units = doc.createElement("units")
    units.appendChild(unit)
    mapcanvas.appendChild(units)

    # Create the <extent> element
    extent = doc.createElement("extent")
    mapcanvas.appendChild(extent)

    # Create the <xmin> element
    xmin = doc.createElement("xmin")
    xmin.appendChild(xmin1)
    extent.appendChild(xmin)

    # Create the <ymin> element
    ymin = doc.createElement("ymin")
    ymin.appendChild(ymin1)
    extent.appendChild(ymin)

    # Create the <xmax> element
    xmax = doc.createElement("xmax")
    xmax.appendChild(xmax1)
    extent.appendChild(xmax)

    # Create the <ymax> element
    ymax = doc.createElement("ymax")
    ymax.appendChild(ymax1)
    extent.appendChild(ymax)

    # Create the <projections> element
    projections = doc.createElement("projections")
    mapcanvas.appendChild(projections)

    # Create the <destinationsrs> element
    destinationsrs = doc.createElement("destinationsrs")
    mapcanvas.appendChild(destinationsrs)

    # Create the <spatialrefsys> element
    spatialrefsys = doc.createElement("spatialrefsys")
    destinationsrs.appendChild(spatialrefsys)

    # Create the <proj4> element
    proj4 = doc.createElement("proj4")
    spatialrefsys.appendChild(proj4)

    # Create the <srsid> element
    srsid = doc.createElement("srsid")
    spatialrefsys.appendChild(srsid)

    # Create the <srid> element
    srid = doc.createElement("srid")
    srid.appendChild(srid1)
    spatialrefsys.appendChild(srid)

    # Create the <authid> element
    authid = doc.createElement("authid")
    authid.appendChild(authid2)
    spatialrefsys.appendChild(authid)

    # Create the <description> element
    description = doc.createElement("description")
    description.appendChild(description1)
    spatialrefsys.appendChild(description)

    # Create the <projectionacronym> element
    projectionacronym = doc.createElement("projectionacronym")
    spatialrefsys.appendChild(projectionacronym)

    # Create the <ellipsoidacronym element
    ellipsoidacronym = doc.createElement("ellipsoidacronym")
    ellipsoidacronym.appendChild(ellipsoidacronym1)
    spatialrefsys.appendChild(ellipsoidacronym)

    # Create the <geographicflag> element
    geographicflag = doc.createElement("geographicflag")
    geographicflag.appendChild(geographicflag1)
    spatialrefsys.appendChild(geographicflag)


def legend_func():

    # Create the <legend> element
    legend = doc.createElement("legend")
    qgis.appendChild(legend)

    for lyr in lyrlist:
        if(lyr.isGroupLayer == False):

            # Create the <legendlayer> element
            legendlayer = doc.createElement("legendlayer")
            legendlayer.setAttribute("open", "true")
            legendlayer.setAttribute("checked", "Qt::Checked")
            legendlayer.setAttribute("name", str(lyr.name))

            legend.appendChild(legendlayer)

            # Create the <filegroup> element
            filegroup = doc.createElement("filegroup")
            filegroup.setAttribute("open", "true")
            filegroup.setAttribute("hidden", "false")
            legendlayer.appendChild(filegroup)

            # Create the <legendlayerfile> element
            legendlayerfile = doc.createElement("legendlayerfile")
            legendlayerfile.setAttribute("isInOverview", "0")
            legendlayerfile.setAttribute("layerid", str(lyr.name) + str(20110427170816078))
            legendlayerfile.setAttribute("visible", "1")
            filegroup.appendChild(legendlayerfile)


def project_layers():

    # Create the <projectlayers> element
    projectlayers = doc.createElement("projectlayers")
    projectlayers.setAttribute("layercount", count1)
    qgis.appendChild(projectlayers)

    for lyr in lyrlist:

        if(lyr.isGroupLayer == False and lyr.isRasterLayer == False):
            geometry1 = arcpy.Describe(lyr)
            geometry2 = str(geometry1.shapeType)
            ds = doc.createTextNode(str(lyr.dataSource))

            name1 = doc.createTextNode(str(lyr.name) + str(20110427170816078))
            name2 = doc.createTextNode(str(lyr.name))

           # Create the <maplayer> element
            maplayer = doc.createElement("maplayer")
            maplayer.setAttribute("minimumScale", "0")
            maplayer.setAttribute("maximumScale", "1e+08")
            maplayer.setAttribute("minLabelScale", "0")
            maplayer.setAttribute("maxLabelScale", "1e+08")
            maplayer.setAttribute("geometry", geometry2)
            if(lyr.isRasterLayer == True):
                maplayer.setAttribute("type", "raster")
            else:
                maplayer.setAttribute("type", "vector")
            maplayer.setAttribute("hasScaleBasedVisibilityFlag", "0")
            maplayer.setAttribute("scaleBasedLabelVisibilityFlag", "0")
            projectlayers.appendChild(maplayer)

            # Create the <id> element
            id = doc.createElement("id")
            id.appendChild(name1)
            maplayer.appendChild(id)

            # Create the <datasource> element
            datasource = doc.createElement("datasource")
            datasource.appendChild(ds)
            maplayer.appendChild(datasource)

            # Create the <layername> element
            layername = doc.createElement("layername")
            layername.appendChild(name2)
            maplayer.appendChild(layername)

            # Create the <srs> element
            srs = doc.createElement("srs")
            maplayer.appendChild(srs)

            # Create the <spatialrefsys> element
            spatialrefsys = doc.createElement("spatialrefsys")
            srs.appendChild(spatialrefsys)

            # Create the <proj4> element
            proj4 = doc.createElement("proj4")
            spatialrefsys.appendChild(proj4)

            # Create the <srsid> element
            srsid = doc.createElement("srsid")
            spatialrefsys.appendChild(srsid)

            # Create the <srid> element
            srid = doc.createElement("srid")
            srid.appendChild(srid2)
            spatialrefsys.appendChild(srid)

            # Create the <authid> element
            authid = doc.createElement("authid")
            authid.appendChild(authid3)
            spatialrefsys.appendChild(authid)

            # Create the <description> element
            description = doc.createElement("description")
            description.appendChild(description2)
            spatialrefsys.appendChild(description)

            # Create the <projectionacronym> element
            projectionacronym = doc.createElement("projectionacronym")
            spatialrefsys.appendChild(projectionacronym)

            # Create the <ellipsoidacronym element
            ellipsoidacronym = doc.createElement("ellipsoidacronym")
            ellipsoidacronym.appendChild(ellipsoidacronym2)
            spatialrefsys.appendChild(ellipsoidacronym)

            # Create the <geographicflag> element
            geographicflag = doc.createElement("geographicflag")
            geographicflag.appendChild(geographicflag2)
            spatialrefsys.appendChild(geographicflag)

            # Create the <transparencyLevelInt> element
            transparencyLevelInt = doc.createElement("transparencyLevelInt")
            transparency2 = doc.createTextNode("255")
            transparencyLevelInt.appendChild(transparency2)
            maplayer.appendChild(transparencyLevelInt)

            # Create the <customproperties> element
            customproperties = doc.createElement("customproperties")
            maplayer.appendChild(customproperties)

            # Create the <provider> element
            provider = doc.createElement("provider")
            provider.setAttribute("encoding", "System")
            ogr = doc.createTextNode("ogr")
            provider.appendChild(ogr)
            maplayer.appendChild(provider)

            # Create the <singlesymbol> element
            singlesymbol = doc.createElement("singlesymbol")
            maplayer.appendChild(singlesymbol)

            # Create the <symbol> element
            symbol = doc.createElement("symbol")
            singlesymbol.appendChild(symbol)

            # Create the <lowervalue> element
            lowervalue = doc.createElement("lowervalue")
            symbol.appendChild(lowervalue)

            # Create the <uppervalue> element
            uppervalue = doc.createElement("uppervalue")
            symbol.appendChild(uppervalue)

            # Create the <label> element
            label = doc.createElement("label")
            symbol.appendChild(label)

            # Create the <rotationclassificationfieldname> element
            rotationclassificationfieldname = doc.createElement("rotationclassificationfieldname")
            symbol.appendChild(rotationclassificationfieldname)

            # Create the <scaleclassificationfieldname> element
            scaleclassificationfieldname = doc.createElement("scaleclassificationfieldname")
            symbol.appendChild(scaleclassificationfieldname)

            # Create the <symbolfieldname> element
            symbolfieldname = doc.createElement("symbolfieldname")
            symbol.appendChild(symbolfieldname)

             # Create the <outlinecolor> element
            outlinecolor = doc.createElement("outlinecolor")
            outlinecolor.setAttribute("red", "88")
            outlinecolor.setAttribute("blue", "99")
            outlinecolor.setAttribute("green", "37")
            symbol.appendChild(outlinecolor)

             # Create the <outlinestyle> element
            outlinestyle = doc.createElement("outlinestyle")
            outline = doc.createTextNode("SolidLine")
            outlinestyle.appendChild(outline)
            symbol.appendChild(outlinestyle)

             # Create the <outlinewidth> element
            outlinewidth = doc.createElement("outlinewidth")
            width = doc.createTextNode("0.26")
            outlinewidth.appendChild(width)
            symbol.appendChild(outlinewidth)

             # Create the <fillcolor> element
            fillcolor = doc.createElement("fillcolor")
            fillcolor.setAttribute("red", "90")
            fillcolor.setAttribute("blue", "210")
            fillcolor.setAttribute("green", "229")
            symbol.appendChild(fillcolor)

             # Create the <fillpattern> element
            fillpattern = doc.createElement("fillpattern")
            fill = doc.createTextNode("SolidPattern")
            fillpattern.appendChild(fill)
            symbol.appendChild(fillpattern)

             # Create the <texturepath> element
            texturepath = doc.createElement("texturepath")
            texturepath.setAttribute("null", "1")
            symbol.appendChild(texturepath)


map_canvas()
legend_func()
project_layers()


#  Write to qgis file

try:
    xml.dom.ext.PrettyPrint(doc, f)
finally:
    f.close()

print 'Done'
