#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np


def object_pos(lower_color, upper_color, stream):
	AllColorsInRange = cv2.inRange(stream, lower_color, upper_color)
	Blurred = cv2.GaussianBlur(AllColorsInRange, (121, 121), 0)
	Thresh = cv2.threshold(Blurred, 37, 255, cv2.THRESH_BINARY)[1]
	Object = cv2.dilate(Thresh, (121, 121), iterations=1)
	(_, cnts, _) = cv2.findContours(Object.copy(), cv2.RETR_EXTERNAL,
									cv2.CHAIN_APPROX_SIMPLE)
	if cnts == []:
		return (None, None, None)
	else:
		c = max(cnts, key=cv2.contourArea)
		marker = cv2.minAreaRect(c)
		box = np.int0(cv2.boxPoints(marker))
		M = cv2.moments(c)
		if int(M['m00']) == 0:
			return (None, None, None)
		else:
			cX = int(M['m10'] / M['m00'])
			cY = int(M['m01'] / M['m00'])
		return (cX, cY, cnts)
