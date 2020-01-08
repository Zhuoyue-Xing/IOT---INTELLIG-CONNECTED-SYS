# Created by Chenye Yang, Haokai Zhao, Zhuoyue Xing on 2019/10/13.
# Copyright © 2019 Chenye Yang, Haokai Zhao, Zhuoyue Xing . All rights reserved.
from machine import Pin, I2C
import socket
import ssd1306
import time
import network
import urequests
import json

# ESP8266 connects to a router
def ConnectWIFI(essid, key):
    import network
    sta_if = network.WLAN(network.STA_IF)   # config a station object
    if not sta_if.isconnected():            # if the connection is not established
        print('connecting to network...')
        sta_if.active(True)                 # activate the station interface
        sta_if.connect(essid, key)  # connect to WiFi network
        while not sta_if.isconnected():
            print('connecting')
            pass
        print('network config:', sta_if.ifconfig()) # check the IP address
        # ap_if.active(False)                   # disable the access-point interface
    else:
        print('network config:', sta_if.ifconfig()) # IP address, subnet mask, gateway and DNS server

# ESP8266 as a server to listen and response
def ListenResponse():
    goodHTML = """<!DOCTYPE html>
    <html>
        <head> <title>Good Command</title> </head>
        <body> <h1>The command from you is received by ESP8266</h1></body>
    </html>
    """

    badHTML = """<!DOCTYPE html>
    <html>
        <head> <title>Bad Command</title> </head>
        <body> <h1>The command from you is NOT received by ESP8266</h1></body>
    </html>
    """

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1] # Set web server port number to 80
    s = socket.socket()
    s.bind(addr) # Bind the socket to address
    s.listen(1) # Enable a server to accept connections
    print('listening on', addr)

    while True:
        cl, addr = s.accept()
        print('client connected from', addr)
        # ESP8266 listen from the port
        # The client terminal instruction should be like:
        # curl -H "Content-Type:application/json" -X POST -d '{"Command":"Code Works"}' http://192.168.50.100:80
        cl_receive = cl.recv(500).decode("utf-8").split("\r\n")[-1] # get the Command in json string
        try:
            cl_receive = json.loads(cl_receive) # convert the json string to json
            print(cl_receive['Command'])
        except:
            response = badHTML
        else:
            response = goodHTML
        # write to the port, i.e., give response
        cl.send(response)
        cl.close()

if __name__ == '__main__':
    ConnectWIFI('Rock_NYC','Columbia_SEAS_1754') # connect esp8266 to a router

    ListenResponse() # Show ESP8266 Pins to test server
    

    



