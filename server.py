import socket
import os
import sys
import time
import random
import subprocess

def processar_arquivo (file_name):
	#Processa a rede propriamente para mãos
	if (False):
		answer_file = file_name.replace(".jpg",".txt")
		os.system("./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights " + str (file_name) + " >> "+ str (answer_file))
		resultado = open (answer_file, "r")
		retorno = ""	
		for linha in resultado.readlines():
			retorno += str(linha)
		return retorno
	else:
		return "Imagem "+ str(file_name) + " foi processada com sucesso no servidor deeplearnig"

def processar_arquivo2 (file_name):
	#Processa a rede propriamente para caixa
	if (False):
		answer_file = file_name.replace(".jpg",".txt")
		os.system("./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights " + str (file_name) + " >> "+ str (answer_file))
		resultado = open (answer_file, "r")
		retorno = ""	
		for linha in resultado.readlines():
			retorno += str(linha)
		return retorno
	else:
		return "Imagem "+ str(file_name) + " foi processada com sucesso no servidor deeplearnig"

HOST = '150.165.138.190'         # Endereco IP do Servidor
PORT = 5000           		 # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(4)
cont = 1
while True:
	print "-----------------\n\tWainting for connections\n"
	con, addr = tcp.accept()
	fname = "arquivo_recebido" + str(addr)+".jpg"
	fname = fname.replace("(","").replace(")","").replace("'","").replace(",","").replace(".","").replace("jpg",".jpg").replace(" ","")
	arq = open(fname, "wb")
	dados = None


	print "\tOnline with "+ str (addr)

	while dados <> "\x18" :
		dados = con.recv(1024)
		if dados.count("EndOF"):
			dados = dados.replace("EndOF", "")
			if len(dados)> 0:
				arq.write(dados)
			arq.close()
			print "\tProcessando Arquivo\n"
			print ("O NOME DO ARQUIVO \n\n" + fname + "\n\n")
			if cont%2==0:
				con.send(processar_arquivo(fname))
			else:
				con.send(processar_arquivo2(fname))
			break
		if not dados:
			break
		arq.write(dados)
	con.close()
	print "\nFinished\n\n"
