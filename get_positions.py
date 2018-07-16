# -*- coding: utf-8 -*-
#goAtoB
#cmd_vel,odom 
#Robot move from A to B
#turlebot
#./know/movaAparaB.py
#name
#controlo, findme
#active


######################################
# This file simulate a robot on ROS. #
# To use, you need to pass like      #
# argument the numnber of robot,     #
# like "./movingRobot 1"             #
######################################


#ROS  imports
import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from std_msgs.msg import String
import os
import random
import sys
import time
####
from tf.transformations import euler_from_quaternion
import tf
import struct
from datetime import datetime
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))

import math
RATE=1


global posicao
posicao = None


global robot1
global robot2
robot1 = None
robot2 = None

def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)
def getpos1(odom):
	global robot1
	x, y, z = getxy (odom)
	robot1 ="("+  str(x) + "," + str(y) + "," + str(z)+")"
def getpos2(odom):
	global robot2
	x, y, z = getxy (odom)
	robot2 ="("+  str(x) + "," + str(y) + "," + str(z)+")"
def getDataFromRos():
	global posicao
	mx, my, mz = getxy (posicao)
	return x, y , mx, my, mz

def getDegreesFromOdom(w):
	#TODO: HOW CONVERT DATA TO ANGLES
	q = [w.pose.pose.orientation.x,	w.pose.pose.orientation.y, w.pose.pose.orientation.z, w.pose.pose.orientation.w]       
        euler_angles = euler_from_quaternion(q, axes='sxyz')
	current_angle = euler_angles[2]
	if current_angle < 0:
		current_angle = 2 * math.pi + current_angle
	return degrees(current_angle)
		

def getxy (odom):
#	return round (odom.pose.pose.position.x), round ( odom.pose.pose.position.y), round (getDegreesFromOdom (odom))#degrees(yall)
	return odom.pose.pose.position.x,  odom.pose.pose.position.y, getDegreesFromOdom (odom)#degrees(yall)

global myId
rospy.init_node("get_positions")
rospy.Subscriber("/robot_1/odom", Odometry, getpos1)
rospy.Subscriber("/robot_0/odom", Odometry, getpos2)

r = rospy.Rate(RATE)
	
lista_pontos = []
try:
	while not rospy.is_shutdown():
		if (robot1 !=  None and robot2 != None):
			lista_pontos.append(robot1 + ":" +  robot2)
		r.sleep()

except Exception :
	raise	
finally:
	arquivo  = open ("posicoes.txt", "w")
	for i in lista_pontos:
		arquivo.write(i+"\n")
	arquivo.close()
print ("Exception!\n")
