#!/usr/bin/env python
#
# mxd2qgs
# https://github.com/fitnr/mxd2qgs
# Converts ArcMap documents to .qgs format

# Copyright (c) 2014 Neil Freeman, except for portions (c) 2011 Allan Maungu
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

from xml.dom.minidom import Document
from datetime import datetime
from random import randint
from os import linesep, path
import arcpy

class mxd2qgs(object):

    """Conversion wrapper"""

    def __init__(self, mxdfile=None):
        # Assign the input file
        mxdfile = mxdfile or "CURRENT"

        try:
            self.mxd = arcpy.mapping.MapDocument(mxdfile)
        except AssertionError, e:
            raise AssertionError('error importing' + mxdfile + ': ' + e.message)

        # Create the minidom
        self.doc = Document()

        # Dataframe elements
        dfs = arcpy.mapping.ListDataFrames(self.mxd)
        self.df = dfs.pop(0)

        # All the layers in all the data frames go in the layer list
        self.layerlist = [y for f in dfs for y in arcpy.mapping.ListLayers(f)]

    def convert(self):
        '''Run conversion and write to a file'''
        # Create the <qgis> base element
        qgis = self.doc.createElement("qgis")
        qgis.setAttribute("projectname", " ")
        qgis.setAttribute("version", "2.4.0-Chugiak")
        self.doc.appendChild(qgis)

        # Create the <title> element
        title = self.doc.createElement("title")
        qgis.appendChild(title)

        layertree, layer_tree_canvas = self.layertrees()
        qgis.appendChild(layertree)
        qgis.appendChild(layer_tree_canvas)

        canvas = self.canvas()
        qgis.appendChild(canvas)

        # Make sure layers have a unique ID
        assign_lyrids(self.layerlist)

        layers = self.projectlayers()
        qgis.appendChild(layers)

        legend = self.legend()
        qgis.appendChild(legend)

        # ArcPy documentation is quite insistent about deleting file references
        # Maybe something is wrong with their garbage collection?
        del(self.mxd)

        # xml.dom.minidom.Document can't handle the !doctype
        return "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>" + self.doc.toxml()

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

        return spatialrefsys

    def legend(self):
        '''Create the <legend> element'''
        legend = self.doc.createElement("legend")

        for lyr in self.layerlist:
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

                legendlayerfile.setAttribute("layerid", lyr.mxd2qgs_id)
                legendlayerfile.setAttribute("visible", "1")
                filegroup.appendChild(legendlayerfile)

        return legend

    def maketree(self, layer, treeElemName):
        tree = self.doc.createElement(treeElemName)
        props = self.doc.createElement('customproperties')
        tree.appendChild(props)

        tree.setAttribute('id', layer.mxd2qgs_id)
        tree.setAttribute('name', layer.name)

        if layer.supports('visible'):
            checked = 'Qt::Checked' if layer.visible else 'Qt::Unchecked'
            tree.setAttribute('checked', checked)

        return tree

    def layertrees(self):
        '''Create the <layer-tree-group> and <layer-tree-canvas> elements'''
        layer_tree_canvas = self.doc.createElement('layer-tree-canvas')
        custom_order = self.doc.createElement('custom-order')
        custom_order.setAttribute('enabled', '0')
        layer_tree_canvas.appendChild(custom_order)

        # top level tree is expanded, checked & unnamed
        layer_tree = self.doc.createElement('layer-tree-group')
        layer_tree.setAttribute("expanded", "1")
        layer_tree.setAttribute("checked", "Qt::Checked")
        layer_tree.setAttribute("name", "")

        # tracking dict for nesting layers,
        # populated with the parent tree-group
        treeDict = {u'': layer_tree}

        for layer in self.layerlist:
            # '' if longName == name
            parent_name = path.basename(path.dirname(layer.longName))

            if layer.isGroupLayer:
                treeLayer = self.maketree(layer, 'layer-tree-group')
                treeDict[layer.name] = treeLayer

            else:
                treeLayer = self.maketree(layer, 'layer-tree-layer')
                treeLayer.setAttribute('id', layer.mxd2qgs_id)

                custom_order_item = self.doc.createElement('item')
                custom_order_item.appendChild(self.doc.createTextNode(layer.mxd2qgs_id))
                custom_order.appendChild(custom_order_item)

            layer_tree[parent_name].appendChild(treeLayer)

        return layer_tree, layer_tree_canvas

    def maplayer(self, layer):
        # Create the <maplayer> element
        maplayer = self.doc.createElement("maplayer")
        maplayer.setAttribute("minimumScale", "0")
        maplayer.setAttribute("maximumScale", "1e+08")
        maplayer.setAttribute("minLabelScale", "0")
        maplayer.setAttribute("maxLabelScale", "1e+08")

        # Create the <id> element
        _id = self.doc.createElement("id")
        _id.appendChild(self.doc.createTextNode(layer.mxd2qgs_id))
        maplayer.appendChild(_id)

        # Create the <datasource> element
        datasource = self.doc.createElement("datasource")
        datasource.appendChild(self.doc.createTextNode(layer.dataSource))
        maplayer.appendChild(datasource)

        if(layer.isRasterLayer == True):
            maplayer.setAttribute("type", "raster")
            pipe = self.doc.createElement('pipe')
            rr = self.doc.createElement('rasterrenderer')
            rr.setAttribute('opacity', layer.transparency / 100.0)
            pipe.appendChild(rr)
            maplayer.appendChild(pipe)

        else:  # Is Vector
            geotype = str(arcpy.Describe(layer).shapeType)
            maplayer.setAttribute("geometry", geotype)
            maplayer.setAttribute("type", "vector")

        maplayer.setAttribute("hasScaleBasedVisibilityFlag", "0")
        maplayer.setAttribute("scaleBasedLabelVisibilityFlag", "0")
        maplayer.setAttribute("simplifyDrawingHints", "1")
        maplayer.setAttribute("simplifyDrawingTol", "1")
        maplayer.setAttribute("geometry", "Polygon")
        maplayer.setAttribute("simplifyMaxScale", "1")

        # Create the <layername> element
        layername = self.doc.createElement("layername")
        layername.appendChild(self.doc.createTextNode(layer.name))
        maplayer.appendChild(layername)

        # Create the <srs> element
        srs = self.doc.createElement("srs")
        srs.appendChild(self.generate_spatial())
        maplayer.appendChild(srs)

        # Create the <customproperties> element
        # commented out because it's needless
        # maplayer.appendChild(self.doc.createElement("customproperties"))

        # Create the <provider> element
        provider = self.doc.createElement("provider")
        provider.setAttribute("encoding", "System")
        ogr = self.doc.createTextNode("ogr")
        provider.appendChild(ogr)
        maplayer.appendChild(provider)

        # Create the <singlesymbol> element
        singlesymbol = self.doc.createElement("singlesymbol")

        # Create the <symbol> element
        symbol = self.symbol()
        singlesymbol.appendChild(symbol)

        maplayer.appendChild(singlesymbol)

        return maplayer

    def projectlayers(self):
        '''Create the <projectlayers> element'''
        layers = self.doc.createElement("projectlayers")
        layers.setAttribute("layercount", str(len(self.layerlist)))

        for layer in self.layerlist:
            if not layer.isGroupLayer:
                maplayer = self.maplayer(layer)
                layers.appendChild(maplayer)

        return layers

    def symbol(self):
        '''Create and populate a dummy symbol element'''
        symbol = self.doc.createElement("symbol")
        # Create the <lowervalue> element
        symbol.appendChild(self.doc.createElement("lowervalue"))

        # Create the <uppervalue> element
        symbol.appendChild(self.doc.createElement("uppervalue"))

        # Create the <label> element
        symbol.appendChild(self.doc.createElement("label"))

        # Create the <rotationclassificationfieldname> element
        rotationclassificationfieldname = self.doc.createElement("rotationclassificationfieldname")
        symbol.appendChild(rotationclassificationfieldname)

        # Create the <scaleclassificationfieldname> element
        scaleclassificationfieldname = self.doc.createElement("scaleclassificationfieldname")
        symbol.appendChild(scaleclassificationfieldname)

        # Create the <symbolfieldname> element
        symbol.appendChild(self.doc.createElement("symbolfieldname"))

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

def assign_lyrids(layerlist):
    '''QGIS uses a unique ID for each layer, assign it here'''
    for lyr in layerlist:
        # Mimic the datetime down to ms, but use a randint because looping is too fast
        lyr.mxd2qgs_id = '{0}{1}{2}'.format(lyr.name, datetime.now().strftime('%Y%m%d%H%M%S'), randint(100000, 999999))

def main():
    from optparse import OptionParser
    import sys

    parser = OptionParser(
        usage='%prog [options] MXD [MXD ...]',
        description='Convert an MXD file to QGS format. Requires ArcPy.'
    )

    parser.add_option('-q', '--qgs', type=str, dest='path', help='destination directory of the new QGIS file (or exact file name only one argument is sent)')
    parser.add_option('-o', '--stdout', action='store_true', help='output to stdout (ignored if -q is set)')

    options, args = parser.parse_args()

    qgs_outdir, qgs_outfile = False, False

    try:
        # Set output directories (and sometimes paths)
        if len(args) == 0:
            raise RuntimeError("Missing input file")

        if options.path:
            # Only got one argument and it ends in qgs:
            # Offer to use a full path with a filename, or just a directory
            if len(args) == 1 and options.path[-4:] == '.qgs':

                if path.exists(options.path):
                    raise RuntimeError("File already exists: {0}".format(options.path))

                qgs_outdir = path.dirname(options.path)
                qgs_outfile = path.basename(options.path)

            else:
                qgs_outdir = options.path

            if not path.exists(qgs_outdir):
                raise RuntimeError("Output path doesn't exist")

        elif options.stdout:
            std_out_flag = True            

        # Conversion loop
        for inputfile in args:
            result = mxd2qgs(inputfile).convert()

            if std_out_flag:
                sys.stdout.write(result + linesep)

            else:
                outdir = qgs_outdir or path.dirname(inputfile)
                outfile = qgs_outfile or path.basename(inputfile)[:-3] + 'qgs'

                outputpath = path.join(outdir, outfile)

                if path.exists(outputpath):
                    raise RuntimeError("File already exists: {0}".format(outputpath))

                with open(outputpath, 'wb') as handle:
                    handle.write(result)

    except Exception as e:
        sys.stderr.write(repr(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
