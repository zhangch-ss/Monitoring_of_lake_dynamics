# This program uses lake shp data to filter satellite altimetry data to obtain lake elevation points

import shapefile
import shapely.geometry as geometry
from shapely import speedups
import pandas as pd
from mpl_toolkits.basemap import Basemap
import numpy as np
# import pylab as plt
import matplotlib.pyplot as plt
from osgeo import ogr
import os


# Use shapefile to filter lake elevation points
def filter(shape_file, file_path, fig_save_path, location):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shape_file, 0)
    layer = dataSource.GetLayer()
    count = layer.GetFeatureCount()
    area_list = []
    for i in range(count):
        feature = layer[i]
        geom = feature.GetGeometryRef()  # 对每一个feature，获取几何信息
        area = geom.GetArea()  # 计算面积
        area_list.append(area)
    if len(area_list) == 0:
        in_shape_points = []
        gaocheng_list = []
    else:
        index = area_list.index(max(area_list))
        sz_shp = shapefile.Reader(shape_file)
        # print(sz_shp)
        all_shapes = sz_shp.shapes()
        shp_ = all_shapes[index]
        m = Basemap(llcrnrlon=location[2], llcrnrlat=location[1], urcrnrlon=location[3], urcrnrlat=location[0],
                    resolution='i', projection='tmerc', lat_0=(location[1] + location[0]) / 2,
                    lon_0=(location[2] + location[3]) / 2)
        data = pd.read_excel(file_path)
        linear_lon = data.iloc[:, 0]
        linear_lat = data.iloc[:, 1]
        gaocheng = data.iloc[:, 2]
        m.readshapefile(shape_file[: -4], 'lake', color='red')
        m.scatter(np.array(linear_lon), np.array(linear_lat), latlon=True, s=10, marker="o",
                  label='Alt_point')
        plt.savefig(fig_save_path + '/Alt_point.jpg', dpi=300)
        plt.close()

        flat_points = np.column_stack((linear_lon, linear_lat))
        in_shape_points = []
        gaocheng_list = []
        # Disable the acceleration module of Shapefly. Otherwise,
        # there will be an error below the operation（GEOSGeom_createLinearRing_r returned a NULL pointer）
        # unknown reason（It may be a conflict between shapefly and osgeo modules），
        # Refer to the website below to solve it. 2021.11.19
        # reference：https://stackoverflow.com/questions/62075847/using-qgis-and-shaply-error-geosgeom-createlinearring-r-returned-a-null-pointer
        speedups.disable()
        for i in range(len(flat_points)):
            # if geometry.Point(flat_points[i]).within(geometry.asPolygon(shp_point)):
            if geometry.Point(flat_points[i]).within(geometry.shape(shp_)):
                # print(flat_points[i])
                # print('The point is in SZ', flat_points[i])
                in_shape_points.append(flat_points[i])
                gaocheng_list.append(gaocheng[i])
        selected_lon = [elem[0] for elem in in_shape_points]
        selected_lat = [elem[1] for elem in in_shape_points]
        # print(selected_lon)
        m.readshapefile(shape_file[: -4], 'lake', color='red')
        m.scatter(selected_lon, selected_lat, latlon=True, s=10, marker="o",
                  label='EP_LS')
        plt.legend(loc=2)
        plt.savefig(fig_save_path + '/EP_LS.jpg', dpi=300, pad_inches=0)
        plt.close()
    return in_shape_points, gaocheng_list


def Border_filter_match(file_path, shp_path, location):
    global file_name_
    file_name_list = os.listdir(file_path)
    shp_name_list = os.listdir(shp_path)
    sign = os.path.basename(shp_path)[10:]
    print(sign)
    # point_file_path = os.path.join(file_path, subfile_name, 'result2.xlsx')
    # print(point_file_path)
    # fig_save_path = os.path.join(file_path, subfile_name)
    # point = pd.read_excel(point_file_path)
    # print(point.iloc[:, 0])
    gaocheng_list_list = []
    for file_name, shp_name in zip(file_name_list, shp_name_list):
        if file_name[:2] == 'AT':
            file_name_ = file_name[6:14]
        elif file_name[:2] == 'CS':
            file_name_ = file_name[19:27]
        elif file_name[:2] == 'SR':
            file_name_ = file_name[12:20]
        print('Image:',shp_name, 'Altimetry:',file_name_)
        point_file_path = os.path.join(file_path, file_name)
        # print('point_file_path', point_file_path)
        fig_save_path = os.path.join(os.path.abspath(os.path.dirname(file_path)), 'Border_filter_' + sign, file_name_)
        if not os.path.exists(fig_save_path):
            os.makedirs(fig_save_path)
        in_shape_points, gaocheng_list = filter(os.path.join(shp_path, shp_name, shp_name + '.shp'), point_file_path,
                                                  fig_save_path, location)
        # print(os.path.join(shp_path, shp_name, shp_name + '.shp'))
        # print('2')
        print('EP_LS:', len(in_shape_points))
        dataframe1 = pd.DataFrame(in_shape_points)
        dataframe1.to_excel(os.path.join(fig_save_path, 'Location.xls'), header=False, index=False)
        gaocheng_list_list.append(gaocheng_list)
        dataframe = pd.DataFrame(gaocheng_list)
        dataframe.to_excel(os.path.join(fig_save_path, 'Elevation.xls'), header=False, index=False)
    dataframe3 = pd.DataFrame(gaocheng_list_list)
    dataframe3.to_csv(os.path.join(os.path.abspath(os.path.dirname(file_path)), 'Border_filter_' + sign + '.csv'),
                        header=False, index=False)

if __name__ == '__main__':
    # Satellite altimetry data results(Excel)
    file_path = ''
    # image shp
    shp_path = ''
    aa = os.path.abspath(os.path.dirname(file_path))
    print(aa)
    # Border_filter_match()
