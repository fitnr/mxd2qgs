# mxd2qgs 
### Convert ArcGIS .mxd files for QGIS

Based on Mxd2Qgs for ArcGIS 10 by Allan Maungu (copyright 2011)

This utility can be installed as a toolbox in ArcGIS, or run on the command line to convert several files at once

### Installing in ArcGIS
Not yet ready for download, under active development.
TK

### Use as a Toolbox Script

1. Once layers are loaded on an ArcMap document, double click "ArcMap to Quantum GIS"
2. Specify name (with .qgs extension) and location of desired QGIS file and click OK.  
3. Open the resulting QGIS file.


## Use on the command line
* Run `python mxd2qgs.py --mxd path/to/file.mxd --qgs /path/to/newfile.qgs`

If you omit the `qgs` argument, the new file will be written to the same path as the old one. For example, `python mxd2qgs.py --mxd path/to/file.mxd` will create `path/to/file.qgs`.
