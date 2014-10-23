from setuptools import setup

setup(
    name='mxd2qgs',
    version='0.1.0',

    description='Convert ArcMap .mxd files to QGIS format',
    long_description="Converts from mxd to qgs. Tools works on the command line, or with the included toolbox.",
    url='https://github.com/fitnr/mxd2qgs',

    author='Neil Freeman',
    author_email='contact@fakeisthenewreal.org',

    license='GPLv2',
    keywords='arcgis arcmap arcpy esri mxd qgis gis',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Topic :: Scientific/Engineering :: GIS'
    ],

    packages=['mxd2qgs'],
    install_requires=['arcpy'],
    entry_points={
        'console_scripts': [
            'mxd2qgs=mxd2qgs.mxd2qgs:main',
        ],
    },
)
