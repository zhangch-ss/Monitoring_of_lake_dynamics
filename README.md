# Monitoring of lake dynamics
This is a program that uses multi-source remote sensing data to monitor the dynamic changes of lakes.
The detailed introduction of the modified procedure and specific application examples will be presented in the form of a paper in the near future.

## Multisource satellite data processing
The program supports the processing of multi-source satellite images (Landsat, Sentinel) and multi-source satellite altimetry data(CryoSat2, ICESat2, Sentinel3).
Including extracting lake water bodies from GSW data, extracting lake area, and extracting lake water level.

## Instructions for use
To use this program, you need to use the water index image as input. It is recommended to use Google earth engine(GEE) to calculate the water index.
Other precautions are detailed in the program.

## Requirements
Please use python 3.7.
Other dependent packages include gdal, opencv, etc.,in requirements.txt. Just follow the prompts and click install.

## Image preprocessing
1. [Calculate MNDWI in GEE](https://code.earthengine.google.com/?scriptPath=users%2Fa1091679080%2Flandsat8%3ALandsat7_download)
2. [Export to Google drive](https://blog.csdn.net/qq_45723511/article/details/120006690)

## Citation
Please cite our works if you use this code:\
https://doi.org/10.3390/rs13163221. 
\
https://doi.org/10.1016/j.jhydrol.2022.127888

## Welcome to communicate
Your comments and suggestions are welcome
