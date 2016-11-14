#!/bin/python
from subprocess import Popen, PIPE, call

from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, system, mkdir, path
import random


class Engine():

    def __init__(self, Arguments, recordCommunication=None):
        try:
            self.engine = Popen(Arguments, stdin=PIPE, stdout=PIPE)
        except FileNotFoundError:
            print("Engine not Found.")
            return

        flags = fcntl(self.engine.stdout, F_GETFL)
        fcntl(self.engine.stdout, F_SETFL, flags | O_NONBLOCK)

        if recordCommunication:
            if not path.isdir('engine_log'):
                mkdir('engine_log')
            
        self.recordCommunication = recordCommunication
        self.MachineName = None
        
    def send(self, data):
        self.engine.stdin.write(bytearray("%s\n" % data, "utf-8"))
        self.engine.stdin.flush()

        self.appendToComm("input> %s\n" % data)

    def newGame(self):
        self.send("new")
        if self.recordCommunication:
            #self.recordCommunication.close()
            filename = "engine_log/%s" % self.generateCommFileName()
            self.recordCommunication = open(filename, 'w')
            
    def appendToComm(self, data):
        try:
            if not type(self.recordCommunication) == bool:
                for c in data:
                    self.recordCommunication.write(c)
        except:
            print("Failure to log. %s     message: %s" % (self.recordCommunication, data))
        
    def generateCommFileName(self):
        return "game_%i.log" % random.randrange(66666)
    
    def receive(self, method="lines"):

        if method == "lines":
            self.engine.stdout.flush()
            data = self.engine.stdout.readlines()
            data = [x.decode('utf-8', 'ignore') for x in data]
            for line in data:
                if 'MACname' in line:
                    self.MachineName = line[-1][:-1]
                    print("%s is loaded." % self.MachineName)
        else:
            self.engine.stdout.flush()
            data = self.engine.stdout.read().decode('utf-8', 'ignore')

        self.appendToComm(data)
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
            File = open("%i.dump" % self.pid(),'w')
            File.write(self.recordedData)
            File.close()
    def __del__(self):
        try:
            self.dumpRecordedData()
            self.destroy()
        except:
            pass
    def destroy(self):
        try:
            call(['kill', '-9', str(self.engine.pid), '&'])
        except AttributeError:
            pass

