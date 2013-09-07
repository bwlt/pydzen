#!/usr/bin/env python2
#
# depends on: dzen2, sensors, mpc
#
# todo
# 	click destro su dzen uccide
# 	mpd applet: renderlo piu performante senza pollare ogni secondo
# 	            same as per uptime applet

import subprocess, shlex, time, sys

class uptime_applet:
	def show(self):
		ret = subprocess.check_output("uptime")
		# TODO bug if uptime returns
		# 11:58:50 up 49 min,  2 users,  load average: 0,62, 0,55, 0,49
		return "uptime " + ret.split()[2][:-1]

class sensor_applet:
	def show(self):
		sensors = subprocess.Popen("sensors", stdout=subprocess.PIPE)
		ret = subprocess.check_output(shlex.split("grep temp1"), stdin=sensors.stdout)
		sensors.wait()
		return "temp " + ret.split()[1]

class mpd_applet:	# TODO buggy
	def __init__(self, length = 30):
		self.length = length
		self.curr = ""
		self.shiftL = False
		self.paused = False
		self.pauseMsg      = "[paused]"
		self.notPlayingMsg = "[not playing]"
	def show(self):
		retStr = ""
		ret = subprocess.check_output(shlex.split("mpc"))
		isNotPlaying = lambda : len(ret.split('\n')) == 2
		isPaused     = lambda : ret.split('\n')[1].split()[0] == "[paused]"
		getSongInfo  = lambda : ret.split('\n')[0]

		if isNotPlaying():
			return self.notPlayingMsg.center(self.length)

		self.paused = isPaused()
		song_info = getSongInfo()
		if len(song_info) > self.length:
			# shift the string
			if self.curr and self.curr in song_info:
				idx = song_info.index(self.curr)
				LIdx = idx              	# Left  index
				RIdx = self.length + idx	# Right index
				if isPaused(): RIdx -= len(self.pauseMsg)

				if LIdx == 0:
					self.shiftL = False
				elif RIdx == len(song_info):
					self.shiftL = True

				if self.shiftL:
					self.curr = song_info[LIdx-1:RIdx-1]
				else:
					self.curr = song_info[LIdx+1:RIdx+1]
				retStr = self.curr
				if isPaused(): retStr = self.curr + self.pauseMsg
			else:
				# new track
				print "<newTrack!>"
				RIdx = self.length	# Right index
				if isPaused(): RIdx -= len(self.pauseMsg)
				self.curr = song_info[:RIdx]
				retStr = self.curr
				if isPaused(): retStr = self.curr + self.pauseMsg
		else:
			self.curr = song_info
			retStr = self.curr
		print retStr.center(self.length)
		return retStr.center(self.length)

class num_applet:
	def __init__(self):
		self.num = 0
	def show(self):
		self.num = (self.num + 1) % 10
		return str(self.num)

class bar:
	def __init__(self, stdin, sep = " | "):
		self.stdin = stdin
		self.sep = sep
		self.applets = []
		#self.applets.append(uptime_applet())
		#self.applets.append(sensor_applet())
		self.applets.append(num_applet())
		self.applets.append(mpd_applet())
	def show(self):
		showlst = []
		for applet in self.applets:
			showlst.append(applet.show())
		self.stdin.write(self.sep.join(showlst) + "\n")

if __name__ == "__main__":
	cmd = "dzen2 -u -x 0 -y 800"
	proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
	bar = bar(stdin = proc.stdin)
	while 1:
		bar.show()
		time.sleep(1)
