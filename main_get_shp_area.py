# This is a program used to obtain lake water body and lake area from water index images(tif)
# water index images (tif) are available on the GEE platform
# The method of selecting the segmentation threshold of lake water body is OTSU


from Index_processing import quyun, ostu, lvbo
import os
import numpy as np
from read_write_img import read_img, write_img
import cv2
from GSW_tif2shp2area import tif2shp, area
import pandas as pd
import time
import shutil


# This is UTM projection information.
# Qaidam Basin contains UTM46 and UTM47
# Available from https://spatialreference.org/
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


def water_index_filter(after_quyun_data):
    for i in range(1, after_quyun_data.shape[0] - 1):
        for j in range(1, after_quyun_data.shape[1] - 1):
            if abs(after_quyun_data[i][j] < 1):
                count = 1
                filter = after_quyun_data[i-count:i+(count+1), j-count:j+(count+1)]
                filter[filter > 1] = np.nan
                filter[filter < -1] = np.nan
                after_quyun_data[i][j] = np.nanmean(filter)
                if after_quyun_data[i][j] == np.nan:
                    count += 1
                    filter1 = after_quyun_data[i - count:i + (count + 1), j - count:j + (count + 1)]
                    filter1[filter1 > 1] = np.nan
                    filter1[filter1 < -1] = np.nan
                    after_quyun_data[i][j] = np.nanmean(filter)
    return after_quyun_data


def all_area_shp(file_path, alt_path):
    global img_proj, shapefile_other1_list, shapefile_other2_list
    alt_sign = os.path.basename(os.path.dirname(alt_path))
    img_sign = os.path.basename(os.path.dirname(file_path)).split('_')[-1]
    print(img_sign, alt_sign)
    if alt_sign == 'CryoSat2':
        file_path = os.path.dirname(file_path) + '/match_CS'
    elif alt_sign == 'ICESat2':
        file_path = os.path.dirname(file_path) + '/match_ICE2'
    elif alt_sign == 'Sentinel3':
        file_path = os.path.dirname(file_path) + '/match_ST3'
    else:
        print('Unrecognized altimetry data!')
    shapefile_sign_list = ['ST3', 'ICE2', 'CS']
    # print(shapefile_sign_list)
    shapefile_sign = str(os.path.basename(file_path).split('_')[-1])
    # print(shapefile_sign)
    shapefile_sign_list.remove(shapefile_sign)
    other1_shapefile_sign = shapefile_sign_list[0]
    other2_shapefile_sign = shapefile_sign_list[1]
    # print(other2_shapefile_sign)
    file_name_list = os.listdir(file_path)
    # result_path = 'J:/Remote_Sensing_Image/tuosu/Tuosu_landsat/quyun/'
    write_img_path = os.path.dirname(file_path) + '/quyun_' + shapefile_sign
    # 'J:/Remote_Sensing_Image/tuosu/Tuosu_landsat/OTSU'
    write_OTSU_path = os.path.dirname(file_path) + '/OTSU_' + shapefile_sign
    # result_file_path2 = 'J:/Remote_Sensing_Image/tuosu/Tuosu_landsat/color'
    write_color_path = os.path.dirname(file_path) + '/color_' + shapefile_sign
    shapefile = os.path.join(os.path.dirname(file_path), 'shapefile_' + shapefile_sign)
    if not os.path.exists(os.path.join(shapefile)):
        os.makedirs(os.path.join(shapefile))
    if not os.path.exists(os.path.join(write_img_path)):
        os.makedirs(os.path.join(write_img_path))
    if not os.path.exists(os.path.join(write_OTSU_path)):
        os.makedirs(os.path.join(write_OTSU_path))
    if not os.path.exists(os.path.join(write_color_path)):
        os.makedirs(os.path.join(write_color_path))
    date_list = []

    shapefile_other1 = os.path.join(os.path.dirname(file_path), 'shapefile_' + other1_shapefile_sign)
    shapefile_other2 = os.path.join(os.path.dirname(file_path), 'shapefile_' + other2_shapefile_sign)
    try:
        shapefile_other1_list = os.listdir(shapefile_other1)
        shapefile_other2_list = os.listdir(shapefile_other2)
    except:
        print('')
    for file_name in file_name_list:
        print('File name', file_name)
        date = file_name[: -4]
        date_list.append(date)
        # If shp exists in other shapefiles, copy it directly
        if os.path.exists(shapefile_other1):
            if date in shapefile_other1_list:
                print('shapefile_' + other1_shapefile_sign + 'Existing file, copy to shapefile_' + shapefile_sign)
                if not os.path.exists(os.path.join(shapefile, str(date))):
                    shutil.copytree(os.path.join(shapefile_other1, str(date)),
                                    os.path.join(shapefile, str(date)))
        try:
            if os.path.exists(shapefile_other2):
                if date in shapefile_other2_list:
                    print('shapefile_' + other2_shapefile_sign + 'Existing file, copy to shapefile_' + shapefile_sign)
                    if not os.path.exists(os.path.join(shapefile, str(date))):
                        shutil.copytree(os.path.join(shapefile_other2, str(date)),
                                        os.path.join(shapefile, str(date)))
        except:
            print('')
        if not os.path.exists(os.path.join(shapefile, str(date))):
            img_proj = OTSU_img(file_path, file_name, shapefile_sign, write_img_path, write_OTSU_path, write_color_path, img_sign)
        else:
            print('File already exists')
    shapefile_ST3_list = os.listdir(shapefile)
    # print(shapefile_ST3_list)
    try:
        lake_area(file_path, shapefile_ST3_list, shapefile_sign, img_proj)
    except NameError:
        _, im_geotrans2, image_slave = read_img(os.path.join(file_path, os.listdir(file_path)[0]))
        print(os.path.join('/'.join(file_path.split('/')[0: -2]), 'Location.txt'))
        if not os.path.exists(os.path.join('/'.join(file_path.split('/')[0: -2]), 'Location.txt')):
            location = [im_geotrans2[3], im_geotrans2[3] + im_geotrans2[5] * image_slave.shape[0], im_geotrans2[0],
                        im_geotrans2[0] + im_geotrans2[1] * image_slave.shape[1]]
            # print(location)
            np.savetxt(os.path.join('/'.join(file_path.split('/')[0: -2]), 'Location.txt'), location)
        if im_geotrans2[0] + im_geotrans2[1] + image_slave.shape[1] > 96.1:
            img_proj = img_proj_UTM47
        else:
            img_proj = img_proj_UTM46
        lake_area(file_path, shapefile_ST3_list, shapefile_sign, img_proj)


def OTSU_img(file_path, file_name, shp_sign, write_img_path, write_OTSU_path, write_color_path, img_sign):
    im_proj2, im_geotrans2, image_slave = read_img(os.path.join(file_path, file_name))
    if not os.path.exists(os.path.join('/'.join(file_path.split('/')[0: -2]), 'Location.txt')):
        location = [im_geotrans2[3], im_geotrans2[3] + im_geotrans2[5] * image_slave.shape[0], im_geotrans2[0],
                    im_geotrans2[0] + im_geotrans2[1] * image_slave.shape[1]]
        # print(location)
        np.savetxt(os.path.join('/'.join(file_path.split('/')[0: -2]), 'Location.txt'), location)

    if im_geotrans2[0] + im_geotrans2[1]*image_slave.shape[1] > 96.1:
        img_proj = img_proj_UTM47
    else:
        img_proj = img_proj_UTM46
    # print(img_proj)
    if (len(image_slave[np.isnan(image_slave)])) / (image_slave.shape[0] * image_slave.shape[1]) < 0.8:
        print('Meet the cloud cover conditions,denoising...')
        if img_sign == 'Landsat7':
            quyun_image_slave = quyun(image_slave)
            # 确保NDWI的范围在-1-1之间
            # quyun_image_slave = NDWI_filter(quyun_image_slave)
            quyun_image_slave[quyun_image_slave > 1] = 0.5
            quyun_image_slave[quyun_image_slave < -1] = -0.5
            # # 一般情况下，landsat7加滤波
            quyun_image_slave = lvbo(quyun_image_slave)
        else:
            image_slave[image_slave > 1] = 0.5
            image_slave[image_slave < -1] = -0.5
            quyun_image_slave = image_slave
    else:
        quyun_image_slave = np.random.rand(image_slave.shape[0], image_slave.shape[1])
        # print(quyun_image_slave)
        # print(quyun_image_slave)
        print('Excessive cloudiness')
    write_img(os.path.join(write_img_path, file_name[: -4] + '_CR.tif'), im_proj2, im_geotrans2, quyun_image_slave)
    print('Denoising is complete, OTSU is automatically segmenting...')
    dst_Otsu, best_thresold_NDWI, dst = ostu(quyun_image_slave)
    print('The segmentation is complete, it is being converted to a shp file...')
    tif2shp(os.path.join(write_img_path, file_name[: -4] + '_CR.tif'), best_thresold_NDWI,
            os.path.join(os.path.dirname(write_img_path), 'shapefile_' + shp_sign, file_name[: -4]), os.path.basename(file_path))
    print('The shapefile conversion is complete!')
    cv2.imwrite(os.path.join(write_OTSU_path, file_name[: -4] + '_OTSU.tif'), dst_Otsu)
    cv2.imwrite(os.path.join(write_color_path, file_name[: -4] + '_color.tif'), dst)
    return img_proj


def lake_area(file_path, shapefile_ST3_list, img_sign, img_proj):
    lake_area_list = []
    date_list = []
    for shp_name in shapefile_ST3_list:
        # print(os.path.join(shp_path, shp_name, shp_name + '.shp'))
        # print(os.path.join(os.path.join(os.path.dirname(file_path), 'shapefile_' + img_sign)))
        lake_area = area(os.path.join(os.path.join(os.path.dirname(file_path), 'shapefile_' + img_sign), shp_name, shp_name + '.shp'), img_proj)
        lake_area_list.append(lake_area)
        date_list.append(shp_name)

    data = pd.DataFrame(lake_area_list)
    data.columns = ['lake_area']
    data.insert(0, 'date', date_list)
    writer = pd.ExcelWriter(os.path.join(os.path.abspath(os.path.dirname(file_path)), 'lake_area_' + img_sign + '.xlsx'))
    data.to_excel(writer, header=True, index=False, sheet_name='lake_area')
    writer.save()


if __name__ == '__main__':
    # Folder for storing water index(tif)
    file_path = ''
    # Folder for storing satellite altimetry data
    alt_path = ''
    start = time.time()
    all_area_shp(file_path, alt_path)
    end = time.time()
    print(end-start)