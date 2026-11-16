
from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8

def checksum(data):
    csum = 0
    countTo = (len(data) // 2) * 2

    for count in range(0, countTo, 2):
        thisVal = data[count + 1] * 256 + data[count]
        csum = (csum + thisVal) & 0xffffffff

    if countTo < len(data):
        csum = (csum + data[-1]) & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum += csum >> 16
    answer = ~csum & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while True:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect

        if not whatReady[0]:
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        ipHeaderLength = (recPacket[0] & 0x0F) * 4
        icmpHeader = recPacket[ipHeaderLength:ipHeaderLength + 8]

        icmpType, code, recvChecksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )

        if icmpType == 0 and packetID == ID:
            timeSent = struct.unpack(
                "d", recPacket[ipHeaderLength + 8:ipHeaderLength + 16]
            )[0]

            delay = (timeReceived - timeSent) * 1000
            return f"Reply from {addr[0]}: time={delay:.2f} ms"
        # Fill in end

        timeLeft -= howLongInSelect

        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    myChecksum = 0

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())

    myChecksum = checksum(header + data)

    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF

    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    dest = gethostbyname(host)
    print(f"Pinging {host} ({dest}) using Python:\n")

    for i in range(4):
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    ping(host)
