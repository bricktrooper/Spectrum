#! /usr/local/bin/python3

# Picks the most accurate C, R1, R2, and R3 values
# for a multiple feedback active bandpass filter.

import math

from sys import argv

def usage():
	print("bandpass <f> <Q> <A> <C multiplier>")
	print("Centre frequency (f) is in Hz")
	print("C multiplier must be a multiple of 10")

MIN_ARGC = 5
MAX_ARGC = 5

argc = len(argv)
if argc < MIN_ARGC or argc > MAX_ARGC:
	usage()
	exit(-1)

# R1, R2, and C determine A, Q, and f.
# R3 can be calculated using A, Q, and f.
# Changing R3 shifts f but does not affect Q and A

def parallel(a, b):
	return 1 / ((1 / a) + (1 / b))

def R1(f, c, q, a):
	return q / (2 * math.pi * f * c * a)

def R2(f, c, q):
	return q / (math.pi * f * c)

def R3(f, c, q, a):
	return q / (2 * math.pi * f * c * (2 * (q ** 2) - a))

def F(r1, r2, r3, c):
	return 1 / (2 * math.pi * c * math.sqrt(parallel(r1, r3) * r2))

def Q(r1, r2, r3):
	return (1 / 2) * math.sqrt(r2 / parallel(r1, r3))

def A(r1, r2):
	return r2 / (2 * r1)   # abs(a)

# Resistor values will be in kohms
# Capacitor values will be in pF
# the standard values are available in decade multiples

# 5 % tolerance resistors and 10 % tolerance capacitors
STANDARD_BASES = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]

def decades(base):
	values = []
	# sweep from 1 to 1M
	for i in range(7):
		multiplier = 10 ** i
		values.append(base * multiplier)
	return values

STANDARD_RESISTORS = []
for base in STANDARD_BASES:
	STANDARD_RESISTORS += decades(base)

# choose a C value
# calcualte the exact R1, R2, and R3 values
# find the closest resistor values for R1, R2, R3
# recalcualte f, Q, and A with the realistic resistor values and find the error

PICO = 1e-12

def pF(c):
	return c * 1e12

def kohm(r):
	return r / 1e3

def deviation(actual, expected):
	return abs(actual - expected)

def error(actual, expected):
	return (abs(actual - expected) / expected) * 100

def pick_resistor(exact):
	closest = STANDARD_RESISTORS[0]   # assume that the first value is the best
	for r in STANDARD_RESISTORS:
		if abs(exact - r) < abs(exact - closest):
			closest = r
	return closest

def calculate_resistors(f, c, q, a):
	r1 = R1(f, c, q, a)
	r2 = R2(f, c, q)
	r3 = R3(f, c, q, a)
	return r1, r2, r3

exact_f = float(argv[1])   # centre frequency (Hz)
exact_q = float(argv[2])   # quality factor
exact_a = float(argv[3])   # max gain at 'f' (actually -a due to inverting nature).  Must be less than 2Q^2

c_multiplier = float(argv[4])

# sweep all capacitor values in pF

CONFIGURATIONS = []
for value in STANDARD_BASES:
	c = value * PICO * c_multiplier

	exact_r1, exact_r2, exact_r3 = calculate_resistors(exact_f, c, exact_q, exact_a)

	real_r1 = pick_resistor(exact_r1)
	real_r2 = pick_resistor(exact_r2)
	real_r3 = pick_resistor(exact_r3)

	real_f = F(real_r1, real_r2, real_r3, c)
	real_q = Q(real_r1, real_r2, real_r3)
	real_a = A(real_r1, real_r2)

	r2_deviation = deviation(real_r2, exact_r2)
	r1_deviation = deviation(real_r1, exact_r1)
	r3_deviation = deviation(real_r3, exact_r3)
	f_deviation = deviation(real_f, exact_f)
	q_deviation = deviation(real_q, exact_q)
	a_deviation = deviation(real_a, exact_a)

	r2_error = error(real_r2, exact_r2)
	r1_error = error(real_r1, exact_r1)
	r3_error = error(real_r3, exact_r3)
	f_error = error(real_f, exact_f)
	q_error = error(real_q, exact_q)
	a_error = error(real_a, exact_a)

	print("[C] %g pF" % (pF(c)))
	print("[R1] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r1, real_r1, r1_deviation, r1_error))
	print("[R2] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r2, real_r2, r2_deviation, r2_error))
	print("[R3] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r3, real_r3, r3_deviation, r3_error))
	print("[F] exact: %g Hz, real: %g Hz, error: %g (%g %%)" % (exact_f, real_f, f_deviation, f_error))
	print("[Q] exact: %g, real: %g, error: %g (%g %%)" % (exact_q, real_q, q_deviation, q_error))
	print("[A] exact: %g V/V, real: %g V/V, error: %g (%g %%)" % (exact_a, real_a, a_deviation, a_error))

	average_error = (f_error + q_error + a_error) / 3
	print("Average error: %g %%" % (average_error))

	CONFIGURATIONS.append(
		{
			"error": "%.3f" % (average_error),
			"C":     "%g pF" % (pF(c)),
			"R1":    "%g R" % (real_r1),
			"R2":    "%g R" % (real_r2),
			"R3":    "%g R" % (real_r3),
			"f":     "%.3f Hz" % (real_f),
			"Q":     "%.3f" % (real_q),
			"A":     "%.3f V/V" % (real_a),
		}
	)

CONFIGURATIONS = sorted(CONFIGURATIONS, key = lambda f: f["error"])

for configuration in CONFIGURATIONS:
	print(configuration)
# decreasing C by a factor of 10 increases R1, R2, and R3 by a factor of 10
# the error stays the same!

print("Q")
print(Q(11e3, 91e3, 27e3))
print(Q(2.7e3, 22e3, 6.3e3))
print(Q(1.5e3, 11e3, 3.3e3))
print(Q(7.5e3, 63e3, 18e3))
print(Q(2e3, 15e3, 43e3))

print("F")
print(F(11e3, 91e3, 27e3, 0.1e-6))
print(F(2.7e3, 22e3, 6.3e3, 0.1e-6))
print(F(1.5e3, 11e3, 3.3e3, 0.047e-6))
print(F(7.5e3, 63e3, 18e3, 0.0022e-6))
print(F(2e3, 15e3, 43e3, 0.0022e-6))
