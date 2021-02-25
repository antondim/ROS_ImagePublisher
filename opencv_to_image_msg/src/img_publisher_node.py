#!/usr/bin/env python

import sys
import os
import cv2
import numpy as np
import math

from cv_bridge import CvBridge, CvBridgeError
import rospy
import rospkg
import std_msgs.msg
from sensor_msgs.msg import Image

IMAGES_DIR = '/path/to/img' #change this
# DEPTH_TIMESTAMP_FILE = "path/to/timestampsdepth.txt"
# COLOR_TIMESTAMP_FILE = "/path/to/timestampscolor.txt"

def read_images(dir):
    '''Function that parses rgb and depth (8bit-16bit) images extracted 
       from frame_extractor.py of pyOniExtractor '''
    color_images_filenames = []
    depth_images_filenames = []
    color_images = []
    depth_images = []
    
    for filename in os.listdir(dir):
        if 'color' in filename:
            color_images_filenames.append(filename)
        elif '16bit' in filename:
            depth_images_filenames.append(filename)

    color_images_filenames = sorted(color_images_filenames, key=lambda x: int(x.split("_")[0]))
    depth_images_filenames = sorted(depth_images_filenames, key=lambda x: int(x.split("_")[0]))

    color_images = [cv2.imread(os.path.join(dir, filename)) for filename in color_images_filenames]
    depth_images = [cv2.imread(os.path.join(dir, filename),-1) for filename in depth_images_filenames]
    
    return (color_images, depth_images)


def get_timestamps(txt_file):
    '''Function that parses timestamps from files extracted from frame_extractor.py of pyOniExtractor '''
    with open(txt_file) as f:
        timestamps = f.readlines()

    for (index, stamp) in enumerate(timestamps):
        timestamps[timestamps.index(stamp)] = stamp[stamp.find(';')+1:stamp.find('/')-1]

    return timestamps


def image_publisher(color_imgs, depth_imgs):
    '''Function that parses timestamps from files extracted from frame_extractor.py of pyOniExtractor '''

    tmp_rgb_array = np.zeros(0)
    tmp_depth_array = np.zeros(0)
    bridge = CvBridge()
    rate = rospy.Rate(10) #publish rate
    
    rgb_publisher = rospy.Publisher('/camera/rgb/image_raw', Image, queue_size=5)
    depth_publisher = rospy.Publisher('/camera/depth/image_raw', Image, queue_size=5)
    
    print('Started publishing....')

    for (color_img, depth_img) in zip(color_imgs, depth_imgs):
        
        # Testing for non-equal sequences of imgs
        if np.array_equal(tmp_rgb_array, color_img):
            print('Rgb img error... Two pictures seem to be the same...EXITING')
            exit(1)
        elif np.array_equal(tmp_depth_array, depth_img):
            print('Depth img error... Two pictures seem to be the same...EXITING')
            exit(1)

        rgb_img_msg = bridge.cv2_to_imgmsg(color_img[:, :], encoding='bgr8')
        rgb_img_msg.header.stamp = rospy.Time.now() # using time stamp as if data are being collected now
        rgb_img_msg.header.frame_id = "/camera"
        
        # # Visualize what is being published
        # cv2.imshow('image',depth_img)
        # cv2.waitKey(1)
        
        depth_img_msg = bridge.cv2_to_imgmsg(depth_img[:, :], encoding='passthrough')
        depth_img_msg.header.stamp = rospy.Time.now() # using time stamp as if data are being collected now
        depth_img_msg.header.frame_id = "/camera"

        #testing parameters
        tmp_rgb_array = color_img
        tmp_depth_array = depth_img
        
        if rospy.is_shutdown():
            exit(1)

        rgb_publisher.publish(rgb_img_msg)
        depth_publisher.publish(depth_img_msg)
        rate.sleep()


if __name__ == "__main__":

    color_images = []
    depth_images = []

    rospy.init_node("images_publish_node")
    (color_images, depth_images) = read_images(IMAGES_DIR)
    image_publisher(color_images, depth_images)
