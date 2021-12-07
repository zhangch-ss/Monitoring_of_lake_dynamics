import numpy as np
from read_write_img import read_img, write_img
import cv2
import os
from skimage import measure, color
import pandas as pd
from numba import jit


def fill(t):
    for k in range(t.shape[1]):
        temp_col = t[:, k]
        nan_num = np.count_nonzero(temp_col != temp_col)

        if nan_num != 0:
            temp_not_nan_col = temp_col[temp_col == temp_col]

            temp_col[np.isnan(temp_col)] = temp_not_nan_col.mean()
    return t


def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range


def quyun(image_slave):
    image_master = np.zeros((image_slave.shape[0], image_slave.shape[1]))
    for i in range(image_master.shape[0] - 1):
        for j in range(image_master.shape[1] - 1):
            if np.isnan(image_slave[i][j]):
                # print(i, j)
                # print(image_slave[i-1:i+2, j-1:j+2])
                # pix_change = image_slave[i-half_window:i+(half_window+1), j-half_window:j+(half_window+1)] - image_master[i-half_window:i+(half_window+1), j-half_window:j+(half_window+1)]
                # average_change = np.nanmean(pix_change)
                # print(pix_change)
                pix_change1 = image_slave[i][j + 1] - image_master[i][j + 1]
                pix_change2 = image_slave[i][j - 1] - image_master[i][j - 1]
                pix_change3 = image_slave[i + 1][j + 1] - image_master[i + 1][j + 1]
                pix_change4 = image_slave[i + 1][j - 1] - image_master[i + 1][j - 1]
                pix_change5 = image_slave[i + 1][j] - image_master[i + 1][j]
                pix_change6 = image_slave[i - 1][j + 1] - image_master[i - 1][j + 1]
                pix_change7 = image_slave[i - 1][j - 1] - image_master[i - 1][j - 1]
                pix_change8 = image_slave[i - 1][j] - image_master[i - 1][j]
                average_change = np.nanmean([pix_change1, pix_change2, pix_change3, pix_change4, pix_change5, pix_change6, pix_change7, pix_change8])
                # print(average_change)
                image_slave[i][j] = image_master[i][j] + average_change
                # print(image_slave[i][j])
    image_slave = fill(image_slave)
    return image_slave


def ostu(data_array):
    data_array_255 = normalization(data_array) * 255
    img = data_array_255.astype(np.uint8)
    maxval = 255
    otsuThe = 0
    otsuThe, dst_Otsu = cv2.threshold(img, otsuThe, maxval, cv2.THRESH_OTSU)
    # water_area = np.count_nonzero(dst_Otsu) * 30 * 30 / 1000000
    best_thresold_NDWI = ((otsuThe / 255) * (data_array.max() - data_array.min())) + data_array.min()
    temp1 = measure.label(dst_Otsu, connectivity=2)
    num_area = temp1.max()
    num_list = []
    for i in range(1, num_area + 1):
        # 逐个建立缓冲区
        temp2 = (temp1 == i)
        num_pixel_before = sum(sum(temp2))
        num_list.append(num_pixel_before)
    # max_area_pix = np.nanmax(num_list)
    # lake_area = max_area_pix * 30 * 30 / 1000000
    # 0是背景
    dst = color.label2rgb(temp1, bg_label=0)
    dst = ((dst - dst.min()) / (dst.max() - dst.min())) * 255
    return dst_Otsu, best_thresold_NDWI, dst


# kernel_size set (n,n) default
def gaussian_2d_kernel(kernel_size=3, sigma=0):
    kernel = np.zeros([kernel_size, kernel_size])
    center = kernel_size // 2

    if sigma == 0:
        sigma = ((kernel_size - 1) * 0.5 - 1) * 0.3 + 0.8

    s = 2 * (sigma ** 2)
    sum_val = 0
    for i in range(0, kernel_size):
        for j in range(0, kernel_size):
            x = i - center
            y = j - center
            kernel[i, j] = np.exp(-(x ** 2 + y ** 2) / s)
            sum_val += kernel[i, j]
    sum_val = 1 / sum_val
    return kernel * sum_val


def lvbo(quyun_image_slave):
    k = gaussian_2d_kernel()
    for i_ in range(1, quyun_image_slave.shape[0]-1):
        for j_ in range(1, quyun_image_slave.shape[1]-1):
            quyun_image_slave[i_][j_] = np.sum(k * quyun_image_slave[i_ - 1:i_ + 2, j_ - 1:j_ + 2])
    return quyun_image_slave


