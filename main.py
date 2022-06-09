# Author: Zhang Chuanhui
# Date: December 07, 2021

from main_shaixuan_img_alt import all_filter
from main_get_shp_area import all_area_shp
from main_get_lake_level import all_get_lake_level


def main_all(img_path, alt_path):
    all_filter(img_path, alt_path)
    all_area_shp(img_path, alt_path)
    all_get_lake_level(img_path, alt_path)


# img: 1, 2, 3
img_name_list = ['Landsat7', 'Landsat8', 'Sentinel2']
# alt: 1, 2, 3
alt_name_list = ['CryoSat2', 'ICESat2', 'Sentinel3']

# 11,12,13,21,22,23,31,32,33
lake_name = ''
img_name = ''
alt_name = ''

# file path
img_path = 'J:/Remote_Sensing_Image/' + lake_name + '/' + lake_name + '_' + img_name + '/data'
# print(img_path)
alt_path = 'J:/Satellite_Altimeter_Data/' + lake_name + '/' + alt_name + '/data'

main_all(img_path, alt_path)
