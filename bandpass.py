#! /usr/local/bin/python3

# Finds the most accurate C, R1, R2, and R3 values
# for a multiple feedback active bandpass filter.

from sys import argv
from math import sqrt, pi as PI

ERROR = -1

# ======= SI UNITS ======= #

PICO = 1e-12
NANO = 1e-9
MICRO = 1e-6
MILLI = 1e-3
KILO = 1e3
MEGA = 1e6
GIGA = 1e9

def pico(x):
	return x * (1 / PICO)

def nano(x):
	return x * (1 / NANO)

def micro(x):
	return x * (1 / MICRO)

def milli(x):
	return x * (1 / MILLI)

def base(x):
	return x

def kilo(x):
	return x * (1 / KILO)

def mega(x):
	return x * (1 / MEGA)

def giga(x):
	return x * (1 / GIGA)

R_UNITS = ["R", "K", "M"]
C_UNITS = ["pF", "nF", "uF", "mF", "F"]
F_UNITS = ["Hz", "kHz", "MHz", "GHz"]

R_CONVERT = {
	"R": base,
	"K": kilo,
	"M": mega
}

C_CONVERT = {
	"pF": pico,
	"nF": nano,
	"uF": micro,
	"mF": milli,
	"F":  base
}

F_CONVERT = {
	"Hz": base,
	"kHz": kilo,
	"MHz": mega,
	"GHz": giga
}

def r_convert(r, unit):
	if unit not in R_CONVERT:
		print(f"Cannot convert invalid R unit '{unit}'")
		exit(ERROR)
	return R_CONVERT[unit](r)

def c_convert(c, unit):
	if unit not in C_CONVERT:
		print(f"Cannot convert invalid C unit '{unit}'")
		exit(ERROR)
	return C_CONVERT[unit](c)

def f_convert(f, unit):
	if unit not in F_CONVERT:
		print(f"Cannot convert invalid f unit '{unit}'")
		exit(ERROR)
	return F_CONVERT[unit](f)

def parallel(a, b):
	return 1 / ((1 / a) + (1 / b))

# ======= MULTIPLE FEEDBACK BPF ======= #

# R1, R2, and C determine A, Q, and f.
# Changing R3 shifts f but does not affect Q and A.

def R1(f, c, q, a):
	return q / (2 * PI * f * c * a)

def R2(f, c, q):
	return q / (PI * f * c)

def R3(f, c, q, a):
	return q / (2 * PI * f * c * (2 * (q ** 2) - a))

def F(r1, r2, r3, c):
	return 1 / (2 * PI * c * sqrt(parallel(r1, r3) * r2))

def Q(r1, r2, r3):
	return (1 / 2) * sqrt(r2 / parallel(r1, r3))

def A(r1, r2):
	# abs(A) since A is actually negative due to inverting nature of the BPF.
	return r2 / (2 * r1)   # must be less than 2Q^2

# ======= STANDARD R AND C VALUES ======= #

# The standard values are available in decade multiples.

# Standard base multiples for 5 % tolerance resistors
STANDARD_RESISTOR_BASES = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]

# Standard base multiples for 10 % tolerance capacitors
STANDARD_CAPACITOR_BASES = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]

def decades(base):
	values = []
	# sweep from 1 to 1M
	for i in range(7):
		values.append(base * (10 ** i))
	return values

# Generate standard resistor values
STANDARD_RESISTORS = []
for base in STANDARD_RESISTOR_BASES:
	STANDARD_RESISTORS += decades(base)

# 1. Choose a C value from the standard values (after applying c_multiplier).
# 2. Calcualte the exact R1, R2, and R3 values given the chosen C value.
# 3. Find the closest standard resistor values for R1, R2, R3.
# 4. recalcualte f, Q, and A with the standard resistor values to determine the error.

def pick_resistor(exact):
	closest = STANDARD_RESISTORS[0]   # assume that the first value is the best
	for r in STANDARD_RESISTORS:
		if abs(exact - r) < abs(exact - closest):
			closest = r
	return closest

# ================================================= #

def deviation(actual, expected):
	return abs(actual - expected)

def error(actual, expected):
	return (abs(actual - expected) / expected) * 100

def calculate_resistors(f, c, q, a):
	r1 = R1(f, c, q, a)
	r2 = R2(f, c, q)
	r3 = R3(f, c, q, a)
	return r1, r2, r3

def usage():
	print("-----------------------------------------------------")
	print("bandpass <f> <Q> <A> <C unit> <R unit> <C multiplier>")
	print("-----------------------------------------------------")
	print("f            : Centre frequency in Hz")
	print("Q            : quality factor")
	print("A            : abs(max gain) at f")
	print("C unit       : pF, nF, uF, mF, F, kF, MF")
	print("R unit       : pR, nR, uR, mR, R, kR, MR")
	print("C multiplier : scaling factor for C")
	print("-----------------------------------------------------")

MIN_ARGC = 7
MAX_ARGC = 7

argc = len(argv)
if argc < MIN_ARGC or argc > MAX_ARGC:
	usage()
	exit(ERROR)

exact_f = float(argv[1])        # centre frequency (Hz)
exact_q = float(argv[2])        # quality factor
exact_a = float(argv[3])        # max gain at f
c_unit = str(argv[4])           # SI unit for R
r_unit = str(argv[5])           # SI unit for C
c_multiplier = float(argv[6])   # scaling factor for C (inversely proportional to R and does not affect f, C, Q, error, etc.)

if c_unit not in C_UNITS:
	print(f"No such C unit '{c_unit}'")
	print(f"Must be one of {C_UNITS}")
	exit(ERROR)

if r_unit not in R_UNITS:
	print(f"No such R unit '{r_unit}'")
	print(f"Must be one of {R_UNITS}")
	exit(ERROR)

# Sweep all capacitor values and R and C combinations
CONFIGURATIONS = []
for value in STANDARD_CAPACITOR_BASES:
	exact_c = value * PICO * c_multiplier   # standard values are in pF for capacitors so convert to F
	exact_r1, exact_r2, exact_r3 = calculate_resistors(exact_f, exact_c, exact_q, exact_a)

	real_r1 = pick_resistor(exact_r1)
	real_r2 = pick_resistor(exact_r2)
	real_r3 = pick_resistor(exact_r3)
	real_f = F(real_r1, real_r2, real_r3, exact_c)
	real_q = Q(real_r1, real_r2, real_r3)
	real_a = A(real_r1, real_r2)

	r1_deviation = deviation(real_r1, exact_r1)
	r2_deviation = deviation(real_r2, exact_r2)
	r3_deviation = deviation(real_r3, exact_r3)
	f_deviation = deviation(real_f, exact_f)
	q_deviation = deviation(real_q, exact_q)
	a_deviation = deviation(real_a, exact_a)

	r1_error = error(real_r1, exact_r1)
	r2_error = error(real_r2, exact_r2)
	r3_error = error(real_r3, exact_r3)
	f_error = error(real_f, exact_f)
	q_error = error(real_q, exact_q)
	a_error = error(real_a, exact_a)

	average_error = (f_error + q_error + a_error) / 3

	#print("[C] %g F" % (exact_c))
	#print("[R1] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r1, real_r1, r1_deviation, r1_error))
	#print("[R2] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r2, real_r2, r2_deviation, r2_error))
	#print("[R3] exact: %g R, real: %g R, error: %g (%g %%)" % (exact_r3, real_r3, r3_deviation, r3_error))
	#print("[F] exact: %g Hz, real: %g Hz, error: %g (%g %%)" % (exact_f, real_f, f_deviation, f_error))
	#print("[Q] exact: %g, real: %g, error: %g (%g %%)" % (exact_q, real_q, q_deviation, q_error))
	#print("[A] exact: %g V/V, real: %g V/V, error: %g (%g %%)" % (exact_a, real_a, a_deviation, a_error))
	#print("Average error: %g %%" % (average_error))

	if real_f >= GIGA:
		f_unit = "GHz"
	elif real_f >= MEGA:
		f_unit = "MHz"
	elif real_f >= KILO:
		f_unit = "kHz"
	else:
		f_unit = "Hz"

	CONFIGURATIONS.append(
		{
			"error": "%.3f" % (average_error),
			"C":     "%g %s" % (c_convert(exact_c, c_unit), c_unit),
			"R1":    "%g %s" % (r_convert(real_r1, r_unit), r_unit),
			"R2":    "%g %s" % (r_convert(real_r2, r_unit), r_unit),
			"R3":    "%g %s" % (r_convert(real_r3, r_unit), r_unit),
			"f":     "%.3f %s" % (f_convert(real_f, f_unit), f_unit),
			"Q":     "%.3f" % (real_q),
			"A":     "%.3f V/V" % (real_a),
		}
	)

# Sort all configurations by average error
CONFIGURATIONS = sorted(CONFIGURATIONS, key = lambda f: float(f["error"]))

print("---------------------------------------------------------------------------------------------------------")
print("| %-10s | %-10s | %-10s | %-10s | %-10s | %-10s | %-10s | %-10s |" % ("ERROR", "C", "R1", "R2", "R3", "f", "Q", "A"))
print("---------------------------------------------------------------------------------------------------------")

for configuration in CONFIGURATIONS:
	print("| %-10s | %-10s | %-10s | %-10s | %-10s | %-10s | %-10s | %-10s |" % (
			configuration["error"],
			configuration["C"],
			configuration["R1"],
			configuration["R2"],
			configuration["R3"],
			configuration["f"],
			configuration["Q"],
			configuration["A"]
		)
	)

print("---------------------------------------------------------------------------------------------------------")
