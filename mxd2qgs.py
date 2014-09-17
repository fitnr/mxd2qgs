#
# mxd2qgs
# Copyright (C) 2011 Allan Maungu, 2014 Neil Freeman
# https://github.com/fitnr/mxd2qgs
# Converts ArcMap documents to .qgs format
# The resulting file can be opened in Quantum GIS
# Tested on ArcMap 10, Python 2.6.5 and Quantum GIS 1.6.0
#
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

from xml.dom.minidom import Document
import arcpy


class mxd2qgs(object):

    """Conversion wrapper"""

    def __init__(self, mxdfile=None):
        # Assign the input file
        mxdfile = mxdfile or "CURRENT"
        try:
            self.mxd = arcpy.mapping.MapDocument(mxdfile)
        except AssertionError, e:
            print('error importing', mxdfile)
            raise e

        # Create the minidom
        self.doc = Document()

        # Dataframe elements
        self.df = arcpy.mapping.ListDataFrames(self.mxd).pop()

        # Layerlist elements
        self.lyrlist = arcpy.mapping.ListLayers(self.df)

    def convert(self, output):
        '''Run conversion and write to a file'''
        try:
            # Create the <qgis> base element
            qgis = self.doc.createElement("qgis")
            qgis.setAttribute("projectname", " ")
            qgis.setAttribute("version", "1.6.0-Capiapo")
            self.doc.appendChild(qgis)

            # Create the <title> element
            title = self.doc.createElement("title")
            qgis.appendChild(title)

            canvas = self.canvas()
            qgis.appendChild(canvas)

            legend = self.legend()
            qgis.appendChild(legend)

            layers = self.layers()
            qgis.appendChild(layers)

            # Write to qgis file
            with open(output, "w") as f:
                f.write(self.doc.toxml())

        except Exception, e:
            raise e

    def canvas(self):
        '''Create the <mapcanvas> element'''
        mapcanvas = self.doc.createElement("mapcanvas")

        # Create the <units> element
        unit = self.doc.createTextNode(self.df.mapUnits)

        units = self.doc.createElement("units")
        units.appendChild(unit)
        mapcanvas.appendChild(units)

        # Create the <extent> element
        extent = self.doc.createElement("extent")
        mapcanvas.appendChild(extent)

        # Create the <xmin> element
        xmin = self.doc.createElement("xmin")
        xmin.appendChild(self.doc.createTextNode(str(self.df.extent.XMin)))
        extent.appendChild(xmin)

        # Create the <ymin> element
        ymin = self.doc.createElement("ymin")
        ymin.appendChild(self.doc.createTextNode(str(self.df.extent.YMin)))
        extent.appendChild(ymin)

        # Create the <xmax> element
        xmax = self.doc.createElement("xmax")
        xmax.appendChild(self.doc.createTextNode(str(self.df.extent.XMax)))
        extent.appendChild(xmax)

        # Create the <ymax> element
        ymax = self.doc.createElement("ymax")
        ymax.appendChild(self.doc.createTextNode(str(self.df.extent.YMax)))
        extent.appendChild(ymax)

        # Create the <projections> element
        projections = self.doc.createElement("projections")
        mapcanvas.appendChild(projections)

        # Create the <destinationsrs> element
        destinationsrs = self.doc.createElement("destinationsrs")
        mapcanvas.appendChild(destinationsrs)

        # Create the <spatialrefsys> element
        spatialrefsys = self.generate_spatial()
        destinationsrs.appendChild(spatialrefsys)

        return mapcanvas

    def generate_spatial(self):
        '''Generate spatial references for the document or a layer'''
        spatialrefsys = self.doc.createElement("spatialrefsys")

        # Create the <proj4> element
        proj4 = self.doc.createElement("proj4")
        spatialrefsys.appendChild(proj4)

        # Create the <srsid> element
        srsid = self.doc.createElement("srsid")
        spatialrefsys.appendChild(srsid)

        # Create the <srid> element
        mxd_srid = self.doc.createTextNode(str(self.df.spatialReference.factoryCode))
        srid = self.doc.createElement("srid")
        srid.appendChild(mxd_srid)
        spatialrefsys.appendChild(srid)

        # Create the <authid> element
        mxd_authid = self.doc.createTextNode("EPSG:" + str(self.df.spatialReference.factoryCode))
        authid = self.doc.createElement("authid")
        authid.appendChild(mxd_authid)
        spatialrefsys.appendChild(authid)

        # Create the <description> element
        max_d = self.doc.createTextNode(str(self.df.spatialReference.name))
        description = self.doc.createElement("description")
        description.appendChild(max_d)
        spatialrefsys.appendChild(description)

        # Create the <projectionacronym> element
        projectionacronym = self.doc.createElement("projectionacronym")
        spatialrefsys.appendChild(projectionacronym)

        # Create the <ellipsoidacronym element
        ea = self.doc.createTextNode(str(self.df.spatialReference.name))
        ellipsoidacronym = self.doc.createElement("ellipsoidacronym")
        ellipsoidacronym.appendChild(ea)
        spatialrefsys.appendChild(ellipsoidacronym)

        # Create the <geographicflag> element
        geographicflag = self.doc.createElement("geographicflag")
        geographicflag.appendChild(self.doc.createTextNode("true"))
        spatialrefsys.appendChild(geographicflag)

    def legend(self):
        '''Create the <legend> element'''
        legend = self.doc.createElement("legend")

        for lyr in self.lyrlist:
            if (lyr.isGroupLayer == False):

                # Create the <legendlayer> element
                legendlayer = self.doc.createElement("legendlayer")
                legendlayer.setAttribute("open", "true")
                legendlayer.setAttribute("checked", "Qt::Checked")
                legendlayer.setAttribute("name", str(lyr.name))

                legend.appendChild(legendlayer)

                # Create the <filegroup> element
                filegroup = self.doc.createElement("filegroup")
                filegroup.setAttribute("open", "true")
                filegroup.setAttribute("hidden", "false")
                legendlayer.appendChild(filegroup)

                # Create the <legendlayerfile> element
                legendlayerfile = self.doc.createElement("legendlayerfile")
                legendlayerfile.setAttribute("isInOverview", "0")
                legendlayerfile.setAttribute("layerid", str(lyr.name) + str(20110427170816078))
                legendlayerfile.setAttribute("visible", "1")
                filegroup.appendChild(legendlayerfile)

        return legend

    def layers(self):
        '''Create the <projectlayers> element'''
        layers = self.doc.createElement("projectlayers")
        layers.setAttribute("layercount", str(len(self.lyrlist)))

        for lyr in self.lyrlist:

            if (lyr.isGroupLayer == False and lyr.isRasterLayer == False):
                geometry1 = arcpy.Describe(lyr)
                geometry2 = str(geometry1.shapeType)
                ds = self.doc.createTextNode(str(lyr.dataSource))

                name1 = self.doc.createTextNode(str(lyr.name) + str(20110427170816078))
                name2 = self.doc.createTextNode(str(lyr.name))

                # Create the <maplayer> element
                maplayer = self.doc.createElement("maplayer")
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

                # Create the <id> element
                _id = self.doc.createElement("id")
                _id.appendChild(name1)
                maplayer.appendChild(_id)

                # Create the <datasource> element
                datasource = self.doc.createElement("datasource")
                datasource.appendChild(ds)
                maplayer.appendChild(datasource)

                # Create the <layername> element
                layername = self.doc.createElement("layername")
                layername.appendChild(name2)
                maplayer.appendChild(layername)

                # Create the <srs> element
                srs = self.doc.createElement("srs")
                maplayer.appendChild(srs)

                spatialrefsys = self.generate_spatial()
                srs.appendChild(spatialrefsys)

                # Create the <transparencyLevelInt> element
                transparencyLevelInt = self.doc.createElement("transparencyLevelInt")
                transparency2 = self.doc.createTextNode("255")
                transparencyLevelInt.appendChild(transparency2)
                maplayer.appendChild(transparencyLevelInt)

                # Create the <customproperties> element
                customproperties = self.doc.createElement("customproperties")
                maplayer.appendChild(customproperties)

                # Create the <provider> element
                provider = self.doc.createElement("provider")
                provider.setAttribute("encoding", "System")
                ogr = self.doc.createTextNode("ogr")
                provider.appendChild(ogr)
                maplayer.appendChild(provider)

                # Create the <singlesymbol> element
                singlesymbol = self.doc.createElement("singlesymbol")
                maplayer.appendChild(singlesymbol)

                # Create the <symbol> element
                symbol = self.doc.createElement("symbol")
                singlesymbol.appendChild(symbol)

                # Create the <lowervalue> element
                lowervalue = self.doc.createElement("lowervalue")
                symbol.appendChild(lowervalue)

                # Create the <uppervalue> element
                uppervalue = self.doc.createElement("uppervalue")
                symbol.appendChild(uppervalue)

                # Create the <label> element
                label = self.doc.createElement("label")
                symbol.appendChild(label)

                # Create the <rotationclassificationfieldname> element
                rotationclassificationfieldname = self.doc.createElement("rotationclassificationfieldname")
                symbol.appendChild(rotationclassificationfieldname)

                # Create the <scaleclassificationfieldname> element
                scaleclassificationfieldname = self.doc.createElement("scaleclassificationfieldname")
                symbol.appendChild(scaleclassificationfieldname)

                # Create the <symbolfieldname> element
                symbolfieldname = self.doc.createElement("symbolfieldname")
                symbol.appendChild(symbolfieldname)

                 # Create the <outlinecolor> element
                outlinecolor = self.doc.createElement("outlinecolor")
                outlinecolor.setAttribute("red", "88")
                outlinecolor.setAttribute("blue", "99")
                outlinecolor.setAttribute("green", "37")
                symbol.appendChild(outlinecolor)

                 # Create the <outlinestyle> element
                outlinestyle = self.doc.createElement("outlinestyle")
                outline = self.doc.createTextNode("SolidLine")
                outlinestyle.appendChild(outline)
                symbol.appendChild(outlinestyle)

                # Create the <outlinewidth> element
                outlinewidth = self.doc.createElement("outlinewidth")
                width = self.doc.createTextNode("0.26")
                outlinewidth.appendChild(width)
                symbol.appendChild(outlinewidth)

                # Create the <fillcolor> element
                # Todo: correct colors"
                fillcolor = self.doc.createElement("fillcolor")
                fillcolor.setAttribute("red", "90")
                fillcolor.setAttribute("blue", "210")
                fillcolor.setAttribute("green", "229")
                symbol.appendChild(fillcolor)

                # Create the <fillpattern> element
                fillpattern = self.doc.createElement("fillpattern")
                fill = self.doc.createTextNode("SolidPattern")
                fillpattern.appendChild(fill)
                symbol.appendChild(fillpattern)

                # Create the <texturepath> element
                texturepath = self.doc.createElement("texturepath")
                texturepath.setAttribute("null", "1")
                symbol.appendChild(texturepath)

                # Append to parent
                layers.appendChild(maplayer)

        return layers

if __name__ == '__main__':
    from os import path
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-m", "--mxd", dest="mxd", help="input ArcGIS file")
    parser.add_option("-q", "--qgs", dest="qgs", help="destination QGIS file")

    options, args = parser.parse_args()

    try:
        m2q = mxd2qgs(options.mxd)

        # If no --qgs opt is passed, use the same path, just replace the file suffix
        output = options.qgs or path.join(path.dirname(options.mxd), path.basename(options.mxd)[:-3] + 'qgs')

        m2q.convert(options.qgs)

        print 'Converted', options.mxd, 'to', options.qgs

    except Exception, e:
        raise e
