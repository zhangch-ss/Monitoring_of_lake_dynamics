# GSW product TIF to shp.
# GSW product is derived from：https://global-surface-water.appspot.com/

import ogr
from osgeo import gdal, ogr, osr
import os
import datetime
import pandas as pd


def tif2shp(folder, mask_par, save_path, mask_name):
    inraster = gdal.Open(folder)  # Read the raster data in the path
    inband = inraster.GetRasterBand(1)  # This band is the last band that you want to convert to a shp.
    # If it is a single band data, it will be 1
    im_width = inraster.RasterXSize  # Read image XSize
    im_height = inraster.RasterYSize  # Read image YSize
    im_geotrans = inraster.GetGeoTransform()
    im_proj = inraster.GetProjection()  # Get projection
    im_data = inband.ReadAsArray(0, 0, im_width, im_height)
    # Create a water body mask, set the data in im_data = 2 (water body in GSW, mask_par) to 1 (Ture),
    # and data less than 2 to 0 (False)
    mask = (im_data >= mask_par).astype(int)
    # Water mask preservation path
    f_path, f_name = os.path.split(folder)
    if not os.path.exists(os.path.join(os.path.dirname(f_path), 'mask' + mask_name[5:])):
        os.mkdir(os.path.join(os.path.dirname(f_path), 'mask' + mask_name[5:]))
    mask_save_path = os.path.join(os.path.dirname(f_path), 'mask' + mask_name[5:], f_name[: -7] + '_mask.tif')
    # print(mask_save_path)
    driver = gdal.GetDriverByName('GTiff')  # The data type must have, how much memory space is needed to calculate
    data = driver.Create(mask_save_path, im_width, im_height, 1, gdal.GDT_Byte)
    data.SetGeoTransform(im_geotrans)  # Write affine transformation parameters
    data.SetProjection(im_proj)  # Write projection
    # print(data.GetProjection())
    data.GetRasterBand(1).WriteArray(mask)
    mask_raster = data.GetRasterBand(1)
    prj = osr.SpatialReference()
    # Read the projection information of raster data to prepare for the vector generated later
    prj.ImportFromWkt(inraster.GetProjection())
    # shp_save_path = os.path.join(f_path[: -5], 'shapefile', f_name[-18: -7])
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    outshp = os.path.join(save_path, f_name[: -7] + ".shp")
    drv = ogr.GetDriverByName("ESRI Shapefile")
    # If the file already exists, delete it and continue to do it again
    if os.path.exists(outshp):
        drv.DeleteDataSource(outshp)
    Polygon = drv.CreateDataSource(outshp)  # Create an object file
    # Create a layer for the shp file and define it as multiple surface types
    Poly_layer = Polygon.CreateLayer(f_name[: -7], srs=prj, geom_type=ogr.wkbMultiPolygon)
    # Add a field to the target shp file to store the pixel value of the original raster
    newField = ogr.FieldDefn('value', ogr.OFTReal)
    Poly_layer.CreateField(newField)
    # print(ogr.OFTReal)
    # Here, mask_raster is used as a mask for mask_raster to ensure that the output water body is the same value (1),
    # avoiding merging
    # The core function, which performs the raster-to-vector operation
    gdal.FPolygonize(mask_raster, mask_raster, Poly_layer, 0)
    Polygon.SyncToDisk()
    Polygon = None


# Similar to tif2shp
def tif2shp_bath(folder, mask_par):
    global im_width, im_geotrans
    start_time = datetime.datetime.now()
    os.chdir(folder)
    for raster in os.listdir(folder):
        inraster = gdal.Open(raster)
        inband = inraster.GetRasterBand(1)
        im_width = inraster.RasterXSize
        im_height = inraster.RasterYSize
        im_geotrans = inraster.GetGeoTransform()
        im_proj = inraster.GetProjection()
        im_data = inband.ReadAsArray(0, 0, im_width, im_height)
        mask = (im_data >= mask_par).astype(int)
        mask_save_path = os.path.join(folder[: -5], 'mask', raster[: -4] + '_mask.tif')
        # print(mask_save_path)
        if not os.path.exists(os.path.join(folder[: -5], 'mask')):
            os.mkdir(os.path.join(folder[: -5], 'mask'))
        driver = gdal.GetDriverByName('GTiff')
        data = driver.Create(os.path.join(mask_save_path), im_width, im_height, 1, gdal.GDT_Byte)
        data.SetGeoTransform(im_geotrans)
        data.SetProjection(im_proj)
        data.GetRasterBand(1).WriteArray(mask*256)
        mask_raster = data.GetRasterBand(1)
        prj = osr.SpatialReference()
        prj.ImportFromWkt(inraster.GetProjection())
        shp_save_path = os.path.join(folder[: -5], 'shapefile', raster[:-4])
        if not os.path.exists(shp_save_path):
            os.makedirs(shp_save_path)
        outshp = os.path.join(shp_save_path, raster[:-4] + ".shp")
        drv = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(outshp):
            drv.DeleteDataSource(outshp)
        Polygon = drv.CreateDataSource(outshp)
        Poly_layer = Polygon.CreateLayer(raster[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)

        newField = ogr.FieldDefn('value', ogr.OFTReal)
        Poly_layer.CreateField(newField)
        # print(ogr.OFTReal)
        gdal.FPolygonize(inband, mask_raster, Poly_layer, 0)
        Polygon.SyncToDisk()
        Polygon = None
    end_time = datetime.datetime.now()
    print("Succeeded at", end_time)
    print("Elapsed Time:", end_time - start_time)
    return im_geotrans, im_width


# projection information of 'WGS 84 / UTM zone 47N'，在'https://spatialreference.org/'可查询
img_proj_UTM47 = '''PROJCS["WGS 84 / UTM zone 47N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",99],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32647"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]'''
img_proj_UTM46 = '''PROJCS["WGS 84 / UTM zone 46N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",93],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32646"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]'''


# Calculate the shp area (the key point is to set the projected coordinate system)
def area(shpPath, project):
    data = os.path.basename(os.path.dirname(shpPath))
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shpPath, 1)
    layer = dataSource.GetLayer()
    spatialref_source = layer.GetSpatialRef()  # Get the source projected coordinate system, WGS-84
    spatialref_target = osr.SpatialReference()  # Define a new projected coordinate system
    spatialref_target.ImportFromWkt(project)  # Import the defined projected coordinate system
    # Create objects for projection transformation
    coordTrans = osr.CoordinateTransformation(spatialref_source, spatialref_target)
    area_list = []
    count = layer.GetFeatureCount()
    if count > 0:  # Avoid calculating empty shp
        for feature in layer:
            geom = feature.GetGeometryRef()  # For each feature, get geometric information
            geom.Transform(coordTrans)  # Projection transformation
            area = geom.GetArea()  # Calculate area
            m_area = area/1000000  # Unit changed from decimal system to meter
            area_list.append(m_area)
        dataSource = None
        lake_area = max(area_list)
        print(data,'area:',lake_area)
        return lake_area
    else:
        print(data,'area:','No Data')
        print('')


def tif2shp2area(tif_path):
    global im_pro
    print('Converting to shp file...')
    im_geo, im_width = tif2shp_bath(tif_path, 2)
    # print(im_geo)
    shp_name_list = os.listdir(os.path.join(tif_path[: -5], 'shapefile'))
    print('The shp file conversion is complete!')
    lake_area_list = []
    date_list = []
    print('Calculating lake area...')
    if im_geo[0] + im_geo[1] * im_width > 96.1:
        im_pro = img_proj_UTM47
    else:
        im_pro = img_proj_UTM46
    for shp_name in shp_name_list:
        # print(os.path.join(shp_path, shp_name, shp_name + '.shp'))
        lake_area = area(os.path.join(os.path.join(tif_path[: -5], 'shapefile'), shp_name, shp_name + '.shp'), im_pro)
        lake_area_list.append(lake_area)
        date_list.append(shp_name)

    data = pd.DataFrame(lake_area_list)
    data.columns = ['lake_area']
    data.insert(0, 'date', date_list)
    writer = pd.ExcelWriter(os.path.join(tif_path[: -5], 'lake_area_list.xlsx'))
    data.to_excel(writer, header=True, index=False, sheet_name='lake_area')
    writer.save()
    print('The lake area is calculated!')


if __name__ == '__main__':
    # Folder to store GSW raster data(tif)
    tif_path = ''
    tif2shp2area(tif_path)



