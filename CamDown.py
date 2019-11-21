#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'used for manage and generate cam data with set ground-image.
it is a virtual camera

By xiaobo
Contact linxiaobo110@gmail.com
Created on  十一月 21 20:29 2019
"""

# Copyright (C)
#
# This file is part of quadrotorfly
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np
import CommonFunctions as Cf
import cv2

"""
********************************************************************************************************
**-------------------------------------------------------------------------------------------------------
**  Compiler   : python 3.6
**  Module Name: CamDown
**  Module Date: 2019/11/21
**  Module Auth: xiaobo
**  Version    : V0.1
**  Description: a virtual camera looking down
**-------------------------------------------------------------------------------------------------------
**  Reversion  :
**  Modified By:
**  Date       :
**  Content    :
**  Notes      :
********************************************************************************************************/
"""


class CamDown(object):
    def __init__(self, img_horizon=400, img_vertical=400, img_depth=3,
                 sensor_horizon=4., sensor_vertical=4., cam_focal=2.36,
                 ground_img_path='./Data/groundImgWood.jpg'):
        """
        ****************** horizon ****************
        *
        v
        e
        r
        t
        i
        c
        a
        l
        ********************************************
        :param img_horizon: the num of vertical pixes of the image which is generated by sensor
        :param img_vertical: the num of horizon pixes of the image which is generated by sensor
        :param img_depth: the num of chanel the image, i.e. rgb is 3
        :param sensor_horizon:   mm,     the height of the active area of the sensor
        :param sensor_vertical:  mm,     the width of the active area of the sensor
        :param cam_focal:       mm,     the focal of the lens of the camera
        """
        self.imgHorizon = img_horizon
        self.imgVertical = img_vertical
        self.imgDepth = img_depth
        self.skx = sensor_horizon / img_horizon   # skx is sensor_k_x
        self.sky = sensor_vertical / img_vertical     # skx is sensor_k_y
        self.sx0 = sensor_horizon * 0.5
        self.sy0 = sensor_vertical * 0.5
        self.camFocal = cam_focal
        self.axCamImgArr = np.zeros([self.imgVertical * self.imgHorizon, 3])
        self.pixCamImg = np.zeros([self.imgVertical, self.imgHorizon, self.imgDepth], dtype=np.uint8)
        self.groundImgPath = ground_img_path
        self.groundImg = None

        # init the array
        for i in range(self.imgVertical):
            for j in range(self.imgHorizon):
                self.axCamImgArr[i * self.imgHorizon + j, :] = [i, j, 1]

    def load_ground_img(self):
        if self.groundImg is not None:
            del self.groundImg
        else:
            self.groundImg = cv2.imread(self.groundImgPath)

    def get_img_by_state(self, pos, att):
        m_img2sensor = np.array([[self.skx, 0, self.sx0],
                                 [0, -self.sky, -self.sy0],
                                 [0, 0, 1]])
        m_sensor2cam = np.array([[pos[2] / self.camFocal, 0, 0],
                                 [0, pos[2] / self.camFocal, 0],
                                 [0, 0, 1]])
        m_cam2world = Cf.get_rotation_matrix(att)
        m_cam2world[0:2, 2] = pos[0:2]
        m_cam2world[2, :] = np.array([0, 0, 1])
        m_trans = m_cam2world.dot(m_sensor2cam.dot(m_img2sensor))
        ax_real = m_trans.dot(self.axCamImgArr.transpose()).transpose()
        for i in range(self.imgVertical):
            for j in range(self.imgHorizon):
                self.pixCamImg[i, j, :] = self.groundImg[int(ax_real[i * self.imgHorizon + j, 0]),
                                          int(ax_real[i * self.imgHorizon + j, 1] + 10000), :]
        return self.pixCamImg


if __name__ == '__main__':
    " used for testing this module"
    testFlag = 1

    if testFlag == 1:
        cam1 = CamDown()
        print('init completed!')
        cam1.load_ground_img()
        print('Load img completed!')
        pos_0 = np.array([4251.97508977, -5843.00458236,   227.35483937])
        att_0 = np.array([-0.13647458, -0.1990263 ,  0.27836947])
        img1 = cam1.get_img_by_state(pos_0, att_0)
        import matplotlib.pyplot as plt
        plt.imshow(cam1.pixCamImg / 255)
        cv2.imwrite('Data/test.jpg', img1)

