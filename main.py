import gi
import time
import sys
import signal
import os
import json
import cv2
import numpy as np
import Coordinate_Calculations
import colorDetector

# Stuff needed to get it to work with vridge/riftcat.
import zmq, json, time, sys, struct
from collections import namedtuple
from construct import Int32ub, Int32ul, Float32l, Struct, Const, Padded, Array

signal.signal(signal.SIGINT, signal.SIG_DFL)

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

builder = Gtk.Builder()
builder.add_from_file("3dpos.glade")

configFilesOpened = False

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);

try:
	configFile = open("./config/config.json", "r+")
	config = json.loads(configFile.read())
	configFilesOpened = True
except:
	os.system('mkdir config')
	os.system('rm -rf ./config/config.json')
	os.system('touch ./config/config.json')
	configFile = open("./config/config.json", "r+")

if configFilesOpened == True:
	greyscale = config['Greyscale']
	units = config['Show_Units']
	Hue_Min = float(config['Hue_Min'])
	Saturation_Min = float(config['Saturation_Min'])
	Value_Min = float(config['Value_Min'])
	Hue_Max = float(config['Hue_Max'])
	Saturation_Max = float(config['Saturation_Max'])
	Value_Max = float(config['Value_Max'])
	alpha = float(config['Alpha'])
	Same_Cam = config['Are_the_cameras_the_same']
	Cam_H_FOV = float(config['Camera_FOV_Horizontal'])
	Cam_V_FOV = float(config['Camera_FOV_Vertical'])
	Dis_Between_Cams = int(config['Dis_Between_Cams'])
	Color_Min = (Hue_Min, Saturation_Min, Value_Min)
	Color_Max = (Hue_Max, Saturation_Max, Value_Max)
else:
	greyscale = False
	units = True
	Hue_Min = 0
	Hue_Max = 360
	Saturation_Min = 0
	Saturation_Max = 255
	Value_Min = 0
	Value_Max = 255
	alpha=0.5
	Same_Cam = True
	Cam_H_FOV = 0
	Cam_V_FOV = 0
	Dis_Between_Cams = 0
	Color_Min = (Hue_Min, Saturation_Min, Value_Min)
	Color_Max = (Hue_Max, Saturation_Max, Value_Max)
	
NotFirstTimeHFOV = False
NotFirstTimeVFOV = False
NotFirstTimeDBC = False

class Handler:
	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)
		Save()
		configFile.close()
		print('[INFO]Exiting...')
		sys.exit(0)
 
	def activateGreyscale(self, *args):
		global greyscale
		greyscale = GreyscaleToggle.get_active()
	
	def activateUnits(self, *args):
		global units
		units = UnitToggle.get_active()
		
	def onHueMinValueChanged(self, *args):
		global Hue_Min
		Hue_Min = Hue_Min_Scale.get_value()
	
	def onHueMaxValueChanged(self, *args):
		global Hue_Max
		Hue_Max = Hue_Max_Scale.get_value()
		
	def onSaturationMinValueChanged(self, *args):
		global Saturation_Min
		Saturation_Min = Saturation_Min_Scale.get_value()
		
	def onSaturationMaxValueChanged(self, *args):
		global Saturation_Max
		Saturation_Max = Saturation_Max_Scale.get_value()

	def onValueMinValueChanged(self, *args):
		global Value_Min
		Value_Min = Value_Min_Scale.get_value()
		
	def onValueMaxValueChanged(self, *args):
		global Value_Max
		Value_Max = Value_Max_Scale.get_value()
		
	def onAlphaValueChanged(self, *args):
		global alpha
		alpha = alpha_Scale.get_value()
	
	def onDestroySettingsWindow(self, *args):
		window2.hide()
		return True
	
	def SettingsWindow(self, *args):
		window2.show()
		
	def on_Cam_Same_toggled(self, *args):
		global Same_Cam
		Same_Cam = CamSameToggle.get_active()
	
	def on_Cam_H_FOV_activate(self, *args):
		global Cam_H_FOV, NotFirstTimeHFOV
		if NotFirstTimeHFOV == True:
			try:
				Cam_H_FOV = float(Cam_H_FOV_Entry.get_text())
			except ValueError:
				Cam_H_FOV = 0
		else:
			pass
		
		NotFirstTimeHFOV = True
		
	def on_Cam_V_FOV_activate(self, *args):
		global Cam_V_FOV, NotFirstTimeVFOV
		if NotFirstTimeVFOV == True:
			try:
				Cam_V_FOV = float(Cam_V_FOV_Entry.get_text())
			except ValueError:
				Cam_V_FOV = 0
		else:
			pass
		
		NotFirstTimeVFOV = True
	
	def on_Dis_Between_Cams_activate(self, *args):
		global Dis_Between_Cams, NotFirstTimeDBC
		if NotFirstTimeDBC == True:
			try:
				Dis_Between_Cams = int(Dis_Between_Cams_Entry.get_text())
			except ValueError:
				Dis_Between_Cams = 0
		else:
			pass
		NotFirstTimeDBC = True
	
	def SaveSettings_clicked(self, *args):
		Save()


def Save():
	print("[INFO]Saving...")
	global configFile
	configFile.close()
	os.system('rm -rf ./config/config.json')
	os.system('touch ./config/config.json')
	configFile = open('./config/config.json', 'r+')
	configFile.write('{\n')
	configFile.write('	"Camera_FOV_Horizontal" : "' + str(Cam_H_FOV) + '",\n')
	configFile.write('	"Camera_FOV_Vertical" : "' + str(Cam_V_FOV) + '",\n')
	configFile.write('	"Dis_Between_Cams" : "' + str(Dis_Between_Cams) + '",\n')
	configFile.write('	"Are_the_cameras_the_same" : "' + str(Same_Cam) +'",\n')
	configFile.write('	"Hue_Min" : "' + str(Hue_Min) + '",\n')
	configFile.write('	"Hue_Max" : "' + str(Hue_Max) + '",\n')
	configFile.write('	"Saturation_Min" : "' + str(Saturation_Min) + '",\n')
	configFile.write('	"Saturation_Max" : "' + str(Saturation_Max) + '",\n')
	configFile.write('	"Value_Min" : "' + str(Value_Min) + '",\n')
	configFile.write('	"Value_Max" : "' + str(Value_Max) + '",\n')
	configFile.write('	"Alpha" : "' + str(alpha) + '",\n')
	configFile.write('	"Show_Units" : "' + str(units) + '",\n')
	configFile.write('	"Greyscale" : "' + str(greyscale) + '"\n')
	configFile.write('}')
	configFile.write('\n')
	configFile.flush()


window = builder.get_object("window1")
window2 = builder.get_object("window2")
image = builder.get_object("image")
UnitToggle = builder.get_object("ShowUnits")
GreyscaleToggle = builder.get_object("Greyscale")
CamSameToggle = builder.get_object("Cam_Same")
Hue_Min_Scale = builder.get_object("Hue_Min_Value")
Hue_Max_Scale = builder.get_object("Hue_Max_Value")
Saturation_Min_Scale = builder.get_object("Saturation_Min_Value")
Saturation_Max_Scale = builder.get_object("Saturation_Max_Value")
Value_Min_Scale = builder.get_object("Value_Min_Value")
Value_Max_Scale = builder.get_object("Value_Max_Value")
alpha_Scale = builder.get_object("Alpha_Scale")
Cam_H_FOV_Entry = builder.get_object("Cam_H_FOV")
Cam_V_FOV_Entry = builder.get_object("Cam_V_FOV")
Dis_Between_Cams_Entry = builder.get_object("Dis_Between_Cams")
window.show_all()
builder.connect_signals(Handler())

Cam_H_FOV_Entry.set_text(str(Cam_H_FOV))
Cam_V_FOV_Entry.set_text(str(Cam_V_FOV))
Dis_Between_Cams_Entry.set_text(str(Dis_Between_Cams))

if units == 'True':
	UnitToggle.set_active(True)
else:
	UnitToggle.set_active(False)

if greyscale == 'True':
	GreyscaleToggle.set_active(True)
else:
	GreyscaleToggle.set_active(False)

if Same_Cam == 'True':
	CamSameToggle.set_active(True)
else:
	CamSameToggle.set_active(False)

alpha_Scale.set_value(alpha)

Hue_Min_Scale.set_value(Hue_Min)
Saturation_Min_Scale.set_value(Saturation_Min)
Value_Min_Scale.set_value(Value_Min)

Hue_Max_Scale.set_value(Hue_Max)
Saturation_Max_Scale.set_value(Saturation_Max)
Value_Max_Scale.set_value(Value_Max)

X_SCREEN_DEPTH = Coordinate_Calculations.screen_depth(640, Cam_H_FOV)
Y_SCREEN_DEPTH = Coordinate_Calculations.screen_depth(480, Cam_V_FOV)

#All this class does is prints messages to the screen so you can see what going on.
class debug: 
    def __init__(self, socket):
        self.socket = socket
        
    def send(self, text):
        self.socket.send(text)
        print("Send: " + str(text))

    def recv(self):
        recieved = self.socket.recv()
        print("Recived: " + str(recieved))
        return recieved

# Setup some fancy ZMQ socket stuff and connect to the vridge api
context = zmq.Context()
control_channel = context.socket(zmq.REQ)
control_channel.connect("tcp://127.0.0.1:38219")
# First you connect to a control channel (setting up debug class)
vridge_control = debug(control_channel)

# Say hi (this doesnt do anything just confirms everything works. Acknowledgement packet)
vridge_control.send('{"ProtocolVersion":1,"Code":2}')
vridge_control.recv()

# Request special connection for head tracking stuff
vridge_control.send('{"RequestedEndpointName":"HeadTracking","ProtocolVersion":1,"Code":1}')
newconnection = json.loads(vridge_control.recv())
#vridge_control.close() # Close socket

# Connect to new socket (timeout is normally 15 seconds)
endpoint_address = newconnection['EndpointAddress']
endpoint = context.socket(zmq.REQ)
endpoint.connect(endpoint_address)
# Connect to the endpoint channel (setting up debug class)
vridge_endpoint = debug(endpoint)

def show_frame(*args):
	global Color_Min, Color_Max
	Color_Min = (Hue_Min, Saturation_Min, Value_Min)
	Color_Max = (Hue_Max, Saturation_Max, Value_Max)
	ret, frame1 = cap1.read()
	ret, frame2 = cap2.read()
	hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
	hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
	cxy, cyy, cntsy = colorDetector.object_pos(Color_Min, Color_Max, hsv1)
	cxy2, cyy2, cntsy2 = colorDetector.object_pos(Color_Min, Color_Max, hsv2)
	if cxy != None and cxy2 != None and X_SCREEN_DEPTH != None and Y_SCREEN_DEPTH != None:
		#Start Converting Pixel Coordinates To Angles
		CAMERA_ANGLE_AY = Coordinate_Calculations.pixels_to_camera_angle(X_SCREEN_DEPTH, cxy)
		CAMERA_ANGLE_YY1 = Coordinate_Calculations.pixels_to_camera_angle(Y_SCREEN_DEPTH, cyy)
		CAMERA_ANGLE_BY = Coordinate_Calculations.pixels_to_camera_angle(X_SCREEN_DEPTH, cxy2)
		CAMERA_ANGLE_YY2 = Coordinate_Calculations.pixels_to_camera_angle(Y_SCREEN_DEPTH, cyy2)
		#End Converting Pixel Coordinates To Angles
		#Start Calculating Variables Needed For Coordinate Calculations
		THETA_AY, THETA_BY = Coordinate_Calculations.topview_camera_angles_to_internal_angles(CAMERA_ANGLE_AY, CAMERA_ANGLE_BY)
		if THETA_AY or THETA_BY != 0:
			LAY, LBY = Coordinate_Calculations.topview_range_from_cams(Dis_Between_Cams, THETA_BY, THETA_AY)
			#End Calculating Variables Needed For Coordinate Calculations
			#Start Calculating Coordinates
			XY = Coordinate_Calculations.x_coord(THETA_AY, THETA_BY, LAY, LBY, Dis_Between_Cams)
			YY = Coordinate_Calculations.y_coord(THETA_AY, THETA_BY, LAY, LBY)
			ZY = Coordinate_Calculations.z_coord(CAMERA_ANGLE_YY1, YY, CAMERA_ANGLE_YY2, YY)
			#End Calculating Coordinates
			
			
			# Start sending information to Vridge
			print(XY, YY, ZY)
			# Specify the structure for the fancy position matrix
			structure = Struct(
				Const(Int32ul, 2),
				Const(Int32ul, 5),
				Const(Int32ul, 24),
				"data" / Padded(64, Array(3, Float32l)),
			)
			
			offset = [0.0, 0.0, 0.0] # offset in case you want to define where the origin is (in centimeters)
			xyz = [(XY + offset[0]) / 100, (YY + offset[1]) / 100, (ZY + offset[2]) / 100] # Steam VR requires this information in meters
			byte_packet = structure.build(dict(data=xyz))
			endpoint.send(byte_packet)
			print("Send: " + str(structure.parse(byte_packet)))
            endpoint.recv()   
            # Stop sending information to vridge 
			
			
			#Start Drawing Contours
			for (i, c) in enumerate(cntsy):
				# draw the contour
				(x, y), radius = cv2.minEnclosingCircle(c)
				cv2.drawContours(frame1, [c], -1, (0, 255, 255), 2)
				overlay1 = frame1.copy()
				cv2.rectangle(overlay1, (int(cxy+radius), cyy - 30), (int(cxy + radius + 200), cyy+60), (0, 0, 0), -1)
				cv2.addWeighted(overlay1, alpha, frame1, 1 - alpha, 0, frame1)
				if units:
					cv2.putText(frame1, "X Axis " + str(Coordinate_Calculations.ceiling(XY)) +"cm", (int(cxy + radius + 20), cyy), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 150, 0), 1)
					cv2.putText(frame1, "Y Axis " + str(Coordinate_Calculations.ceiling(YY)) +"cm", (int(cxy + radius + 20), cyy + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
					cv2.putText(frame1, "Z Axis " + str(Coordinate_Calculations.ceiling(ZY)) +"cm", (int(cxy + radius + 20), cyy + 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
				else:
					cv2.putText(frame1, "X Axis " + str(Coordinate_Calculations.ceiling(XY)), (int(cxy + radius + 20), cyy), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 150, 0), 1)
					cv2.putText(frame1, "Y Axis " + str(Coordinate_Calculations.ceiling(YY)), (int(cxy + radius + 20), cyy + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
					cv2.putText(frame1, "Z Axis " + str(Coordinate_Calculations.ceiling(ZY)), (int(cxy + radius + 20), cyy + 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)

			for (i, c) in enumerate(cntsy2):
				# draw the contour
				(x, y), radius = cv2.minEnclosingCircle(c)
				cv2.drawContours(frame2, [c], -1, (0, 255, 255), 2)
				overlay2 = frame2.copy()
				cv2.rectangle(overlay2, (int(cxy2+radius), cyy2 - 30), (int(cxy2 + radius + 200), cyy2 + 60), (0, 0, 0), -1)
				cv2.addWeighted(overlay2, alpha, frame2, 1 - alpha, 0, frame2)
				if units:
					cv2.putText(frame2, "X Axis " + str(Coordinate_Calculations.ceiling(XY)) +"cm", (int(cxy2 + radius + 20), cyy2), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 150, 0), 1)
					cv2.putText(frame2, "Y Axis " + str(Coordinate_Calculations.ceiling(YY)) +"cm", (int(cxy2 + radius + 20), cyy2 + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
					cv2.putText(frame2, "Z Axis " + str(Coordinate_Calculations.ceiling(ZY)) +"cm", (int(cxy2 + radius + 20), cyy2 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
				else:
					cv2.putText(frame2, "X Axis " + str(Coordinate_Calculations.ceiling(XY)), (int(cxy2 + radius + 20), cyy2), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 150, 0), 1)
					cv2.putText(frame2, "Y Axis " + str(Coordinate_Calculations.ceiling(YY)), (int(cxy2 + radius + 20), cyy2 + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
					cv2.putText(frame2, "Z Axis " + str(Coordinate_Calculations.ceiling(ZY)), (int(cxy2 + radius + 20), cyy2 + 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
				#End Draw Contours

	vis = np.concatenate((frame1, frame2), axis=1)
	frame = cv2.resize(vis, None, fx=0.7, fy=0.7, interpolation = cv2.INTER_CUBIC)
	if greyscale == True or greyscale == 'True':
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
	else:
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	pb = GdkPixbuf.Pixbuf.new_from_data(frame.tostring(),
										GdkPixbuf.Colorspace.RGB,
										False,
										8,
										frame.shape[1],
										frame.shape[0],
										frame.shape[2]*frame.shape[1])
	image.set_from_pixbuf(pb.copy())
	return True


GLib.idle_add(show_frame)
Gtk.main()


##Oh hi there, I'm the crazy haired blond volunteer who was talking to you about this
##project at the young ict explorers. Congrats for winning first! This was
##my first time volunteering there and it was a lot more amazing than I
##thought it would be. On Sunday the grades 5-6 had some really interesting
##projects as well. When I competed in 2014 I didn't get to look at everybody
##else's in as much depth as this year so it was really good to be able to
##spend the time to talk to students about what they made.
##
##Thanks for giving me a link to your github code, I thought a really cool
##use of this code would be for things where you sit at the computer and
##could use a position tracker like a flight simulator in VR. I don't
##have the kind of money to buy an oculus rift or HTC vive so I wanted to
##create my own VR setup. I know theres this piece of software called
##Vridge made by Riftcat where you can play VR games on your computer and
##they get steamed to your phone via wifi (to be used with a VR headset). 
##The only problem is that it only translates rotational information from 
##your phone, and can't get position information. 
##So I thought if you used this program to get the position
##info it would do pretty good as a DIY vive. Sadly I don't have 2 identical
##webcams to test with but this code should (probably) work. When you
##download/install Vridge, make sure you set it to the beta version as this
##software uses the API which is only available in the beta version. 
##
##You will have to install a few modules first before you get it to work,
##that shouldn't be too hard. I think I just got them from pip install or
##they were already there installed by default. The video I (tried) to show
##you is https://youtu.be/1FYMBoXsBbE where I was able to use 2 PS3Eye
##cameras to do position tracking and parse that information to SteamVR,
##but as you can see its very slow and clearly has bottlenecks. The problem
##with the PS3Eye cameras is that the windows drivers only allow 1 camera
##to be detected and can be used, meaning if I plugged 2 cameras in it 
##ignores the second one. So sadly I couldn't get it working that way.
##I have a .dll that allows PS3Eye multiple cameras to work, but it's
##very difficult to try and get dll's made for C++/C# to work with opencv
##and python.
##
##I took your suggestion about Linux's video API potentially having
##compatible drivers and to my suprise both the latest versions of Ubuntu
##and Fedora seem to support multiple PS3 eye cameras. I thought I tested
##on ubuntu before and it didn't work. Oh well. However when running
##your code I ran into issues when getting the PS3 cameras to work inside
##python using opencv. Nothing to do with your code, it's that 
##cv2.VideoCapture is returning no frames (I believe it returns None).
##
##I would one day like to be able to use a set of Wii remotes in place of
##vive controllers, I was thinking about using an arduino with an 8266 wifi
##board with a gyroscope/accellerometer with an IR ball, which would be
##pretty cool I think. If you have a look on my github/BoomBrush/VRTracker
## page you'll see that i've uploaded a version of my tracker code. It's
## designed to work with a piece of software made by somebody else that
## computes the 3D position, but the way it works is way to complex to
## explain here.
##
##Look, theres a lot more I could have talked about on the day but I kinda
##ran out of time and this is getting a bit long. If it's cool with you
##and your parents (due to the age different, I am 18) shoot me an email
##and we can continue this discussion. Chao.
##
##boombrush [@] hotmail [.dot] com
##
##- Scott Howie
