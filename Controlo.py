# -*- coding: utf-8 -*-
#controlo
#none
#Algoritm that allows robots to go to coordinates xy
#turtlebot, pionneer
#./know/Controlo.py
#none
#passive


import math


class Controlo :
	def __init__ (self):
		#real turtlebot
		self.VEL_MAX= 0.11
		self.VEL_MAX_ANG=0.80
		#to simulation
#		self.VEL_MAX= 0.4
#		self.VEL_MAX_ANG=0.2
		self.lex= 0
		self.ley= 0
		self.mId= 0
		self.mmx=0
		self.mmy=0
		self.mmz=0
		self.targets = [[10, 10], [-10, 10], [-10, -10] , [10, -10]]
		self.myTarget = 0

	def myPosition(self):
		return self.mmx, self.mmy, self.mmz
	def walkon(self):
		return self.VEL_MAX, 0 #linear and angular modificado 1
	def walkright(self):
		return 0.001, -self.VEL_MAX_ANG #linear and angular modificado -0.5
	def walkleft(self):
		return 0.001, self.VEL_MAX_ANG#linear and angular modificado 0.5
	def walkhorario(self):
		return 0.04, -self.VEL_MAX_ANG #linear and angular modificado -0.5
	def walkantihorario(self):
		return 0.04, self.VEL_MAX_ANG#linear and angular modificado 0.5
	def degrees(self, value):
		return ((value* 180.0)/math.pi)
	def changeTarget(self):
		self.myTarget = (self.myTarget + 1) % (len (self.targets))
#Walking and redirecting
	def walkhorarioon(self, vel):
		return 0.001, -self.VEL_MAX_ANG #linear and angular modificado -0.5
	def walkantihorarioon(self, vel):
		return 0.001, self.VEL_MAX_ANG #linear and angular modificado 0.5
	def walkonhorario(self):
		return self.VEL_MAX, -0.01 #linear and angular modificado 0.5
	def walkonantihorario(self):
		return self.VEL_MAX, 0.01 #linear and angular modificado 0.5



	def whereImGoing(self):
		lx= float(self.lex)
		ly= float (self.ley)
		lz= float (self.lez)
		return lx, ly, lz


	def isOriented(self):
		x, y, z= self.whereImGoing()
		mx, my, mz = self.myPosition()
		if (not (mx == 0 and my == 0)):
			#calcula a distancia entre meu ponto e o ponto que quero ir
			hip = math.hypot (x - mx, y - my)
			#calcula a distancia dos dois catetos
			tmp1 = math.hypot( x -mx, 0 )
			tmp2 = math.hypot( 0, y -my )
			#seleciona o maior cateto
			cat = max ([tmp1, tmp2])
			#calcula o angulo que preciso estar para
			anguloEsperado = self.degrees(math.cos(float(cat)/hip))
			deltax = x - mx
			deltay = y - my
			deltax = abs(deltax)
			deltay = abs(deltay)
			if (deltax<0.19) and y > my:
			        anguloEsperado = 90
			elif (deltax<0.19) and y < my:
			        anguloEsperado = 270
			elif (deltay<0.19) and mx < x:
			        anguloEsperado = 0
			elif (deltay<0.19) and mx > x:
			        anguloEsperado = 180
			elif mx < x and my <=y:
			        pass#anguloEsperado += 180 
			elif mx < x and my >= y:
			        anguloEsperado= anguloEsperado +270# = 180 - anguloEsperado
			elif mx > x and my <= y:
			        anguloEsperado= anguloEsperado + 90# = 360 - anguloEsperado
			elif mx > x and my >= y:
			        anguloEsperado =anguloEsperado + 180# anguloEsperado
			a = max ([anguloEsperado, mz])
			b = min ([anguloEsperado , mz])
			limin = 3
			if ((a - b) < limin or ((a-b)>(360-limin))):
			        return True , anguloEsperado, mz, hip
			return False, anguloEsperado, mz, hip
		return False, 1000, 800, 1000




	def inPosition(self):
		x, y ,z = self.whereImGoing()
		mx, my, mz = self.myPosition()
		# Distancia original = 0.3
		if ((math.hypot(x-mx, y-my))< 0.10):
		        return True
		return False


	def walk (self):
		x, y,z  = self.whereImGoing()
#		print "Going to : (" + str (x) + " " + str (y) + " " + str(z)
		mx, my, mz = self.myPosition()
	        if (not self.inPosition()):
	                orient, ang, mz, hip = self.isOriented()
	                if (orient):
				#muito Orientado
				if (int (mz) == int (ang)):
					#self.log.broadcast(ptolemy.data.StringToken("em frente "))
	                        	return self.walkon()
				#Orientado mas necessita de ajustes TODO: NO ORIGINAL TEM UM ELIF
				else:
					if ((ang-mz)>= 0):
						if (ang-mz)< 180:
							return self.walkonantihorario()
						else:
							return self.walkonhorario()
					else:
						if (ang-mz)< 180:
							return self.walkonhorario()
						else:
							return self.walkonantihorario()

			#Não está orientado, com distancia curta TODO provavelmente elif ou if nao faz diferenca nesse caso por causa do return
			if hip < 2:
			        if ((ang - mz) >= 0):
					if ((ang- mz) < 180):
						return self.walkantihorario()
					else: 
						return self.walkhorario()
				elif((ang- mz) < 0):
					if (abs((ang- mz)) < 180):
						return self.walkhorario()
					else: 
						return self.walkantihorario()
			#Não está orientado, possuindo grande distancia ao alvo
			else:
				velocidade = 0.5# self.calculaVelocidadeLinear(hip)
			        if ((ang - mz) >= 0):
					if ((ang- mz) < 180):
						return self.walkantihorarioon(velocidade)
					else: 
						return self.walkhorarioon(velocidade)
				elif((ang- mz) < 0):
					if (abs((ang- mz)) < 180):
						return self.walkhorarioon(velocidade)
					else: 
						return self.walkantihorarioon(velocidade)
		#Na posicao, mas precisa estar no angulo correto
		else:
			#muito Orientado
			a = max ([mz, z])
			b = min ([mz, z])
			if (int (mz) == int (z)or (a -b <5)):
                        	return 0,0

			if ((z-mz)>= 0):
				if (z-mz)< 180:
					return self.walkleft()
				else:
					return self.walkright()
			else:
				if (z-mz)> 180:#mudança punk
					return self.walkright()
				else:
					return self.walkleft()

	def start(self, x, y, z , mx, my, mz):
		#where im going
		self.lex  = x
		self.ley  = y
		self.lez = z
		#my position
		self.mmx  = mx
		self.mmy  = my 
		self.mmz  = mz
		return self.walk()

