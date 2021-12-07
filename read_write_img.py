import gdal


def read_img(filename):
    data = gdal.Open(filename)
    im_width = data.RasterXSize
    im_height = data.RasterYSize
    im_geotrans = data.GetGeoTransform()
    im_proj = data.GetProjection()
    im_data = data.ReadAsArray(0, 0, im_width, im_height)
    del data
    return im_proj, im_geotrans, im_data


def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape
    driver = gdal.GetDriverByName('GTiff')
    data = driver.Create(filename, im_width, im_height, im_bands, datatype)
    data.SetGeoTransform(im_geotrans)
    data.SetProjection(im_proj)
    if im_bands == 1:
        data.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            data.GetRasterBand(i + 1).WriteArray(im_data[i])
    del data