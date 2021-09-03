import sys
import asyncio
import argparse
import logging
import subprocess
import socket
import hmac
import hashlib
import base64
from asyncio import *
from pathlib import Path
from http.server import *

import numpy as np
import random

import shlex
# even though not used directly, this has side effects on the input() function
# used in interactive mode
from pickle import GET

try:
    import readline  # noqa: F401
except ImportError:
    pass  # that's normal on some platforms, and ok since it's just a usability enhancement

from aiocoap import *

if len(sys.argv) < 3:
    print("Please provide the IP address and the tap interface which you want to connect to.")
    sys.exit(0)

ip_coap = sys.argv[1]+"%"+sys.argv[2]

if len(sys.argv) > 3 and sys.argv[3] == "puf":
    puf = True
else:
    puf = False

async def main():

    print(len(sys.argv))

    if puf:
        print("Richiesta Chiave...\n")
        protocol = await Context.create_client_context()
        url = "coap://[" + ip_coap + "]/key"
        responses = [
            protocol.request(Message(code=GET, uri=url)).response
        ]
        for f in asyncio.as_completed(responses):
            response = await f
            key = response.payload
    else:
        key = "cfb8cdb1526a8c4f3372501b83dadb27"

    class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data_int = int(post_data)
            with open('provider.txt', 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1]
                f.close()
            seq_vecchia = int(last_line)
            if post_data_int == 0 and seq_vecchia == 0:
                # print("IF 1")
                lines.append(post_data_int)
                f = open('provider.txt', 'a')
                f.write("\n" + str(post_data_int + 100))
                f.close()

                number_list = random.sample(range(0, 100000), 100)
                output = []
                print("Generazione Input Casuali...\n")
                print("Generazione hmac...\n")
                for i in range(0, 100):
                    mid = post_data_int + i
                    number = str(number_list[i]) + str(mid) + "XRES"
                    if puf:
                        h = hmac.new(bytes(key), number.encode(), hashlib.sha256)
                    else:
                        h = hmac.new(bytes(key,encoding= "utf-8"), number.encode(), hashlib.sha256)
                    output.append(h.hexdigest())

                for i in range(0, 100):
                    mid = post_data_int + i
                    number = str(number_list[i]) + str(mid) + "AUTN"
                    if puf:
                        h = hmac.new(bytes(key), number.encode(), hashlib.sha256)
                    else:
                        h = hmac.new(bytes(key,encoding= "utf-8"), number.encode(), hashlib.sha256)
                    output[i] = output[i] + "#" + h.hexdigest()

                for j in range(0, 100):
                    if j == 0:
                        message = '{"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                    if j != 0 and j < 99:
                        message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                    if j == 99:
                        message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '"}'
                    self.wfile.write(bytes(message, "utf8"))

            elif post_data_int == seq_vecchia:
                # print("IF 2")
                lines.append(post_data_int)
                f = open('provider.txt', 'a')
                f.write("\n" + str(post_data_int + 100))
                f.close()

                number_list = random.sample(range(0, 100000), 100)
                output = []
                print("Generazione Input Casuali...\n")
                print("Generazione hmac...\n")
                for i in range(0, 100):
                    number = str(number_list[i]) + post_data + "XRES"
                    if puf:
                        h = hmac.new(bytes(key), number.encode(), hashlib.sha256)
                    else:
                        h = hmac.new(bytes(key,encoding= "utf-8"), number.encode(), hashlib.sha256)
                    output.append(h.hexdigest())

                for i in range(0, 100):
                    number = post_data + str(number_list[i]) + "AUTN"
                    if puf:
                        h = hmac.new(bytes(key), number.encode(), hashlib.sha256)
                    else:
                        h = hmac.new(bytes(key,encoding= "utf-8"), number.encode(), hashlib.sha256)
                    output[i] = output[i] + "#" + h.hexdigest()

                for j in range(0, 100):
                    if j == 0:
                        message = '{"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                    if j != 0 and j < 99:
                        message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                    if j == 99:
                        message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '"}'
                    self.wfile.write(bytes(message, "utf8"))

            else:
                print("Numero sequenza anomalo, token ancora disponibili")

            return

    def run():
        print('Avvio del server...\n')
        server_address = ('127.0.0.1', 8081)
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('Server in esecuzione...\n')
        print("Attesa...\n")
        httpd.serve_forever()

    run()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
