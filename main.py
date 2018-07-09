# -*- coding: utf-8 -*-
######################################
#Move o robo em quadrados e para ao  #
#identificar um obstáculo	     #
######################################


from Controlo import Controlo
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
import datetime
####
import numpy
from tf.transformations import euler_from_quaternion
import tf
import struct
from datetime import datetime
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))

import math
RATE=6

global posicao
posicao = None

global distancia
distancia = None

def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)

def get_pos(odom):
	global posicao
	posicao= odom

def get_size (vector, menor_distancia):
        number_elements =  len (vector)
        margin = numpy.mean (vector)/2
        right = 0
        left = 0
        previous = vector[len(vector)/2]
        for i in range(len (vector)/2, number_elements):
#               print ("visitando : " + str(vector[i]))
                if max(vector[i] ,previous) - min (vector[i] ,previous) > margin:
#                       print ("Parou em : " + str(vector[i]))
                        break
                right+=1
                previous = vector[i]
        tmp =[]
        for i in  reversed (vector):
                tmp.append(i)
        for i in range(len (vector)/2+1, number_elements):
#               print ("visitando : " + str(tmp[i]))
                if (max(tmp[i] ,previous) - min (tmp[i] ,previous)) > margin:
#                       print ("Parou em : " + str(tmp[i]))
                        break
                left+=1
                previous = tmp[i]
#        print str (left) +"+"+ str(right) +"="+str(left+right)
        left = math.tan(left *0.0016) * menor_distancia
        right = math.tan(right * 0.0016) * menor_distancia


        print "Tamanho do objeto:" + str (left) +"+"+ str(right) +"="+str(left+right)



def get_distance(scan):
	global distancia 
	distancia = min ( scan.ranges)
	print "\n\n" + str (scan.ranges)
#	print "Angulo inicial  " + str(scan.angle_min) + " Angulo final " + str(scan.angle_max) + " intervalo de  "+ str(scan.angle_increment) + "Tamanho " + str (len (scan.ranges))
#	print "distancia minima " + str(scan.range_min) + " distancia maxima " + str(scan.range_max) + "ranges "+ str(min(remove_fromList(var.ranges, 5.0)))

def hasDataToWalk():
	global posicao
	return posicao != None

def getDataFromRos():
	global posicao
	x, y, z = 0, 0 ,0
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

#############
# ROS SETUP #
#############
#Became a node, using the arg to decide what the number of robot
global myId



myId = 1

rospy.init_node("controle_robo_myId")
rospy.Subscriber("/odom", Odometry, get_pos)
rospy.Subscriber("/scan", LaserScan, get_distance)
p = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist)

r = rospy.Rate(RATE) # 5hz


u = 1.5
	
#################
#   Main Loop   #
#################
points = [(2,2,90), (0,2,0)]
#points = [(0, -2, 0), (2,-2,90), (2,2,90), (0,2,0)]

#points = [(0, -u)]
cont = 0
posInicialx=0
posInicialy=0







#### Iniciando o loop principal ######

try:
	algoritmo = Controlo()
	while not rospy.is_shutdown():
		if hasDataToWalk():
			global distancia
			if (distancia != None and distancia < 2.5 and distancia > 0.1):
				print "Chegamos a caixa com distância de  " + str(distancia)
				t.angular.z = 0
				t.linear.x = 0
				p.publish(t)
				continue
			x, y , mx, my, mz = getDataFromRos()
			t= Twist()
			x, y, z = points[cont]
			lin,ang  = algoritmo.start(x, y, z, mx, my, mz)
			if (lin == 0 and ang == 0):
				cont= (cont + 1)%len (points)
				print ("Chegamos ao ponto " + str (cont) )
				if (cont == 0):
					print "CHEGAMOS NO PONTO FINAL"
					
			global saida
			t.angular.z = ang
			t.linear.x = lin
			p.publish(t)
		r.sleep()

except Exception :
	raise	
print ("Exception!\n")
