# Obtain effective elevation points on the lake surface
# For details, please refer to the article https://doi.org/10.3390/rs13163221
import numpy as np
import pandas as pd
import os


# Obtain effective elevation points on the lake surface
def get_EEP(file_path):
    sign = str(os.path.basename(file_path).split('_')[-1])
    print(sign)
    result = []
    result_list = []
    file_name = os.listdir(file_path)
    date_list = []
    for file in file_name:
        print('Date', file)
        date_list.append(file)
        data = pd.read_excel(os.path.join(file_path, file, 'Elevation.xlsx'), header=None)
        data_i_ary = np.array(data)
        data_i_ary = data_i_ary[~np.isnan(data_i_ary)]
        list_point = []
        len_point1 = 0
        for j in data_i_ary:
            # print(j)
            point = []
            for k in data_i_ary:
                if j - 0.3 < k < j + 0.3:
                    point.append(k)
            len_point = len(point)
            if len_point > len_point1:
                len_point1 = len_point
                list_point = point
            elif len_point == len_point1:
                if np.std(point) < np.std(list_point):
                    len_point1 = len_point
                    list_point = point
        print('quantity:', len(list_point))

        if len(data_i_ary) > 0:
            if len(list_point) / len(data_i_ary) >= 4 / 5:
                print('Excellent')
            elif 3 / 5 <= len(list_point) / len(data_i_ary) < 4 / 5:
                print('Good')
            elif 2 / 5 >= len(list_point) / len(data_i_ary) < 3 / 5:
                print('Medium')
            elif len(list_point) / len(data_i_ary) < 2 / 5 or len(list_point)<6:
                print('Bad ')
        else:
            print('No data')
        print('average value', np.mean(list_point))
        result.append(np.mean(list_point))
        result_list.append(list_point)
    dataframe1 = pd.DataFrame(result)
    dataframe1.insert(0, 'Date', date_list)
    # lake water level of the lake after excluding abnormal points
    dataframe1.to_excel(os.path.join(file_path, os.path.abspath(os.path.dirname(file_path)), 'lake_level_' + sign +
                                     '.xlsx'), header=False, index=False)
    dataframe = pd.DataFrame(result_list)
    # Lake elevation point set after excluding abnormal points
    dataframe.to_excel(os.path.join(file_path, os.path.abspath(os.path.dirname(file_path)), 'lake_level_' + sign +
                                    'list.xlsx'), header=False,
                       index=False)


if __name__ == '__main__':
    # The filtered lake elevation point (Excel) storage path
    file_path = ''
    get_EEP(file_path)


