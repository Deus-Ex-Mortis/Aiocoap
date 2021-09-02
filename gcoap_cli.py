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

if len(sys.argv) < 3:
    print("Please provide the IP address and the tap interface which you want to connect to.")
    sys.exit(0)

ip_coap = sys.argv[1]+"%"+sys.argv[2]

async def main():

    with open('seq.txt', 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
        f.close()
    seq_vecchia = int(last_line)
    seq_nuova = seq_vecchia+1

    if seq_vecchia == 0 or seq_vecchia % 100 == 0:
        print("Richiesta Input-Output Per Autenticazione...\n")
        url = "http://127.0.0.1:8081"
        data = str(seq_vecchia)
        x = requests.post(url, data)
        inputs = []
        output_xres = []
        output_autn = []
        f = open('gateway.txt', 'w')
        f.write("")
        f.close()
        f = open('gateway.txt', 'a')
        for j in range(0, 100):
            inputs.append(str(x.json()).split(',')[j].split("'")[1])
            output_xres.append(str(x.json()).split(',')[j].split("'")[3].split('#')[0])
            output_autn.append(str(x.json()).split(',')[j].split("'")[3].split('#')[1])
            # print(inputs[0] + ":" + output_xres[0] + ":" + output_autn[0])
            f.write(inputs[j] + ":" + output_xres[j] + ":" + output_autn[j] + "\n")
        f.close()

    f = open('gateway.txt', 'r')
    lista = []
    for x in f:
        lista.append(x)

    rand = lista[seq_vecchia % 100].split(':')[0]
    xres = lista[seq_vecchia % 100].split(':')[1]
    autn = lista[seq_vecchia % 100].split(':')[2]
    f.close()

    f = open('seq.txt', 'a')
    f.write('\n' + str(seq_nuova))
    f.close()

    riscontro = []
    print("\nInvio Input...\n")
    print("Ricezione hmac...\n")

    protocol = await Context.create_client_context()

    url = "coap://[" + ip_coap + "]/auth"
    payload = str(rand) + "#" + str(seq_vecchia) + "#" + str(autn)
    # print(payload)
    responses = [
        protocol.request(Message(code=GET, uri=url, payload=bytes(payload, encoding='utf-8'))).response
    ]
    for f in asyncio.as_completed(responses):
        response = await f
        riscontro.append(response.payload.decode())
    print(riscontro[0].lower())
    print(xres)
    print("Confronto HMAC...")

    corta = riscontro[0].lower()
    lunga = str(xres)
    j = 0
    counter = 0

    for k in range(0,64):
        if corta[j] == lunga[k]:
            counter += 1
        else:
            j -= 1
        j += 1
    print(counter)

    if counter >= 60:
        print("\nDispositivo Autenticato")

    else:
        print("\nAutenticazione Fallita")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
