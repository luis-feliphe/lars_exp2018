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
global master
master = None
global distancia
distancia = None

def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)
def hasMasterPos():
	global master
	return master!= None

def get_pos_master (odom):
	print "RECEBIDA A POSICAO \n"
	global master
	master = odom

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


#        print "Tamanho do objeto:" + str (left) +"+"+ str(right) +"="+str(left+right)+ "\n"



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

def getMasterPos():
	global master
	return getxy(master)
	

def getDataFromRos():
	global posicao
	x, y, z = 0,0,0
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

def goto(value):
#points = [(0, -2, 0), (2,-2,90), (2,2,90), (0,2,0)]
	global robot_id
	if robot_id != 1:
		while True:
			if hasMasterPos():
				break
#		orientation, x,y,z = str(value.data).split(":")
		orientation = str(value.data)
		
#		x_r = float (x)
#		y_r = float (y)
#		z_r = float (z)
		if hasMasterPos():
			x_r, y_r, z_r = getMasterPos()
		distance = 0.75
		if orientation == "n":
			x_r += distance
		elif orientation == "s":
			x_r += distance
		elif orientation == "l":
			y_r -= distance
		elif orientation == "o":
			y_r += distance
		
		algoritmo = Controlo()
		global master
		while True:
			if hasDataToWalk() and master != None:
				global contPontos
				global p
				x, y , mx, my, mz = getDataFromRos()
				x_r, y_r, z_r = getMasterPos()
				x_r -= 0.75
				y_r -= 0.75
				t= Twist()
				lin,ang  = algoritmo.start(x_r ,y_r , z_r, mx, my, mz)
				t.angular.z = ang
				t.linear.x = lin
				p.publish(t)
				if (lin == 0 and ang == 0):
					break

#############
# ROS SETUP #
#############
#Became a node, using the arg to decide what the number of robot
global robot_id
robot_id = sys.argv[1]
print "ROBOT ID = "+str (robot_id)
robot_id = int (robot_id)

if robot_id == 2:
	rospy.init_node("control_r"+str(robot_id))
	rospy.Subscriber("/robot_0/base_pose_ground_truth", Odometry, get_pos_master)
	#rospy.Subscriber("robot_"+str(robot_id)+"/odom", Odometry, get_pos)
	rospy.Subscriber("/robot_1/base_pose_ground_truth", Odometry, get_pos)
	#rospy.Subscriber("robot_"+str(robot_id)+"/scan", LaserScan, get_distance)
	rospy.Subscriber("/robot_1/base_scan", LaserScan, get_distance)
	#p = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist)
	p = rospy.Publisher("/robot_1/cmd_vel", Twist)
	rospy.Subscriber("/goto", String, goto)
else: 
	rospy.init_node("control_r"+str(robot_id))
	#rospy.Subscriber("robot_"+str(robot_id)+"/odom", Odometry, get_pos)
	rospy.Subscriber("/robot_0/base_pose_ground_truth", Odometry, get_pos)
	#rospy.Subscriber("robot_"+str(robot_id)+"/scan", LaserScan, get_distance)
	rospy.Subscriber("/robot_0/base_scan", LaserScan, get_distance)
	#p = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist)
	global p
	p = rospy.Publisher("/robot_0/cmd_vel", Twist)
	goto = rospy.Publisher("/goto", String) #send message to the slave





u = 1.5
	
#################
#   Main Loop   #
#################
#points = [(2,2,90), (0,2,0)]
points = [(0, -2, 0), (2,-2,90), (2,2,90), (0,2,0)]
points = [(2, 2, 90), (0.2,2,90)]

#points = [(0, -u)]
cont = 0
posInicialx=0
posInicialy=0



tarefa = 2 #1 - 1 robô\ 2 - 2 robôs



r = rospy.Rate(RATE) # 5hz
#### Iniciando o loop principal ######
sended = False

if robot_id != 1:
	print "Esperando indicacao do mestre"
	while True:
		r.sleep()
else:

	try:
		algoritmo = Controlo()
		print "\n\n\n"

			
		while not rospy.is_shutdown():
			if hasDataToWalk():
				t= Twist()
				global distancia
				if tarefa == 2 :
					resp = "s"
					goto.publish(resp)
				if (distancia != None and min (distancia) < 200 and min (distancia) > 25):
					#print "Chegamos a caixa com distância de  " + str(distancia)
					#x, y , mx, my, mz = getDataFromRos()
					resp = "n"
					goto.publish(resp)
					get_size(distancia, min (distancia))
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
				p.publish(t)

	except Exception :
		raise	
	print ("Exception!\n")
