import sys
import fileinput

with fileinput.input() as lines:
    for line in lines:
        print(line)
