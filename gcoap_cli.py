import sys
import asyncio
import argparse
import logging
import subprocess
import socket
from asyncio import *
from pathlib import Path
import numpy as np
import random
import requests

import shlex
# even though not used directly, this has side effects on the input() function
# used in interactive mode
from pickle import GET

try:
    import readline  # noqa: F401
except ImportError:
    pass  # that's normal on some platforms, and ok since it's just a usability enhancement

from aiocoap import *


# async def main():
#    protocol = await Context.create_client_context()
#    msg = Message(code=GET, uri="coap://[fe80::3c0a:c1ff:fe78:69b%tap0]/echo/ciao")
#    response = await protocol.request(msg).response
#    print(response.payload)
#run(main())



async def main():

    print("Richiesta Input-Output Per Autenticazione...\n")
    url = "http://127.0.0.1:8081"
    x = requests.get(url)
    inputs = []
    outputs = []
    counter = 0
    for j in range(0,100):
        inputs.append(str(x.json()).split(',')[j].split("'")[1])
        outputs.append(str(x.json()).split(',')[j].split("'")[3])
        #print(inputs[j] + ":" + outputs[j])
    riscontro = []
    number_list = random.sample(range(0,100), 10)
    print("Invio Input...\n")
    print("Ricezione hmac...\n")

    protocol = await Context.create_client_context()
    for k in range(0, 10):
        url = "coap://[fe80::fcb7:95ff:fe21:a414%riot0]/auth"
        payload = str(inputs[number_list[k]])
        #print(payload)
        responses = [
            protocol.request(Message(code=GET, uri=url, payload=bytes(payload, encoding='utf-8'))).response
        ]
        for f in asyncio.as_completed(responses):
            response = await f
            riscontro.append(response.payload.decode())
    for g in range(0,10):
        if outputs[number_list[g]].upper() == str(riscontro[g]):
            print("confronto numero " + str(g+1) + ": ... OK")
            counter +=1
            if counter == 10:
                print("\nDispositivo Autenticato")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
