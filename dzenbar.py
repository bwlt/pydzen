#!/usr/bin/env python
#
# depends on: dzen2, sensors, mpc
#
# todo
#   click destro su dzen uccide
#   mpd applet: renderlo piu performante senza pollare ogni secondo
#               same as per uptime applet

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

class mpd_applet:
    def __init__(self, length = 30):
        self.length = length
        self.curr = ""
        self.shiftL = False
        self.pauseMsg      = "[paused]"
        self.notPlayingMsg = "[not playing]"
    def show(self):
        retStr = ""
        ret = subprocess.check_output(shlex.split("mpc"))

        # check if not playing
        if len(ret.split('\n')) == 2:
            return self.notPlayingMsg.center(self.length)

        isPaused = ret.split('\n')[1].split()[0] == "[paused]"
        songInfo = ret.split('\n')[0]

        # find proper index
        LIdx = 0
        if self.curr in songInfo:
            LIdx = songInfo.index(self.curr)
        RIdx = self.length + LIdx
        if isPaused:
            RIdx -= len(self.pauseMsg)

        # shift when:
        #   - song info length is greater than applet length
        #   - song info length plus pause message length is greater than applet length
        #   - new song
        if len(songInfo) > self.length or \
           (isPaused and ((len(songInfo) + len(self.pauseMsg)) > self.length)) or \
           LIdx != 0:
            # need shift
            if LIdx == 0:
                self.shiftL = False
            elif RIdx >= len(songInfo):
                self.shiftL = True

            if self.shiftL:
                self.curr = songInfo[LIdx-1:RIdx-1]
            else:
                self.curr = songInfo[LIdx+1:RIdx+1]
            retStr = self.curr
            if isPaused: retStr = self.curr + self.pauseMsg
        else:
            # no need to shift
            self.curr = songInfo[LIdx:RIdx]
            retStr = self.curr
            if isPaused: retStr += self.pauseMsg

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
        self.applets.append(uptime_applet())
        #self.applets.append(sensor_applet())
        #self.applets.append(mpd_applet())
        #self.applets.append(num_applet())
    def show(self):
        showlst = []
        for applet in self.applets:
            showlst.append(applet.show())
        self.stdin.write(self.sep.join(showlst) + "\n")

if __name__ == "__main__":
    cmd = "dzen2 -u -x 0 -y 800"
    proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
    bar = bar(stdin = proc.stdin)
    while True:
        bar.show()
        time.sleep(1)
