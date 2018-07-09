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
RATE=1

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
	ANGLE = 0.00171110546216
        number_elements =  len (vector)
        margin = numpy.std (vector)/2
#	print ("Margem de : " + str (margin))
        right = 0
        left = 0
	cont = 0
        previous = vector[len(vector)/2]
        for i in range(len (vector)/2, number_elements):
#		print ("visitando : " + str(vector[i]))
		if max(vector[i] ,previous) - min (vector[i] ,previous) > margin:
			if cont > 1:
#				print ("Parou em : " + str(vector[i]))
				right = right -1
				break
			else:
				cont+=1
	                	right+=1
		else:
	                right+=1
	                previous = vector[i]
			cont = 0
        tmp =[]
        for i in  reversed (vector):
                tmp.append(i)
        for i in range(len (vector)/2+1, number_elements):
#		print ("visitando : " + str(tmp[i]))
                if (max(tmp[i] ,previous) - min (tmp[i] ,previous)) > margin:
			if cont > 1:
#				print ("Parou em : " + str(vector[i]))
				left= left -1
				break
			else:
				cont+=1
	                	left+=1
		else:
	                left+=1
	                previous = tmp[i]
			cont = 0

#print "Numero de angulos visitados : "+ str (left) +"+"+ str(right) +"="+str(left+right)
#print "Angulos : "+ str (math.degrees (left*ANGLE)) +"+"+ str(math.degrees(right*ANGLE)) +"="+str(math.degrees ((left*ANGLE)+ (right*ANGLE)))
        left = math.tan(left *ANGLE) * menor_distancia
        right = math.tan(right * ANGLE) * menor_distancia


        print "Tamanho do objeto:" + str (left) +"+"+ str(right) +"="+str(left+right)+ "\n"



def get_distance(scan):
	global distancia 
	distancia = list (scan.ranges)
	for n, i in enumerate (distancia):
		if math.isnan(i):
			distancia[n] = 3
	for i in range (0,len(distancia)):
		distancia[i] = round (distancia[i] * 100,1)
#	print "\n\n" + str (scan.ranges)
#	print "Angulo inicial  " + str(scan.angle_min) + " Angulo final " + str(scan.angle_max) + " intervalo de  "+ str(scan.angle_increment) + "Tamanho " + str (len (scan.ranges))
#	print "distancia minima " + str(scan.range_min) + " distancia maxima " + str(scan.range_max) + "ranges "+ str(distancia)

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
			t= Twist()
			global distancia
#			print "Distancia = > "+ str (min (distancia))
			if (distancia != None and min (distancia) < 200 and min (distancia)> 25):
				print "\nChegamos a caixa com distância de  " + str(min (distancia))
				get_size(distancia, min(distancia))
				t.angular.z = 0
				t.linear.x = 0
				p.publish(t)
				continue
			x, y , mx, my, mz = getDataFromRos()

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
			print "andando"
#			p.publish(t)
		r.sleep()

except Exception :
	raise	
print ("Exception!\n")
