import random
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 12000))

for i in range(100):
  rand = random.randint(0, 10000)
  message, address = server_socket.recvfrom(2024)
  message = message.upper()
  if rand >= 4:
    server_socket.sendto(message, address)
