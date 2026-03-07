import socket

website = input("Enter website name (example: google.com): ")

try:
    ip = socket.gethostbyname(website)
    print("Website:", website)
    print("IP Address:", ip)
except:
    print("Unable to get IP address")