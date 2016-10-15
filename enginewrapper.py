#!/bin/python
from subprocess import Popen, PIPE, call

from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, system


class Engine():

    def __init__(self, Arguments):
        try:
            self.engine = Popen(Arguments, stdin=PIPE, stdout=PIPE)
        except FileNotFoundError:
            print("Engine not Found.")
            return

        flags = fcntl(self.engine.stdout, F_GETFL)
        fcntl(self.engine.stdout, F_SETFL, flags | O_NONBLOCK)

        self.recordComm = 0

        self.recordedData=""

    def send(self, data):
        self.engine.stdin.write(bytearray("%s\n" % data, "utf-8"))
        self.engine.stdin.flush()

    def receive(self, method="lines"):

        if method == "lines":
            self.engine.stdout.flush()
            data = self.engine.stdout.readlines()
            data = [x.decode('utf-8', 'ignore') for x in data]
            if self.recordComm:
                for c in data:
                    self.recordedData += c
        else:
            self.engine.stdout.flush()
            data = self.engine.stdout.read().decode('utf-8', 'ignore')
            if self.recordComm:
                self.recordedData +=data

        return data

    def readMove(self, data=None, moveKeyword="move", Verbose=False):
        if not data:
            data = self.receive()

        for line in data:
            if Verbose:
                print(">%s" % line)
            if moveKeyword in line and not line.startswith("param"):
                line = line.replace('\n', '').strip().split(" ")
                return line[-1]
    
        return None

    def pid(self):
        return self.engine.pid

    def dumpRecordedData(self):
        if self.recordedData:
            File = open("log/%i.dump" % self.pid(),'w')
            File.write(self.recordedData)
            File.close()
    def __del__(self):
        try:
            self.destroy()
        except:
            pass
    def destroy(self):
        try:
            call(['kill', '-9', str(self.engine.pid)])
        except AttributeError:
            pass

