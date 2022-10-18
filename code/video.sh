#!/bin/bash
while [ 1 -eq 1 ]; do raspivid -t 0 -h 600 -w 600 -o - -fps 20 -b 5000000 | nc -l 1234; done
