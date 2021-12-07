# This program is used to obtain lake water levels.
# It can obtain elevation points from multi-source satellite altimetry data (CryoSat2,ICESat2,Sentinel3),
# then use lake boundary filtering to obtain lake elevation points,
# and finally eliminate abnormal points to calculate high-precision lake water levels.

import netCDF4 as nc
import numpy as np
import pandas as pd
import os
import shutil
import h5py
from filter import Border_filter_match
from Get_EEP import get_EEP


def read_CryoSat2(file_path, location):
    result_file_path = os.path.abspath(os.path.dirname(file_path)) + '/match_CS_result'
    if os.path.exists(os.path.join(result_file_path)):
        shutil.rmtree(os.path.join(result_file_path))
    if not os.path.exists(os.path.join(result_file_path)):
        os.makedirs(os.path.join(result_file_path))
    file_name = os.listdir(file_path)
    # Traverse the NC file
    for i in file_name:
        print(i[19:27])
        data = nc.Dataset(os.path.join(file_path, i))
        # print(data.variables.keys())
        lon_poca_20_ku = data.variables['lon_poca_20_ku']
        lat_poca_20_ku = data.variables['lat_poca_20_ku']
        height_1_20_ku = data.variables['height_1_20_ku']
        # 建立list
        list_mean_sea_surf_sea_ice_20_ku = []
        list_longitude = []
        list_latitude = []
        # Traverse to obtain the data of the study area
        for k in range(len(lon_poca_20_ku)):
            if location[3] > lon_poca_20_ku[k] > location[2] and location[0] > lat_poca_20_ku[k] > location[1]:
                list_longitude.append(lon_poca_20_ku[k])
                list_latitude.append(lat_poca_20_ku[k])
                list_mean_sea_surf_sea_ice_20_ku.append(height_1_20_ku[k])

        array_con1 = np.concatenate((np.array(list_longitude).reshape((-1, 1)),
                                     np.array(list_latitude).reshape((-1, 1)),
                                     np.array(list_mean_sea_surf_sea_ice_20_ku).reshape((-1, 1))), axis=1)
        data1 = pd.DataFrame(array_con1)
        data1.columns = ['x', 'y', 'WGS-84']
        writer = pd.ExcelWriter(os.path.join(result_file_path, i) + '.xlsx')
        data1.to_excel(writer, header=True, index=False)
        writer.save()
    print('all_done')


def read_ICESat2(file_path, location):
    result_file_path = os.path.abspath(os.path.dirname(file_path)) + '/match_ICE2_result'
    if os.path.exists(os.path.join(result_file_path)):
        shutil.rmtree(os.path.join(result_file_path))
    if not os.path.exists(os.path.join(result_file_path)):
        os.makedirs(os.path.join(result_file_path))
    file_name = os.listdir(file_path)
    sub_file_list = ['gt1l/', 'gt1r/', 'gt2l/', 'gt2r/', 'gt3l/', 'gt3r/']
    OT = 1
    # Traverse hdf5 files
    for i in file_name:
        print(i[6:14])
        data = h5py.File(os.path.join(file_path, i))
        # Traverse 6 groups of laser data
        gt_avg_list_cor_ht_water_surf = []
        gt_avg_cor_list_ht_ortho = []
        for j in sub_file_list:
            # Get the elevation value in the WGS-84 coordinate system
            ht_water_surf = data.get(os.path.join(j, 'ht_water_surf'))[:]
            latitude = data.get(os.path.join(j, 'sseg_mean_lat'))[:]  # Get latitude
            longitude = data.get(os.path.join(j, 'sseg_mean_lon'))[:]  # Get longitude
            list_ht_water_surf = []
            list_cor_ht_water_surf = []
            list_cor_ht_ortho = []
            list_cor_longitude = []
            list_cor_latitude = []
            list_longitude = []
            list_latitude = []
            # Traverse to obtain the data of the study area
            # print(len(latitude))
            for k in range(len(latitude)):
                if location[3] > longitude[k] > location[2] and location[0] > latitude[k] > location[1]:
                    list_longitude.append(longitude[k])
                    list_latitude.append(latitude[k])
                    list_ht_water_surf.append(ht_water_surf[k])
            # Eliminate data beyond the median of 2m
            MD_list_ht_water_surf = np.nanmedian(list_ht_water_surf)
            # MD_list_ht_ortho = np.nanmedian(list_ht_ortho)
            for m in range(len(list_ht_water_surf)):
                if MD_list_ht_water_surf - OT < list_ht_water_surf[m] < MD_list_ht_water_surf + OT:
                    list_cor_ht_water_surf.append(list_ht_water_surf[m])
                    # list_cor_ht_ortho.append(list_ht_ortho[m])
                    list_cor_longitude.append(list_longitude[m])
                    list_cor_latitude.append(list_latitude[m])
            avg_list_cor_ht_water_surf = np.nanmean(list_cor_ht_water_surf)
            gt_avg_list_cor_ht_water_surf.append(avg_list_cor_ht_water_surf)
            avg_cor_list_ht_ortho = np.nanmean(list_cor_ht_ortho)
            gt_avg_cor_list_ht_ortho.append(avg_cor_list_ht_ortho)
            array_con1 = np.concatenate((np.array(list_cor_longitude).reshape(-1, 1),
                                         np.array(list_cor_latitude).reshape(-1, 1),
                                         np.array(list_cor_ht_water_surf).reshape(-1, 1)), axis=1)
            data1 = pd.DataFrame(array_con1)
            data1.columns = ['x', 'y', 'WGS-84']
            writer = pd.ExcelWriter(os.path.join(os.path.join(result_file_path, i) + '.xlsx'))
            data1.to_excel(writer, header=True, index=False)
            writer.save()
    print('all_done')


def read_sentinel3(file_path, location):
    result_file_path = os.path.abspath(os.path.dirname(file_path)) + '/match_ST3_result'
    if os.path.exists(os.path.join(result_file_path)):
        shutil.rmtree(os.path.join(result_file_path))
    if not os.path.exists(os.path.join(result_file_path)):
        os.makedirs(os.path.join(result_file_path))
    file_name = os.listdir(file_path)
    for i in file_name:
        print(i[16:24])
        data = nc.Dataset(os.path.join(file_path, i, 'standard_measurement.nc'))  # 读取对应文件
        time_20_ku = data.variables['time_20_ku']
        mean_time = np.nanmean(time_20_ku)
        # Get the corrected latitude and longitude
        lat_cor_20_ku = data.variables['lat_cor_20_ku']
        lon_cor_20_ku = data.variables['lon_cor_20_ku']
        sea_ice_sea_surf_20_ku = data.variables['sea_ice_sea_surf_20_ku']
        list_mean_sea_surf_sea_ice_20_ku = []
        list_longitude = []
        list_latitude = []
        for k in range(len(lat_cor_20_ku)):
            if location[3] > lon_cor_20_ku[k] > location[2] and location[0] > lat_cor_20_ku[k] > location[1]:
                list_longitude.append(lon_cor_20_ku[k])
                list_latitude.append(lat_cor_20_ku[k])
                list_mean_sea_surf_sea_ice_20_ku.append(sea_ice_sea_surf_20_ku[k])
        array_con1 = np.concatenate((np.array(list_longitude).reshape((-1, 1)),
                                     np.array(list_latitude).reshape((-1, 1)),
                                     np.array(list_mean_sea_surf_sea_ice_20_ku).reshape((-1, 1))), axis=1)
        data1 = pd.DataFrame(array_con1)
        data1.columns = ['x', 'y', 'WGS-84']
        writer = pd.ExcelWriter(os.path.join(result_file_path, i[4:]) + '.xlsx')
        # print(os.path.join(result_file_path, i) + '.xlsx')
        data1.to_excel(writer, header=True, index=False)
        writer.save()
    print('all_done')


def all_get_lake_level(alt_file, img_file):
    alt_sign = os.path.basename(os.path.dirname(alt_file))
    img_sign = os.path.basename(os.path.dirname(img_file)).split('_')[1]
    location = np.loadtxt(os.path.join('/'.join(img_file.split('/')[0: -2]), 'Location.txt'))
    point_path_CS = os.path.join(os.path.dirname(alt_file), img_sign, 'match_CS')
    point_path_ICE = os.path.join(os.path.dirname(alt_file), img_sign, 'match_ICE2')
    point_path_Sentinel = os.path.join(os.path.dirname(alt_file), img_sign, 'match_ST3')
    print('Extracting lake water level...')
    if alt_sign == 'CryoSat2':
        print(img_sign,':','CryoSat2')
        read_CryoSat2(point_path_CS, location)
        Border_filter_match(point_path_CS + '_result', os.path.dirname(img_file) + '/shapefile_CS', location)
        get_EEP(os.path.dirname(point_path_CS) + '/Border_filter_CS')
    elif alt_sign == 'ICESat2':
        print(img_sign, ':', 'ICESat2')
        read_ICESat2(point_path_ICE, location)
        Border_filter_match(point_path_ICE + '_result', os.path.dirname(img_file) + '/shapefile_ICE2', location)
        get_EEP(os.path.dirname(point_path_CS) + '/Border_filter_ICE2')
    elif alt_sign == 'Sentinel3':
        print(img_sign, ':', 'Sentinel3')
        read_sentinel3(point_path_Sentinel, location)
        Border_filter_match(point_path_Sentinel + '_result', os.path.dirname(img_file) + '/shapefile_ST3', location)
        get_EEP(os.path.dirname(point_path_CS) + '/Border_filter_ST3')


if __name__ == '__main__':
    all_get_lake_level('J:/Satellite_Altimeter_Data/Dachaidan/CryoSat2/data',
                       'J:/Remote_Sensing_Image/Dachaidan/Dachaidan_Sentinel2/data')
