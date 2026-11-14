
from socket import *
import ssl
import base64

mailserver = "smtp.mail.yahoo.com"
port = 465

sender = "type the sender email here"
password = "type the password here"
recipient = "type the recipient email here"

msg = "\r\nI love computer networks!"
endmsg = "\r\n.\r\n"

def receive_response(sock):
    response = sock.recv(4096).decode()
    print(response)
    return response

# Create TCP socket and establish encrypted connection
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.settimeout(15)
clientSocket.connect((mailserver, port))

context = ssl.create_default_context()
clientSocket = context.wrap_socket(
    clientSocket, server_hostname=mailserver
)

receive_response(clientSocket)

# Send HELO command
clientSocket.sendall(b"EHLO localhost\r\n")
receive_response(clientSocket)

# Authenticate
clientSocket.sendall(b"AUTH LOGIN\r\n")
receive_response(clientSocket)

clientSocket.sendall(
    base64.b64encode(sender.encode()) + b"\r\n"
)
receive_response(clientSocket)

clientSocket.sendall(
    base64.b64encode(password.encode()) + b"\r\n"
)
receive_response(clientSocket)

# MAIL FROM
clientSocket.sendall(
    f"MAIL FROM:<{sender}>\r\n".encode()
)
receive_response(clientSocket)

# RCPT TO
clientSocket.sendall(
    f"RCPT TO:<{recipient}>\r\n".encode()
)
receive_response(clientSocket)

# DATA
clientSocket.sendall(b"DATA\r\n")
receive_response(clientSocket)

# Send message
clientSocket.sendall(
    f"From: {sender}\r\n"
    f"To: {recipient}\r\n"
    f"Subject: Python SMTP Lab 3\r\n"
    f"{msg}\r\n".encode()
)

# End message
clientSocket.sendall(endmsg.encode())
receive_response(clientSocket)

# QUIT
clientSocket.sendall(b"QUIT\r\n")
receive_response(clientSocket)

clientSocket.close()