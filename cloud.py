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


async def main():
    print("Richiesta Chiave...\n")
    protocol = await Context.create_client_context()
    url = "coap://[fe80::fcb7:95ff:fe21:a414%riot0]/key"
    responses = [
        protocol.request(Message(code=GET, uri=url)).response
    ]
    for f in asyncio.as_completed(responses):
        response = await f
        key = response.payload

    number_list = random.sample(range(0, 100000), 100)
    output = []
    print("Generazione Input Casuali...\n")
    print("Generazione hmac...\n")
    for i in range(0,100):
        number = str(number_list[i])
        h = hmac.new(bytes(key), number.encode(), hashlib.sha256)
        output.append(h.hexdigest())
        #print(output[0])

    class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            for j in range(0,100):
                if j == 0:
                    message = '{"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                if j != 0 and j < 99:
                    message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '", '
                if j == 99:
                    message = '"' + str(number_list[j]) + '": "' + str(output[j]) + '"}'
                self.wfile.write(bytes(message, "utf8"))
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
