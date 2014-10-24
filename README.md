# mxd2qgs
## Convert ArcMap .mxd files to QGIS format

Based on Mxd2Qgs for ArcGIS 10 by Allan Maungu (copyright 2011).
The resulting file can be opened in Quantum GIS.

Converts [ArcMAP](http://www.esri.com/software/arcgis) mxd files for use in [QGIS](http://qgis.com).

This utility can be installed as a toolbox in ArcGIS, or run on the command line.

## Limitations
Because of the shortcomings of the ArcGIS api, and the differences between ArcMap and QGIS, the converter has some limitations:
* layer symbologies are lost in the conversion.
* QGIS lacks Data Frames. All of the layers from each Data Frame in the mxd document will be addded, but the spatial settings from only one ArcMap Data Frame (generally the first) will be converted.
* Proprietary ESRI formats (e.g. sdc) won't work in QGIS.

Requirements: ArcMap 10 or higher.

Tested on ArcMap 10, Python 2.6.5 and Quantum GIS 1.6.0.

## Installing

There are several options for installing this software.

### As a toolbox

[Download the zip archive](https://github.com/fitnr/mxd2qgs/archive/master.zip) and unzip it to somewhere handy, like your `My Documents\ArcGIS` folder. [Add the toolbox in ArcMap](http://webhelp.esri.com/arcgisdesktop/9.3/index.cfm?TopicName=Basic_toolbox_management). Run the script and enter the desired path for the new QGIS file.

### With pip

Run `pip install mxd2qgs`. The mxd2qgs tool will be available on the command line.

### Build from source

Download or clone this package, and run `python setup.py install`.

## Using the command line tool

Using the `mxd2qgs` command depnds on having your PATH properly set up. If it work and you don't want to worry about your PATH, try `python mxd2qgs/mxd2qgs.py [args]` or python -m mxd2qgs.mxd2qgs [args]`.

```bash
# convert with the same file name, differet extension
mxd2qgs path/to/file.mxd
# save to path/to/file.qgs

# convert several files
mxd2qgs path/to/file2.mxd foo/file.mxd bar/file.mxd
# save to path/to/file2.qgs, foo/file.qgs, bar/file.qgs, respectively

# specify a completely new path or file name
mxd2qgs path/to/file.mxd --qgs new/path/name.qgs
# saves to new/path/name.qgs

# If the input for `--qgs` doesn't end in '.qgs' the converter assumes you're giving a path
mxd2qgs path/to/file.mxd --qgs new/path
# saves to new/path/file.qgs

mxd2qgs path/to/file.mxd path/to/file2.mxd --qgs new/path
# saves to new/path/file.qgs and new/path/file2.qgs, respectively

# Output to stdout
mxd2qgs -o path/to/file.mxd
# [long xml output clipped]
````

The converter doesn't convert or edit the paths of your feature class/layers at all, so the option to save to a new location is just there to be friendly.

## License

This software is licensed under the [GNU General Public License, version 2](http://www.gnu.org/licenses/gpl-2.0.html).