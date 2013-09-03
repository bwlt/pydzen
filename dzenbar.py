#!/usr/bin/env python2
#
# depends on: dzen2, sensors, mpc

import subprocess, shlex, time, sys

def print_sep():
	print "|",

def print_uptime():
	ret = subprocess.check_output("uptime")
	print "uptime", ret.split()[2][:-1],

def print_cpu_temp():
	sensors = subprocess.Popen("sensors", stdout=subprocess.PIPE)
	ret = subprocess.check_output(shlex.split("grep temp1"), stdin=sensors.stdout)
	sensors.wait()
	print "temp", ret.split()[1],

def print_song_info():
	ret = subprocess.check_output(shlex.split("mpc"))
	if len(ret.split('\n')) == 2:
		print "[not playing]",
		return
	print ret.split('\n')[0],
	if ret.split('\n')[1].split()[0] == "[paused]":
		print "[paused]",

def print_statusbar():
	print_uptime()
	print_sep()
	print_cpu_temp()
	print_sep()
	print_song_info()
	print

if __name__ == "__main__":
	cmd = "dzen2 -u -x 0 -y 800 -l 1"
	proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
	sys.stdout = proc.stdin
	while 1:
		print_statusbar()
		time.sleep(1)
