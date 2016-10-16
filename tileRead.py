#!/bin/python

from subprocess import run, PIPE
import PIL.Image
import time
import imagehash

startingTime = time.time()
from keyConstants import *



def grabBrowserAbsolutePosition(browserName="mozilla"):
    C = ["xdotool", "search", "--name", browserName]
    ID = run(C, stdout=PIPE).stdout.decode("utf-8")
    C = ["xwininfo", "-id", ID]
    rawINFO = run(C, stdout=PIPE).stdout.decode("utf-8")

    INFO = {'absoluteX': 'Absolute upper-left X:', 'absoluteY': 'Absolute upper-left Y:',
            'relativeX': 'Relative upper-left X:', 'relativeY': 'Relative upper-left Y:'}
    
    for line in rawINFO.split('\n'):
        for K in INFO.keys():
            if type(INFO[K]) == int:
                continue
            if INFO[K] in line:
                INFO[K] = int(line.split(':')[1])

    for K in INFO.keys():
        assert(type(INFO[K]) == int)

    X = INFO['absoluteX'] - INFO['relativeX']
    Y = INFO['absoluteY'] - INFO['absoluteY']
        
    COORD = [X, Y]

    return COORD


def takeScreenshot():
    callshutter = ['shutter', '--window=.*firefox.*',
                   '-e', '-n', '--disable_systray',
                   '-o', PathToPresentBoardScreenshot ]
    run(callshutter, stdout=PIPE,stderr=PIPE)

def createBlackPointPieceMap(iBPPM):
    PieceValueMap = {
                     iBPPM[0]: 'r',
                     iBPPM[1]: 'n',
                     iBPPM[2]: 'b',
                     iBPPM[3]: 'q',
                     iBPPM[4]: 'k',
                     iBPPM[5]: 'b',
                     iBPPM[6]: 'n',
                     iBPPM[7]: 'r',
                     iBPPM[8]: 'p',
                     iBPPM[9]: 'p',
                     #
                     iBPPM[32]: 'x',
                     iBPPM[33]: 'x',
                     #
                     iBPPM[48]: 'P',
                     iBPPM[49]: 'P',
                     iBPPM[56]: 'R',
                     iBPPM[57]: 'N',
                     iBPPM[58]: 'B',
                     iBPPM[59]: 'Q',
                     iBPPM[60]: 'K',
                     iBPPM[61]: 'B',
                     iBPPM[62]: 'N',
                     iBPPM[63]: 'R'
                     }
    #print(PieceValueMap)
    return PieceValueMap
    
    

def fullScreenToBoard(screenpath):

    IMG = PIL.Image.open(screenpath)
    IMG = IMG.crop(BoardDelimitationBox)

    return IMG

def showMountedBoard(MountedBoardArray):
    j=0
    print("")
    for i in range(8):
        for j in range(8):
            print(MountedBoardArray[i*8+j], end=" ")
        print("")
    print("")
def EvaluateSquare(IMG):
    score = imagehash.dhash(IMG)
    return score

def EvaluateColoredBoard(IMG):
    score = imagehash.dhash(IMG)
    return score

def GameStillRunning(IMG):
    pass
    

def ProcessImage(IMG):
    WHITE = (255,255,255,255)
    pixels = IMG.load()
    for i in range(IMG.size[0]):
        for j in range(IMG.size[1]):
            if sum(pixels[i,j]) > BlackThreshold:
                pixels[i,j] = WHITE 
            else:
                if i+3 > IMG.size[0] or i-3 < 0:
                    pixels[i,j] = WHITE
                if j+3 > IMG.size[1] or j-3 < 0:
                    pixels[i,j] = WHITE

    return IMG

def GenerateSquareImages(BoardImage):
    BoardSquares = SliceBoard(BoardImage)
    
    IDX=0
    for S in BoardSquares:

        BoardSquares[IDX] = ProcessImage(S)
        BoardSquares[IDX].save("SquareImages/%i.png" % IDX)
        IDX+=1
    return BoardSquares


def SliceBoard(BOARD):
    bWidth, bHeight = BOARD.size

    xDotDistance = bWidth/8
    yDotDistance = bHeight/8

    Squares = []
    for i in range(8):
        for j in range(8):
            J = j * xDotDistance
            I = i * yDotDistance
            box = (J, I, J+xDotDistance, I+yDotDistance)
            p = BOARD.crop(box)
            Squares.append(p)

    return Squares

def MakeReferenceMap(BoardSquares):
    
    iBPPM = []
    for S in range(len(BoardSquares)):
        c = EvaluateSquare(BoardSquares[S])
        iBPPM.append(c)

    return iBPPM

def AnalyzeBoard(BoardImage, PieceValueMap):
    
    BoardSquares = SliceBoard(BoardImage)

    MountedBoard = [ 'x' for i in range(64) ]
    MapKeys = PieceValueMap.keys()
    for S in range(len(BoardSquares)):
        BoardSquares[S] = ProcessImage(BoardSquares[S])
        Value = EvaluateSquare(BoardSquares[S])
        #print(Value)
        k = min(MapKeys, key=lambda x:abs(x-Value))
        MountedBoard[S] = PieceValueMap[k]

    return MountedBoard
                
def setupTileReadingValues(BoardDelimitationBox):
    R = fullScreenToBoard(PathToReferenceScreenshot)

    squarelist = GenerateSquareImages(R)
    iBPPM = MakeReferenceMap(squarelist)
    PieceValueMap = createBlackPointPieceMap(iBPPM)

    return PieceValueMap

def detectBoardBox():
    IMG = PIL.Image.open(PathToReferenceScreenshot)
    pixels = IMG.load()
    first = [0,0]
    last = [0,0]
    for i in range(IMG.size[0]):
        for j in range(IMG.size[1]):

            if pixels[i,j] == WhiteSquareColor:
                if not first[0]:
                    first[0] = i
                if not first[1]:
                    first[1] = j

                last[0] = max(last[0], i)
                last[1] = max(last[1], j)


    return [ first[0], first[1], last[0], last[1] ] 

BoardDelimitationBox = detectBoardBox()

#print('done. %i ' % (time.time() - startingTime))
