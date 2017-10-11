#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def screen_depth(RESOLUTION, FOV):
    SCREEN_DEPTH = RESOLUTION / 2 / math.tan(math.radians(FOV / 2))
    return SCREEN_DEPTH
    
def pixels_to_camera_angle(SCREEN_DEPTH, COORDINATE):
    CAMERA_ANGLE = math.degrees(math.atan(COORDINATE / SCREEN_DEPTH))
    return CAMERA_ANGLE

def topview_camera_angles_to_internal_angles(CAMERA_A_ANGLE, CAMERA_B_ANGLE):
    THETA_A = 90.0 - CAMERA_A_ANGLE
    THETA_B = 90.0 + CAMERA_B_ANGLE
    return (THETA_A, THETA_B)

def topview_range_from_cams(LAB, THETA_A, THETA_B):
    LA = LAB * math.sin(math.radians(THETA_B)) / math.sin(math.radians(180 - THETA_A - THETA_B))
    LB = LAB * math.sin(math.radians(THETA_A)) / math.sin(math.radians(180 - THETA_A - THETA_B))
    return (LA, LB)

def x_coord(THETA_A, THETA_B, LA, LB, LAB):
    XA = LA * math.sin(math.radians(90 - THETA_A))
    XB = LB * math.sin(math.radians(90 - THETA_B))
    X1 = XA - LAB/2
    X2 = LAB/2 - XB
    X = (X1 + X2) / 2
    return X

def y_coord(THETA_A, THETA_B, LA, LB):
    Y1 = LA * math.cos(math.radians(90 - THETA_A))
    Y2 = LB * math.cos(math.radians(90 - THETA_B))
    Y = (Y1 + Y2) / 2
    return Y

def z_coord(CAMERA_A_ANGLE_Y, Y1, CAMERA_B_ANGLE_Y, Y2):
    Z1 = Y1 * math.tan(math.radians(CAMERA_A_ANGLE_Y))
    Z2 = Y2 * math.tan(math.radians(CAMERA_B_ANGLE_Y))
    Z = (Z1 + Z2) / 2
    return Z

def ceiling(x):
    n = math.ceil(x*100)/100
    return n
