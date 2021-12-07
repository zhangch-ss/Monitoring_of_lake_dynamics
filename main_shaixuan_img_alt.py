# This program is to obtain remote sensing images and satellite altimetry data paris
# within a certain number of days of date difference, the time interval we set is 7 days

import os
from dateutil.parser import parse
from matplotlib.pylab import date2num
import shutil


def ICESat2_filter(img_path, cegao_path):
    # Image sign, used to identify the input image type, currently supports Landsat 7/8 and Sentinel 2
    img_sign = os.path.basename(os.path.dirname(img_path)).split('_')[1]
    print(img_sign,':','ICESat2')
    # Create a folder. Save matching images
    img_pipei_path = os.path.join(os.path.dirname(img_path), 'match_ICE2')
    if os.path.exists(img_pipei_path):
        shutil.rmtree(img_pipei_path)
    if not os.path.exists(img_pipei_path):
        os.makedirs(img_pipei_path)
    # Create a folder to store the matching height measurement data
    cegao_pipei_path = os.path.join(os.path.dirname(cegao_path), img_sign, 'match_ICE2')
    if os.path.exists(cegao_pipei_path):
        shutil.rmtree(cegao_pipei_path)
    if not os.path.exists(cegao_pipei_path):
        os.makedirs(cegao_pipei_path)
    # Additional matching images (because the height measurement data is relatively small)
    img_pipei_extra_path = os.path.join(os.path.dirname(img_path), 'extra_match_ICE2')
    if os.path.exists(img_pipei_extra_path):
        shutil.rmtree(img_pipei_extra_path)
    if not os.path.exists(img_pipei_extra_path):
        os.makedirs(img_pipei_extra_path)
    # Obtain the name of the image and altimetry data (the time of data acquisition is in the name)
    img_name_list = os.listdir(img_path)
    cegao_name_list = os.listdir(cegao_path)
    # Traverse. Based on the altimetry data, select the image data within 7 days of the difference
    if img_sign != 'Sentinel2':
        for cegao_name in cegao_name_list:
            # Count. Used to identify additional matching images, count>1 means additional matching
            count = 0
            for img_name in img_name_list:
                # print(cegao_name)
                # Calculate the time interval between the two types of data
                # (convert a number similar to 20211109 into a date format)
                # GEE downloaded Landsat video, [12:20] is the date. ICESat altimetry data, [6:14] is the date
                date_residual = date2num(parse(str(img_name[12:20]))) - date2num(parse(str(cegao_name[6:14])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[12:20] + '.tif'))
                        print('Redundant image data')
                    else:
                        shutil.copy(os.path.join(cegao_path, cegao_name), os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[12:20] + '.tif'))
                        print(cegao_name[6:14], img_name[12:20])
                        img_name_list.remove(img_name)
    else:
        for cegao_name in cegao_name_list:
            count = 0
            for img_name in img_name_list:
                date_residual = date2num(parse(str(img_name[:8]))) - date2num(parse(str(cegao_name[6:14])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[:8] + '.tif'))
                        print('Redundant image data')
                    else:
                        shutil.copy(os.path.join(cegao_path, cegao_name), os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[:8] + '.tif'))
                        print(cegao_name[6:14], img_name[:8])
                        img_name_list.remove(img_name)
    print('Data filtering is complete!')


def Sentinel3_filter(img_path, cegao_path):
    img_sign = os.path.basename(os.path.dirname(img_path)).split('_')[1]
    print(img_sign,':','Sentinel3')
    img_pipei_path = os.path.join(os.path.dirname(img_path), 'match_ST3')
    if os.path.exists(img_pipei_path):
        shutil.rmtree(img_pipei_path)
    if not os.path.exists(img_pipei_path):
        os.makedirs(img_pipei_path)
    cegao_pipei_path = os.path.join(os.path.dirname(cegao_path), img_sign, 'match_ST3')
    if os.path.exists(cegao_pipei_path):
        shutil.rmtree(cegao_pipei_path)
    if not os.path.exists(cegao_pipei_path):
        os.makedirs(cegao_pipei_path)
    img_pipei_extra_path = os.path.join(os.path.dirname(img_path), 'extra_match_ST3')
    # print(img_pipei_extra_path)
    if os.path.exists(img_pipei_extra_path):
        shutil.rmtree(img_pipei_extra_path)
    if not os.path.exists(img_pipei_extra_path):
        os.makedirs(img_pipei_extra_path)
    img_name_list = os.listdir(img_path)
    cegao_name_list = os.listdir(cegao_path)
    if img_sign != 'Sentinel2':
        for cegao_name in cegao_name_list:
            count = 0
            for img_name in img_name_list:
                date_residual = date2num(parse(str(img_name[12:20]))) - date2num(parse(str(cegao_name[16:24])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[12:20] + '.tif'))
                        print('Redundant image data')
                    else:
                        print(img_name[12:20], cegao_name[16:24])
                        shutil.copytree(os.path.join(cegao_path, cegao_name),
                                        os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[12:20] + '.tif'))
                        img_name_list.remove(img_name)
    else:
        for cegao_name in cegao_name_list:
            count = 0
            for img_name in img_name_list:
                date_residual = date2num(parse(str(img_name[:8]))) - date2num(parse(str(cegao_name[16:24])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[:8] + '.tif'))
                        print('Redundant image data')
                    else:
                        shutil.copytree(os.path.join(cegao_path, cegao_name), os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[:8] + '.tif'))
                        print(img_name[:8], cegao_name[16:24])
                        img_name_list.remove(img_name)
    print('Data filtering is complete!')


def CryoSat2_filter(img_path, cegao_path):
    img_sign = os.path.basename(os.path.dirname(img_path)).split('_')[1]
    print(img_sign,':','CryoSat2')
    img_pipei_path = os.path.join(os.path.dirname(img_path), 'match_CS')
    if os.path.exists(img_pipei_path):
        shutil.rmtree(img_pipei_path)
    if not os.path.exists(img_pipei_path):
        os.makedirs(img_pipei_path)
    cegao_pipei_path = os.path.join(os.path.dirname(cegao_path), img_sign, 'match_CS')
    if os.path.exists(cegao_pipei_path):
        shutil.rmtree(cegao_pipei_path)
    if not os.path.exists(cegao_pipei_path):
        os.makedirs(cegao_pipei_path)
    img_pipei_extra_path = os.path.join(os.path.dirname(img_path), 'extra_match_CS')
    if os.path.exists(img_pipei_extra_path):
        shutil.rmtree(img_pipei_extra_path)
    if not os.path.exists(img_pipei_extra_path):
        os.makedirs(img_pipei_extra_path)
    img_name_list = os.listdir(img_path)
    cegao_name_list = os.listdir(cegao_path)
    if img_sign != 'Sentinel2':
        for cegao_name in cegao_name_list:
            count = 0
            for img_name in img_name_list:
                date_residual = date2num(parse(str(img_name[12:20]))) - date2num(parse(str(cegao_name[19:27])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[12:20] + '.tif'))
                        print('Redundant image data')
                    else:
                        shutil.copy(os.path.join(cegao_path, cegao_name), os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[12:20] + '.tif'))
                        print(img_name[12:20], cegao_name[19:27])
                        img_name_list.remove(img_name)
    else:
        for cegao_name in cegao_name_list:
            count = 0
            for img_name in img_name_list:
                date_residual = date2num(parse(str(img_name[:8]))) - date2num(parse(str(cegao_name[19:27])))
                if abs(date_residual) < 7:
                    count += 1
                    if count > 1:
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_extra_path, img_name[:8] + '.tif'))
                        print('Redundant image data')
                    else:
                        shutil.copy(os.path.join(cegao_path, cegao_name), os.path.join(cegao_pipei_path, cegao_name))
                        shutil.copy(os.path.join(img_path, img_name),
                                    os.path.join(img_pipei_path, img_name[:8] + '.tif'))
                        print(cegao_name[19:27], img_name[:8])
                        img_name_list.remove(img_name)
    print('Data filtering is complete!')


def all_filter(img_path, cegao_path):
    cegao_name_Sign = os.listdir(cegao_path)[0][0:2]
    print('Screening images and altimetry data...')
    if cegao_name_Sign == 'CS':
        CryoSat2_filter(img_path, cegao_path)
    elif cegao_name_Sign == 'AT':
        ICESat2_filter(img_path, cegao_path)
    elif cegao_name_Sign == 'S3':
        Sentinel3_filter(img_path, cegao_path)
    else:
        print(cegao_name_Sign)


if __name__ == '__main__':
    img_path = 'J:/Remote_Sensing_Image/Dabuxun/Dabuxun_Sentinel2/data'
    cegao_path = 'J:/Satellite_Altimeter_Data/Dabuxun/Sentinel3/data'
    all_filter(img_path, cegao_path)
