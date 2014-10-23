# mxd2qgs
## Convert ArcMap .mxd files to QGIS format

Based on Mxd2Qgs for ArcGIS 10 by Allan Maungu (copyright 2011).
The resulting file can be opened in Quantum GIS.

Converts [ArcMAP](http://www.esri.com/software/arcgis) mxd files for use in [QGIS](http://qgis.com).

This utility can be installed as a toolbox in ArcGIS, or run on the command line. Note that because of the limits of scripting in ArcGIS, layer symbologies are lost in the conversion.

Requirements: ArcMap 10 or higher.

Tested on ArcMap 10, Python 2.6.5 and Quantum GIS 1.6.0.

## Installing

There are several options for installing this software.

### As a toolbox

**Not yet ready for download, under active development.**

[Download the zip archive](https://github.com/fitnr/mxd2qgs/archive/master.zip) and install it. [Add the toolbox in ArcMap](http://webhelp.esri.com/arcgisdesktop/9.3/index.cfm?TopicName=Basic_toolbox_management). Converting is as simple as entering the desired path for the new QGIS file.

### With pip

Run `pip install mxd2qgs`. The mxd2qgs tool will be available on the command line.

### Build from source

Download or clone this package, and run `python setup.py install`.

You can also just download the package and use the as a python library. Prefix the below commands with `python `.

## Using the command line tool

By default, the converter outputs to stdout because I read on some UNIX website that was the cool thing to do.

```bash
# Saves to /path/to/newfile.qgs
mxd2qgs.py path/to/file.mxd > /path/to/newfile.qgs

# Use the --same or -s flag to save with same filename, but a different extension
# Saves to path/to/file.qgs
mxd2qgs.py --same path/to/file.mxd

# Specify a new path
# Saves to /new/path/save.qgs`
mxd2qgs.py path/to/file.mxd --qgs /new/path/save.qgs
````

## License

This software is licensed under the [GNU General Public License, version 2](http://www.gnu.org/licenses/gpl-2.0.html).