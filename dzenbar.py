#!/usr/bin/env python2
#
# depends on: dzen2, sensors, mpc
#
# todo
# 	click destro su dzen uccide

import subprocess, shlex, time, sys

class uptime_applet:
	def show(self):
		ret = subprocess.check_output("uptime")
		# TODO bug if uptime returns
		# 11:58:50 up 49 min,  2 users,  load average: 0,62, 0,55, 0,49
		print "uptime", ret.split()[2][:-1],

class sensor_applet:
	def show(self):
		sensors = subprocess.Popen("sensors", stdout=subprocess.PIPE)
		ret = subprocess.check_output(shlex.split("grep temp1"), stdin=sensors.stdout)
		sensors.wait()
		print "temp", ret.split()[1],

class mpd_applet:
	def show(self):
		ret = subprocess.check_output(shlex.split("mpc"))
		if len(ret.split('\n')) == 2:
			print "[not playing]",
			return
		curr_song = ret.split('\n')[0]
		print curr_song,
		if ret.split('\n')[1].split()[0] == "[paused]":
			print "[paused]",

class bar:
	def __init__(self):
		self.uptime = uptime_applet()
		self.cpu_temp = sensor_applet()
		self.song = mpd_applet()
	def print_sep(self):
		print "|",
	def show(self):
		self.uptime.show()
		self.print_sep()
		self.cpu_temp.show()
		self.print_sep()
		self.song.show()
		print

if __name__ == "__main__":
	cmd = "dzen2 -u -x 0 -y 800 -l 1"
	proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
	sys.stdout = proc.stdin
	bar = bar()
	while 1:
		# print_statusbar()
		bar.show()
		time.sleep(1)
