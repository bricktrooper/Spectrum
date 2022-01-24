#! /usr/local/bin/python3

from sys import argv
from math import pi as PI

def usage():
	print("cutoff <R> <C>")

if len(argv) != 3:
	usage()
	exit(-1)

r = float(argv[1])
c = float(argv[2])

f = 1 / (2 * PI * r * c)
print(f"R: {r} R, C: {c} F, f: {f} Hz")
