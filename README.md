# mxd2qgs 
### Convert ArcGIS .mxd files for QGIS

Based on Mxd2Qgs for ArcGIS 10 by Allan Maungu (copyright 2011)

This utility can be installed as a toolbox in ArcGIS, or run on the command line to convert several files at once.

Note that because of the limits of scripting in ArcGIS, layer symbologies are lost in the conversion

### Installing in ArcGIS
Not yet ready for download, under active development.
TK

### Use as a Toolbox Script

1. Once layers are loaded on an ArcMap document, double click "ArcMap to Quantum GIS"
2. Specify name (with .qgs extension) and location of desired QGIS file and click OK.  
3. Open the resulting QGIS file.


## Use on the command line
* Run `python mxd2qgs.py -O path/to/file.mxd # Saves to path/to/file.qgs`
* Run `python mxd2qgs.py path/to/file.mxd > /path/to/newfile.qgs # outputs to /path/to/newfile.qgs`
* Run `python mxd2qgs.py path/to/file.mxd --qgs /new/path/newfile.qgs # Saves to /new/path/newfile.qgs`
