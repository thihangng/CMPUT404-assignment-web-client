#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Hang Ngo
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

from email import header
import sys
import socket
import re
from unittest.mock import DEFAULT
# you may use urllib to encode data appropriately
import urllib.parse as p


DEFAULT_HTTP_PORT = 80
DEFAULT_HTTPS_PORT = 443
def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            return None
        except Exception as e:
            print("Problem in connection to %s on port %d" % (host, port))
        return False

    def get_code(self, data):
        scheme = data.split("\r\n")[0]
        code = scheme.split()[1]
        return int(code)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')


    # Newly added methods
    def PARSE(self, url):
        parseResult = p.urlparse(url)
        host = parseResult.netloc.split(":")[0]
        port = parseResult.port
        scheme = parseResult.scheme
        path = parseResult.path
        
        # Default port if no port is stated
        if not port and scheme == "https":
            port = DEFAULT_HTTPS_PORT
        elif not port and scheme == "http":
            port = DEFAULT_HTTP_PORT

        # Use the right path if no path is stated
        if not path or path == "":
            path = "/"

        return host, port, path
    # New method
    def sendRequest(self, reqHeader):
        # Send request header 
        self.sendall(reqHeader)
        response = self.recvall(self.socket)  # Receive the response back
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)

        print("---------response body starts here--------")
        print(body)
        print("---------response body ends here---------")

        return code, body

    def GET(self, url, args=None):
        code = 500
        body = ""
        # Get the parse results from the input url
        host, port, path = self.PARSE(url)
        # Connect client with host server
        self.connect(host, port)
        # curl -v http://www.cs.ualberta.ca to see eg
        reqHeader  = "GET {} HTTP/1.1\r\nHost: {}\r\n".format(path, host)
        reqHeader += "Accept: */*\r\nConnection: close\r\n\r\n"
        code, body = self.sendRequest(reqHeader)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
         # Get the parse results from the input url
        host, port, path = self.PARSE(url)
        # Connect client with host server
        self.connect(host, port)

        if args:
            payload = p.urlencode(args)
        else:
            payload = p.urlencode("")
        
        #Request header
        reqHeader = "POST {} HTTP/1.1\r\nHost: {}\r\n".format(path, host)
        reqHeader += "Content-Length: {}\r\n".format(len(payload))
        reqHeader += "Content-Type: application/x-www-form-urlencoded\r\n"
        reqHeader += "Accept: */*\r\nConnection: close\r\n\r\n"
        if args:
            reqHeader += payload

        code, body = self.sendRequest(reqHeader)
    
        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
