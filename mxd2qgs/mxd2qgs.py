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

    color = None

    geo_attrs = {
        'Point': {
            'class': "SimpleMarker",
            'type': 'marker',
        },
        'Polyline': {
            'class': "SimpleLine",
            'type': 'line',
        },
        'Polygon': {
            'class': "SimpleFill",
            'type': 'fill',
        },
    }

    target_path = None

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

        # Create a color generator
        self.color = colorgen()

        # Add method helpers
        self.geo_attrs['Point']['properties'] = self.symbol_props_line
        self.geo_attrs['Polyline']['properties'] = self.symbol_props_line
        self.geo_attrs['Polygon']['properties'] = self.symbol_props_polygon

    def convert(self, target_path=None):
        '''Run conversion and write to a file'''

        if target_path:
            self.target_path = path.abspath(target_path)

        # Give layers a unique ID
        assign_lyrids(self.layerlist)

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
                legendlayer.setAttribute("name", lyr.name)

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
            # longName looks like Group1\Group2\layer.name,
            # so dirname -> '' if layer.longName == layer.name
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

            treeDict[parent_name].appendChild(treeLayer)

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

        # Set relative path
        # self.target_path: (full path to qgs target directory)
        # C:/path/to/new/file.qgs
        # datasource (full path to SHP)
        # C:/path/to/directory/file.shp
        #
        # New relative path should be: ../directory/file.shp
        if self.target_path:
            data_path = path.relpath(layer.dataSource, self.target_path)
        else:
            data_path = layer.dataSource

        # Create the <datasource> element
        datasource = self.doc.createElement("datasource")
        datasource.appendChild(self.doc.createTextNode(data_path))
        maplayer.appendChild(datasource)

        if (layer.isRasterLayer == True):
            layer.geotype = 'raster'
            maplayer.setAttribute("type", "raster")
            pipe = self.doc.createElement('pipe')
            rr = self.doc.createElement('rasterrenderer')
            rr.setAttribute('opacity', layer.transparency / 100.0)
            pipe.appendChild(rr)
            maplayer.appendChild(pipe)

        else:  # Is Vector
            layer.geotype = arcpy.Describe(layer).shapeType
            maplayer.setAttribute("geometry", layer.geotype)
            maplayer.setAttribute("type", "vector")

            maplayer.setAttribute("simplifyDrawingHints", "1")
            maplayer.setAttribute("simplifyDrawingTol", "1")
            maplayer.setAttribute("simplifyMaxScale", "1")

            # Create the <renderer-v2> element
            renderer = self.symbol(layer)
            maplayer.appendChild(renderer)

        maplayer.setAttribute("hasScaleBasedVisibilityFlag", "0")
        maplayer.setAttribute("scaleBasedLabelVisibilityFlag", "0")

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
        provider.appendChild(self.doc.createTextNode("ogr"))
        maplayer.appendChild(provider)

        return maplayer

    def projectlayers(self):
        '''Create the <projectlayers> element'''
        layers = self.doc.createElement("projectlayers")
        layers.setAttribute("layercount", str(len(self.layerlist)))

        for layer in self.layerlist:
            if not layer.isGroupLayer and layer.supports('dataSource'):
                maplayer = self.maplayer(layer)
                layers.appendChild(maplayer)

        return layers

    def symbol_props_point(self):
        '''Return symbol properties for point layers'''
        return {
            'angle': '0',
            'color_border': next(self.color),
            'horizontal_anchor_point': '1',
            'name': 'circle',
            'offset_map_unit_scale': '0,0',
            'offset': '0,0',
            'offset_unit': "MM",
            'outline_style': "solid",
            'outline_width': "0",
            'outline_width_map_unit_scale': "0,0",
            'outline_width_unit': "MM",
            'scale_method': "area",
            'size': "2",
            'size_map_unit_scale': "0,0",
            'size_unit': "MM",
            'vertical_anchor_point': "1",
        }

    def symbol_props_line(self):
        '''Return symbol properties for polyline layers'''
        return {
            'capstyle': "square",
            'color': next(self.color),
            'customdash': "5;2",
            'customdash_map_unit_scale': "0,0",
            'customdash_unit': "MM",
            'draw_inside_polygon': "0",
            'joinstyle': "bevel",
            'offset': "0",
            'offset_map_unit_scale': "0,0",
            'offset_unit': "MM",
            'penstyle': "solid",
            'use_custom_dash': "0",
            'width': "0.26",
            'width_map_unit_scale': "0,0",
            'width_unit': "MM",
        }

    def symbol_props_polygon(self):
        '''Return symbol properties for polygon layers'''
        # border is a neutral gray, for simplicity
        return {
            'border_width_map_unit_scale': "0,0",
            'border_width_unit': "MM",
            'color': next(self.color),
            'color_border': "144,164,172,255",
            'joinstyle': "bevel",
            'offset': "0,0",
            'offset_map_unit_scale': "0,0",
            'offset_unit': "MM",
            'style': "solid",
            'style_border': "solid",
            'width_border': "0.5",
        }

    def symbol(self, layer):
        '''Create and populate a dummy symbol element'''
        # <renderer-v2 symbollevels="0" type="singleSymbol">
        #     <symbols>
        #         <symbol alpha="0.537255" type="fill" name="0">
        #             <prop k="border_width_map_unit_scale" v="0,0"/>
        #             ...
        #     <rotation/>
        #     <sizescale scalemethod="area"/>
        renderer = self.doc.createElement('renderer-v2')
        renderer.setAttribute('symbollevels', '0')
        renderer.setAttribute('type', 'singleSymbol')

        symbols = self.doc.createElement("symbols")
        renderer.appendChild(symbols)

        symbol = self.doc.createElement("symbol")
        symbols.appendChild(symbol)

        # point, polyline, or polygon?
        geo_attrs = self.geo_attrs[layer.geotype]

        symbol.setAttribute('alpha', str(transp_to_alpha(layer.transparency)))
        symbol.setAttribute('type', geo_attrs['type'])
        symbol.setAttribute('name', '0')

        # Create appropriate symbol
        symbol_layer = self.doc.createElement('layer')
        symbol_layer.setAttribute('class', geo_attrs['class'])
        symbol_layer.setAttribute('pass', '0')
        symbol_layer.setAttribute('locked', '0')

        for key, value in geo_attrs['properties']().items():
            prop = self.doc.createElement('prop')
            prop.setAttribute('k', key)
            prop.setAttribute('v', value)
            symbol_layer.appendChild(prop)

        symbol.appendChild(symbol_layer)

        renderer.appendChild(self.doc.createElement("rotation"))

        sizescale = self.doc.createElement("sizescale")
        sizescale.setAttribute('scalemethod', 'area')

        return renderer


def assign_lyrids(layerlist):
    '''QGIS uses a unique ID for each layer, assign it here'''
    for lyr in layerlist:
        # Mimic the datetime down to ms, but use a randint because looping is too fast
        lyr.mxd2qgs_id = '{0}{1}{2}'.format(lyr.name, datetime.now().strftime('%Y%m%d%H%M%S'), randint(100000, 999999))


def colorgen(alpha=255):
    '''Generator that eternally loops through a list of lovely matched lighter/darker colors '''
    # List of colors is adapted from http://colorbrewer2.org
    colors = [
        (166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44),
        (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0),
        (202, 178, 214), (106, 61, 154), (255, 255, 153), (177, 89, 40),
        (141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114),
        (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229),
        (217, 217, 217), (188, 128, 189), (204, 235, 197), (255, 237, 111)
    ]

    while True:
        item = colors.pop(0)
        out = '{0},{1},{2},{alpha}'.format(*item, alpha=alpha)
        yield out
        colors.append(item)


def transp_to_alpha(transparency, in_max=100, out_max=1):
    return out_max * (1 - transparency / float(in_max))


def main():
    from optparse import OptionParser
    import sys

    parser = OptionParser(
        usage='%prog [options] MXD [MXD ...]',
        description='Convert an MXD file to QGS format. Requires ArcPy.'
    )

    parser.add_option('-q', '--qgs', type=str, dest='path', help='destination directory of the new QGIS file (or exact file name if only one mxd file is given)')
    parser.add_option('-o', '--stdout', action='store_true', help='output to stdout (ignored if -q is set)')

    options, args = parser.parse_args()

    qgs_outdir, qgs_outfile, std_out_flag = False, False, False

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

                if not path.exists(qgs_outdir):
                    raise RuntimeError("Folder doesn't exist: {0}".format(qgs_outdir))

            else:
                qgs_outdir = options.path

            if not path.exists(qgs_outdir):
                raise RuntimeError("Output path doesn't exist")

        elif options.stdout:
            std_out_flag = True

        # Conversion loop
        for inputfile in args:
            m2q = mxd2qgs(inputfile)

            if std_out_flag:
                sys.stdout.write(m2q.convert() + linesep)

            else:
                outdir = qgs_outdir or path.dirname(inputfile)
                outfile = qgs_outfile or path.basename(inputfile)[:-3] + 'qgs'

                outputpath = path.join(outdir, outfile)

                if path.exists(outputpath):
                    raise RuntimeError("File already exists: {0}".format(outputpath))

                result = m2q.convert(target_path=qgs_outdir)

                with open(outputpath, 'wb') as handle:
                    handle.write(result)

    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
