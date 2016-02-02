#http://www.tutorialspoint.com/http/http_requests.htm

#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Kieran Boyle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #this function gets the value of the host port
    def get_host_port(self,url):
        #self.url_contents = url.split(':')
        #print self.url_contents
        contents = url.split("/")
        host_port =  int(contents.pop(0))
        #print contents
        dash = "/"
        path = dash.join(contents)
        return host_port, path
    #this function connects to the server via socket
    def connect(self, host, port):
        # use sockets!
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, port))
        return clientsocket
    #this function gets the value of code that needs to be returned
    def get_code(self, data):
        contents = data.split(' ')
        code = contents[1]
        #print code
        return int(code)
    #I actually do not use this function
    def get_headers(self,data):
        #print(data)
        return None
    #this returns the body of the response
    def get_body(self, data):
        if len(data) > 1:
            return data[1]
        else:
            return data[0] 
    #this function breaks the url down into pieces so things can be done
    def breakdown_url (self, url):
        url_content = url.split(":")
        url_content.pop(0)
        print url_content
        if len(url_content)== 2:
            #print url_content[1]
            host_port, path = self.get_host_port(url_content[1])
            host =  url_content[0].strip("//")

        elif len(url_content) == 1:
            host_port = 80
            url_info = url_content[0].strip("//")
            #print "WUUUUUUUUUUUUUUUUUUUUUUUUUT"
            #print  url_info
            #print "*************************************************************"
            if "/" in url_info:
                url_pieces = url_info.split("/")
                host = url_pieces.pop(0)
                dash = "/"
                path = dash.join(url_pieces)
            else:
                host = url_info
                path = ''
        #print "#################################################################"    
        #print "host: ",host
        #print "host port: ",host_port
        #print "#################################################################"  
        #print "path: ",path
        return host, host_port, path
    
    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)
    #this is for the get methods that allow you to ahndle HTTP gets
    def GET(self, url, args=None):
        code = 500
        body = ""
        if args == None:
            arguments = ''
        else:
            arguments = urllib.urlencode(args)
            
        host, port,path = self.breakdown_url(url)
        
        sock = self.connect(host, port)
        sock.sendall("GET /"+path+" HTTP/1.1\r\n")
        sock.sendall("Host: "+host+"\r\n\r\n")
        sock.sendall(str(arguments)+"\r\n")
        sock.sendall("Connection: close\r\n\r\n")
        response = self.recvall(sock)
        print response
        returns =  response.split("\r\n\r\n")
        sock.close()
        #print returns
        code = self.get_code(returns[0])
        body = self.get_body(returns) 
        return HTTPRequest(code, body)
    #This function handles post requests
    def POST(self, url, args=None):
        code = 500
        body = ""
        
        if args == None:
            arguments = ''
        else:
            arguments = urllib.urlencode(args)
        print "these are the arguments "+arguments    
        host, port,path = self.breakdown_url(url)
        sock = self.connect(host, port)
        sock.sendall("POST /"+path+" HTTP/1.1\r\n")
        sock.sendall("Host: "+host+"\r\n")
        sock.sendall("Content_Type: application/x-www-form-urlencoded\r\n")
        sock.sendall("Content-Length: "+ str(len(arguments))+"\r\n\r\n")
        sock.sendall(str(arguments)+"\r\n\r\n")
        sock.sendall("Connection: close\r\n\r\n")
        response = self.recvall(sock)
        print response
        returns =  response.split("\r\n\r\n")
        sock.close()        
        sock = self.connect(host, port)
        code = self.get_code(returns[0])
        body = self.get_body(returns)        
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
