
from socket import *
import time

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

serverAddress = ('127.0.0.1', 12000)

for sequence in range(1, 11):
    message = f"Ping {sequence} {time.time()}"
    startTime = time.time()

    clientSocket.sendto(message.encode(), serverAddress)

    try:
        response, address = clientSocket.recvfrom(1024)
        rtt = time.time() - startTime

        print(f"{response.decode()} | RTT: {rtt:.6f} seconds")

    except timeout:
        print(f"Ping {sequence}: Request timed out")

clientSocket.close()
