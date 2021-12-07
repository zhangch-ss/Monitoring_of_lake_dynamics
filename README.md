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

## Citation
Please cite our preliminary work if you use this code:.\
Zhang C, Lv A, Zhu W, Yao G, Qi S. Using Multisource Satellite Data to Investigate Lake Area, Water Level, and Water Storage Changes of Terminal Lakes in Ungauged Regions. Remote Sensing. 2021; 13(16):3221. https://doi.org/10.3390/rs13163221. .\
More detailed code explanations and application examples are under review in the form of academic articles.

## Welcome to communicate
Your comments and suggestions are welcome
