import time
import socket
import sys
import rospy
from std_msgs.msg import String
#HOST = '127.0.0.1'     # Endereco IP do Servidor
HOST = '150.165.138.191'     # Endereco IP do Servidor
PORT = 5001            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

#arquivo = raw_input ("Digite o arquivo a ser enviado, para teste aperte enter \n")
#Utiliza arquivo de teste
arquivo = sys.argv[1]
if arquivo == '':
        arquivo = "./arquivo_teste.jpg"

fp = open(arquivo, "rb")

for line in fp.readlines():
        tcp.send(line)
tcp.send("EndOF")
#print "------------\n+++++  Recebendo Resposta ++++\n------------"
x = tcp.recv(512)

#print ("\n\t => Resultado = " + str (x))

tcp.close()
#print "\nConection Closed."


time.sleep(2)
print "\n\nAcordando ... \n"
# Enviando resposta     
rospy.init_node ("client_deep_learning")
r = rospy.Rate(6)
p = rospy.Publisher("answer", String)


for i in range (10):
	p.publish(str(x))
	r.sleep()



