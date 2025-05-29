#!/usr/bin/bash
# script para arrancar el servidor ocsp con openssl

openssl ocsp \
    -port 2560 \
    -index /home/dgarcia/diegoCA/index.txt \
    -CA /home/dgarcia/diegoCA/certs/ca.crt \
    -rkey /home/dgarcia/diegoCA/private/ocsp.key \
    -rsigner /home/dgarcia/diegoCA/certs/ocsp.crt \
    -text \
    >> /home/dgarcia/diegoCA/logs/ocsp.log 2>&1

#Es el mismo comando, solo que manda la salida al log
