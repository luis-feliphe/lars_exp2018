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
from kobuki_msgs.msg import Sound
from tf.transformations import euler_from_quaternion
import tf
import struct
from datetime import datetime
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))

import math
RATE=10

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
	return right + left

#        print "Tamanho do objeto:" + str (left) +"+"+ str(right) +"="+str(left+right)+ "\n"



def get_distance(scan):
	temp = list (scan.ranges)
	for n, i in enumerate (temp):
		if math.isnan(i):
			temp[n] = 3
	for i in range (0,len(temp)):
		temp[i] = round (temp[i] * 100,1)
	global distancia
	distancia = temp 
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

def get_answer (resposta):
	global tarefa
	global caixa
	resposta = resposta.data
	if resposta.count("comando_1")==1:
		tarefa = 1
	if resposta.count("comando_2")==1:
		tarefa = 2
	if resposta.count("caixa_grande")==1:
		caixa = True
		print "Reconheci uma caixa grande pela imagem"
	if resposta.count("caixa_pequena")==1:
		caixa = True
		print "Reconheci uma caixa pequena pela imagem"
			

def getxy (odom):
#	return round (odom.pose.pose.position.x), round ( odom.pose.pose.position.y), round (getDegreesFromOdom (odom))#degrees(yall)
	return odom.pose.pose.position.x,  odom.pose.pose.position.y, getDegreesFromOdom (odom)#degrees(yall)

def goto(value):
#points = [(0, -2, 0), (2,-2,90), (2,2,90), (0,2,0)]
	global robot_id
	global r
	if robot_id != 1:
		print "\nRecebeu o goto \n"
		while not hasMasterPos():
			print "Esperando posicao do mestre"
			r.sleep()
			break
#		orientation = str(value.data)
#		if hasMasterPos():
#			x_r, y_r, z_r = getMasterPos()
#		distance = 0.75
#		if orientation == "n":
#			x_r += distance
#		elif orientation == "s":
#			x_r += distance
#		elif orientation == "l":
#			y_r -= distance
#		elif orientation == "o":
#			y_r += distance
		
		algoritmo = Controlo()
		global master
		while True:
			cont = 0
			if hasDataToWalk() and master != None:
				global contPontos
				global p
				x, y , mx, my, mz = getDataFromRos()
				x_r, y_r, z_r = getMasterPos()
				x_r -= 0.45
#				y_r -= 0.50
				t= Twist()
				lin,ang  = algoritmo.start(x_r ,y_r , z_r, mx, my, mz)
				t.angular.z = ang
				t.linear.x = lin
				print "publicando o valor" + str (ang) + " : " + str(lin) + " e indo para " + str (x_r) + " : " + str(y_r)
				p.publish(t)
				if (lin == 0 and ang == 0):
					cont += 1
					if (cont>20):
						break
			r.sleep()

#############
# ROS SETUP #
#############
#Became a node, using the arg to decide what the number of robot
global robot_id
robot_id = sys.argv[1]
print "ROBOT ID = "+str (robot_id)
robot_id = int (robot_id)

global r
if robot_id == 2:
	rospy.init_node("control_r"+str(robot_id))
	#rospy.Subscriber("/robot_0/base_pose_ground_truth", Odometry, get_pos_master)
	rospy.Subscriber("/robot_0/odom" , Odometry, get_pos_master)
	rospy.Subscriber("/robot_1/odom" , Odometry, get_pos)
#	rospy.Subscriber("/robot_1/base_pose_ground_truth", Odometry, get_pos)
	#rospy.Subscriber("robot_"+str(robot_id)+"/scan", LaserScan, get_distance)
	rospy.Subscriber("/robot_1/base_scan", LaserScan, get_distance)
	#p = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist)
	p = rospy.Publisher("/robot_1/cmd_vel_mux/input/teleop", Twist)
	rospy.Subscriber("/goto", String, goto)
else: 
	rospy.init_node("control_r"+str(robot_id))
	rospy.Subscriber("/robot_0/odom", Odometry, get_pos)
	#rospy.Subscriber("/robot_0/base_pose_ground_truth", Odometry, get_pos)
	#rospy.Subscriber("robot_"+str(robot_id)+"/scan", LaserScan, get_distance)
	rospy.Subscriber("/robot_0/scan", LaserScan, get_distance)
	#p = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist)
	rospy.Subscriber("/robot_0/answer", String, get_answer)
	global p
#	p = rospy.Publisher("/robot_0/cmd_vel", Twist)
	p = rospy.Publisher("/robot_0/cmd_vel_mux/input/teleop", Twist)
	goto = rospy.Publisher("/goto", String) #send message to the slave
	psound = rospy.Publisher("/robot_0/mobile_base/commands/sound", Sound) #send message to the slave





u = 1.5
	
#################
#   Main Loop   #
#################
#points = [(2,2,90), (0,2,0)]
points = [(0, -2, 0), (2,-2,90), (2,2,90), (0,2,0)]
#points = [(2, 2, 90), (0.2,2,90)]

#points = [(0, -u)]
cont = 0
posInicialx=0
posInicialy=0


global tarefa
tarefa = 3 #1 - 1 robô\ 2 - 2 robôs \ 3 - esperando comand

global caixa 
caixa = False
contador_imagem = 1

r = rospy.Rate(RATE) # 5hz
#### Iniciando o loop principal ######
sended = False
if robot_id == 1:
	while tarefa ==3:
		if (distancia != None and min (distancia) < 100 ):
			file_name="imagem"+str(contador_imagem)+".jpg"
			cont +=1
			os.system("python take_photo.py " + str (file_name))
			psound.publish (Sound.ON)
			print "Detectado um obstáculo"
			os.system("python client.py " + str(file_name))
			break
		print "Aguardando alguem passar na frente para dá o comando"
		r.sleep()

print "Saiu do loop com o comando " + str (tarefa)

distancia = None

if robot_id != 1:
	print "Esperando indicacao do mestre"
	while True:
		r.sleep()
else:

	try:
		algoritmo = Controlo()
		print "Iniciando busca pela caixa"

			
		while not rospy.is_shutdown():
			if hasDataToWalk():
				t= Twist()
				global distancia
				if tarefa == 2 and not ask_for_help :
					resp = "s"
					goto.publish(resp)
					ask_for_help = True
					print "pediu ajuda"
				if (distancia != None and min (distancia) < 160 and min (distancia) > 25 ):
					if sended==False:
						sended = True
						file_name="imagem"+str(contador_imagem)+".jpg"
						cont +=1
						os.system("python take_photo.py " + str (file_name))
						os.system("python client.py " + str(file_name))
						tamanho = get_size(distancia, min (distancia))
						print "Tamanho do obstáculo:"+str (tamanho) + "\nDistância até obstáculo" + str(min(distancia))
						if tamanho > 60:
							resp = "n"
							goto.publish(resp)
							psound.publish (Sound.ON)
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
				distancia = None

	except Exception :
		raise	
	print ("Exception!\n")
